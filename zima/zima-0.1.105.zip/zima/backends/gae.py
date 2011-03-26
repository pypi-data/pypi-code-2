import os

from time import time

from google.appengine.ext import db

class StorageFailError(Exception):
    def __init__(self, val='Unknown fail'):
        self.value = val
    def __str__(self):
        return repr(self.value)

class Document(db.Expando):
    pass


class Counter(db.Model):
    val = db.IntegerProperty(default=0)

    def nextid(self):
        attempts = 5
        while attempts:
            attempts -= 1
            try:
                def incr_cntr():
                    self.val+=1
                    self.put()
                    db.run_in_transaction(incr_cntr)
            except db.Rollback, r:
                if attempts > 0:
                    continue
                else:
                    raise StorageFailError('Failed to increment counter')
                break
            return self.counter

class Model():
    """ Модель хранилища на основе GAE.

    Вторая основная рабочая модель предназначенная для продакшена.
    """


    def __init__(self, config):
        """ Соединение с БД, настройка коллекций. """

        self._cfg = config

    def save(self, message, raw=False):
        """ Сохранение нового или уже имеющегося сообщения """

        doc = Document()

        for k, v in message:
            setattr(doc, k, v)

        if raw:
            self._messages.save(message)
            return

        doc.id = self.__nextid__()
        doc.ts = int(time())

        if 'parent' not in message:
            threadid = doc.id
            threadSize = 1
        else:
            threadid = int(message['parent'])
            threadSize = self._digest.find_one(
                {'_id': threadid}, fields=['postsCount'])['postsCount']

        doc.parent = threadid

        if threadSize >= self._cfg.bumpLimit:
            doc.sage = 'auto'

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
        return map(
            lambda x:x,
            self._digest.find().sort('bump', DESC)
            .skip(int(ofs)).limit(int(lim)))

    def thread(self, num):
        return self._messages.find({'parent':int(num)}).sort('ts', ASC)

    def threadCount(self):
        return self._digest.count()

    def postCount(self):
        return self._messages.count()

    def getPost(self, num):
        return self._messages.find_one({'_id':int(num)})

    def findFile(self, checksum):
        return self._crc.find_one({'_id':checksum})

    def addFile(self, checksum):
        return self._crc.insert({'_id':checksum})

    def forgetFile(self, checksum):
        self._crc.remove({'_id':checksum})

