# -*- coding: utf-8 -*-

#------------------------------------------------------------------
# Модель

import os

from time import time
from threading import Thread
from Queue import Queue

from pymongo import Connection as mongoConnect, \
    ASCENDING as ASC, DESCENDING as DESC
from pymongo.errors import OperationFailure
from pymongo.code import Code

from utils import flatten
from errors import Message404Error, File404Error

class Scheduler(Thread):
    """ Планировщик задач.

    Обеспечивает функционирование конвееров.
    """
    def __init__(self):
        Thread.__init__(self)
        self._names = {}
        self._queue = Queue()
        self._i = 0

    def run(self):
        while True:
            task, name = self._queue.get()
            del self._names[name]
            task()
            self._i += 1
            if self._i % 10 == 0:
                print 'Q size: %s' % self.stat()

    def stat(self):
        return self._queue.qsize()

    def enqueue(self, name, task):
        if name not in self._names:
            self._names[name] = True
            self._queue.put((task, name))

class Model:
    """ Модель хранилища на основе mongodb.

    Основная рабочая модель предназначенная для продакшена.
    """
    def __init__(self, config):
        """ Соединение с БД, настройка коллекций. """

        host, port = config.iface.split(':')
        self._db = db = mongoConnect(host, int(port))[config.dbname]

        self._cfg = config

        self._command = db.command

        self._messages = db.messages
        self._digest = db.digest
        self._boardid = db.boardid
        self._crc = db.crc

        self._harvesterDel = 0

        self.__insure_indexes()

        self._sched = Scheduler()
        self._sched.start()

        # Map reduce functions
        self._mr = map(Code, open('backends/digest.js')\
                           .read()\
                           .replace('/*TAIL*/', str(config.tailCount))\
                           .split('/***/'))

    def __insure_indexes(self):
        self._command('repairDatabase')
        self._messages.ensure_index('ts')
        self._messages.ensure_index('parent')
        self._digest.ensure_index('bump')

    def __nextid(self):
        """ Получение индексов для новых сообщений """
        try:
            nid = self._command(
                "findandmodify",
                "boardid",
                query={},
                update={"$inc": {"id": 1}})
        except OperationFailure:
            self._boardid.save({'id': 1})
            return 1

        return nid['value']['id']

    # TODO: Поместить map-reduce прямо сюда.
    def __build_digest(self, q):
        """ Обновление дайджеста треда """
        mr_success = False
        attempts = 5
        while not mr_success and attempts > 0:
            try:
                digests = self._messages.map_reduce(self._mr[0], self._mr[1], sort={'ts':1}, query=q)
                mr_success = True
            except Exception, x:
                print "Map Reduce failed at query: %s" % q
                attempts -= 1
                self.__insure_indexes()
                pass
        if attempts == 0:
            print "Map Reduce COMPLETELY failed at query: %s" % q
            return
        else:
            for d in digests.find():
                self._digest.save(d['value'])
            self._db.drop_collection(digests)

    def __harvest(self):
        """ Подтирает хвост, возможно перемещает треды в архив. """
        harvested = 0
        threads = self._messages.find(
            {'$where':"this._id == this.parent"},
            sort=[('ts',-1)],
            skip=self._cfg.maxThreads
            )
        for doomed in threads:
            harvested += 1
            doomedFiles = self._messages.find(
                {'parent':doomed['_id']}, fields=['attaches'])
            for df in flatten(map(lambda p: p['attaches'], doomedFiles)):
                try:
                    os.remove(os.path.join(
                            self._cfg.attPath, '%s%s' % tuple(df['name'])))
                except Exception, x:
                    print x
                if 'thumb' in df:
                    try:
                        os.remove(os.path.join(
                                self._cfg.thumbPath,
                                '%s%s' % tuple(df['thumb']['name'])))
                    except Exception, x:
                        print x
            self._messages.remove({'parent':doomed['_id']})
        print "Harvester: %s threads removed." % harvested

    def get_msgs(self, pred, limit=None):
        return self._messages.find(pred, limit=limit)

    def del_msg(self, pred):
        doomed = self._messages.find(pred, {_id:1})
        if doomed:
            self._messages.remove(doomed)
        else:
            raise Message404Error(pred)

    def save(self, message):
        message['_id'] = message['num'] = self.__nextid()
        message['ts'] = int(time())
        if 'parent' not in message:
            threadid = message['num']
            threadSize = 1
        else:
            threadid = int(message['parent'])
            threadSize = self._digest.find_one(
                {'_id': threadid}, fields=['postsCount'])['postsCount']

        message['parent'] = threadid

        if threadSize >= self._cfg.bumpLimit:
            message['sage'] = 'auto'

        self._messages.save(message)

        def closure(tid):
            def task():
                self.__build_digest({'parent': tid})
            return task
        self._sched.enqueue(threadid, closure(threadid))

        if message['parent'] == message['_id']:
            self._harvesterDel += 1
            if self._harvesterDel >= self._cfg.harvesterDelta:
                self._harvesterDel = 0
                def task():
                    self.__harvest()
                self._sched.enqueue('harvest', task)

    def delete(self, message_id):
        """ Удаление сообщения """
        msg = self._messages.find({'_id':message_id})
        if msg['_id'] == msg['parent']: # Удаление треда
            self._digest.remove({'op': {'_id': message_id}})
        else:
            self._messages.remove({'_id':message_id})
            self.__build_digest({'parent': msg['parent']})

    def digestList(self, lim, ofs=0):
        # Нужно, чтобы результат поддерживал len(), а драйвер класс
        # Cursor драйвера pymongo этого не делает.
        return map(
            lambda x:x,
            self._digest.find().sort('bump', DESC)
            .skip(int(ofs)).limit(int(lim)))

    def thread(self, num):
        return self._messages.find({'parent':int(num)}).sort('ts', ASC)

    def getPost(self, num):
        return self._messages.find_one({'_id':int(num)})

    def findFile(self, checksum):
        return self._crc.find_one({'_id':checksum})

    def addFile(self, checksum):
        return self._crc.insert({'_id':checksum})

    def forgetFile(self, checksum):
        self._crc.remove({'_id':checksum})
