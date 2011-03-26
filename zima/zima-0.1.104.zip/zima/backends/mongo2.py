# -*- coding: utf-8 -*-
from time import time

from pymongo import Connection as mongoConnect, \
    ASCENDING as ASC, DESCENDING as DESC
from pymongo.errors import OperationFailure
from pymongo.code import Code

from zima import cron, kv
from utils import flatten
from errors import Message404Error, File404Error

class Model:
    def __init__(self, config):
        host, port = config.iface.split(':')
        self._db = mongoConnect(host, int(port))[config.dbname]
        self._cfg = config

        self._insure_indexes()

    def _insure_indexes(self):
        self._db.command('repairDatabase')
        self._db.messages.ensure_index('num')
        self._db.messages.ensure_index('pfx')
        self._db.messages.ensure_index('host')
        self._db.messages.ensure_index('ts')
        self._db.messages.ensure_index('parent')
        self._db.digest.ensure_index('bump')
        self._db.digest.ensure_index('pfx')
        self._db.digest.ensure_index('host')
        self._db.digest.ensure_index('parent')
        self._db.boardid.ensure_index('pfx')
        self._db.boardid.ensure_index('host')
        self._db.chksums.ensure_index('hash')

    def _nextid(self, host, pfx):
        """ Получение индексов для новых сообщений """
        try:
            nid = self._db.command(
                "findandmodify",
                "boardid",
                query={'pfx':pfx, 'host':host},
                update={"$inc": {"id": 1}})
        except OperationFailure:
            self._db.boardid.save({'pfx':pfx, 'host':host,'id': 2})
            return 1

        return nid['value']['id']

    def _refresh_digest(self, pred):
        def worker(did):
            if did in kv:
                del kv[did]
            thread = self.get_msgs(pred)
            def stats((mc, ac, omc, oac, bump), m):
                if 0 < mc < len(thread) - self._cfg.tailLength:
                    omc += 1
                    oac += len(m['attaches'])
                return (mc+1, ac+len(m['attaches']), omc, oac, max(bump, m['ts']))
            postsCount, attachesCount, omittedPosts,\
                omittedAttaches, bump = reduce(stats, thread, (0, 0, 0, 0, 0))
            digest = pred.copy()
            op = thread.pop(0)
            digest.update({
                'op': op,
                'bump': bump,
                'pfx': op['pfx'],
                'host': op['host'],
                'postsCount':postsCount,
                'attachesCount':attachesCount,
                'omittedPosts': omittedPosts,
                'omittedAttaches': omittedAttaches,
                'tail': thread[-self._cfg.tailLength:]
            })
            self._db.digest.update(pred, {'$set': digest}, True)

        did = 'x-digest%s%s%s' % (pred['host'], pred['pfx'], pred['parent'])
        if did in kv:
            return
        else:
            kv[did]=True
            cron.schedule(worker, did)

    def get_msgs(self, pred, limit=10000):
        return list(self._db.messages.find(pred, limit=limit).sort('ts', ASC))

    def del_msgs(self, pred):
        doomed = self._messages.find(pred, {_id:1})
        if len(doomed) > 0:
            self._messages.remove(pred)
        else:
            raise Message404Error(pred)

    def save_msg(self, message):
        message['ts'] = int(time())
        message['_id'] = message['uid']
        message['num'] = self._nextid(message['host'], message['pfx'])
        message['_id'] = ''.join([message['host'], message['pfx'], str(message['num'])])
        if 'parent' not in message:
            message['parent'] = message['num']
        message['parent'] = int(message['parent'])
        if 'attaches' not in message:
            message['attaches'] = []
        threadLen = self._db.messages.\
            find({'parent': message['parent']}).count()
        if threadLen >= self._cfg.bumpLimit:
            if 'sage' not in message:
                message['sage'] = 'auto'
        self._db.messages.save(message)
        self._refresh_digest({
            'pfx': message['pfx'],
            'host': message['host'],
            'parent': message['parent'],
        })

    def get_digests(self, pred, offset=0, limit=10000):
        return list(self._db.digest.find(pred, skip=int(offset), limit=int(limit)).sort('bump', DESC))

    def ping_msgs(self, messages, origin):
        for m in messages:
            self._db.messages.update(m, {'$push': {'pings': origin}})

    def reg_attach(self, hash, meta):
        meta['hash'] = hash
        if self._db.chksums.find_one({'hash':hash}):
            raise StorageCollisionError(meta)
        self._db.chksums.save(meta)

    def del_attach(self, pred):
        self._db.chksums.remove(pred)
