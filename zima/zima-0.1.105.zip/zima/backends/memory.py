# -*- coding: utf-8 -*-
#
# Модель, хранящая данные в памяти
#
# Эта реализацпия не является ни быстрым, ни наиболее эффективным
# хранилищем данных. Скорее она написана для того, чтобы было понятно,
# что собственно должна делать модель.
#

from time import time
from threading import Lock

from zima.utils import flatten
from names import uid
from errors import StorageError, Message404Error, File404Error, \
    StorageCollisionError

class Model:
    """ Модель хранилища данных в оперативной памяти. """

    def __init__(self, cfg):
        """ В конструкторе в модель передается конфиг """
        self._mutex = Lock()

        self._cfg = cfg

        self._storage = []
        self._chksums = []

        def index_closure():
            index = [0]
            def incr():
                index[0] += 1
                return index[0]
            return incr

        self._nextid = index_closure()

    def _mkpred(self, pred):
        if 'num' in pred:
            pred['num'] = int(pred['num'])
        def predicate(x):
            for k,v in pred.items():
                if k not in x or x[k] <> v:
                    return False
            return True
        return predicate

    def get_msgs(self, pred, limit=None):
        return filter(self._mkpred(pred), self._storage)[:limit]

    def del_msg(self, pred):
        try:
            self._storage.remove(self.get_msg(pred, 1)[0])
        except IndexError:
            raise Message404Error({'pred': pred})

    def save_msg(self, message):
        message['ts'] = int(time())
        self._mutex.acquire()
        message['num'] = self._nextid()
        self._storage.append(message)
        self._mutex.release()
        if 'parent' not in message:
            message['parent'] = message['num']
        if 'attaches' not in message:
            message['attaches'] = []
        message['parent'] = int(message['parent'])
        threadLen = len(self.get_msgs({'parent': message['parent']}))
        if threadLen > self._cfg.bumpLimit:
            message['sage'] = message['sage'] or 'auto'
        if message['parent'] == message['num']:
            pass # TODO: Harvest

    def get_digests(self, pred, offset=0, limit=10000):
        limit = [limit]
        offset = [offset]
        def folder(res, x):
            if x['num'] == x['parent']:
                if offset[0] > 0:
                    offset[0] -= 1
                if offset[0] == 0 and limit[0] > 0:
                    limit[0] -= 1
                    res[x['num']] = {
                        'op': x,
                        'postsCount': 1,
                        'attachesCount': len(x['attaches']),
                        'omittedPosts': 0,
                        'omittedAttaches': 0,
                        'tail': []
                        }
            elif x['parent'] in res:
                thread = res[x['parent']]
                thread['tail'].append(x)
                thread['postsCount'] += 1
                thread['attachesCount'] += len(x['attaches'])
                doomed = thread['tail'][self._cfg.tailLength:]
                thread['tail'] = thread['tail'][:self._cfg.tailLength]
                if len(doomed) > 0:
                    thread['omittedPosts'] += len(doomed)
                    for d in doomed:
                        thread['omittedAttaches'] += len(d['attaches'])
            return res
        return reduce(folder,\
                          filter(self._mkpred(pred), self._storage),\
                          {}).values()

    def ping_msgs(self, origin, messages):
        predicates = map(self._mkpred, messages)
        for m in self._storage:
            for pred in predicates:
                if pred(m):
                    if 'pings' not in m:
                        m['pings'] = []
                        m['pings'].append(origin)

    def reg_attach(self, hash, meta):
        meta['hash'] = hash
        collisions = filter(self._mkpred({'hash':hash}), self._chksums)
        if len(collisions) > 0:
            raise StorageCollisionError({'meta':meta, 'found':collisions})
        self._chksums.append(meta)

    def del_attach(self, pred):
        doomed = filter(self._mkpred(pred), self._chksums)
        if len(doomed) == 0:
            raise File404Error(pred)
        for d in doomed:
            self._chksums.remove(d)
