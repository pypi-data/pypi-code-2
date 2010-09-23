import os
import md5
import time

try:
    from ZODB.POSException import ConflictError
    ZLOCK=True
except:
    ZLOCK=False
    

from lovely.memcached.utility import MemcachedClient

from config import PROJECTNAME

import logging


logger = logging.getLogger(PROJECTNAME)
_marker = []


## enable local module debug logging
## edit zope.conf as follows
##
## <eventlog>
##  level INFO
##  <logfile>
##    path <path to zope's event log>/var/log/instance.log
##    level DEBUG
##  </logfile>
## </eventlog>
##
## and uncomment following line
#
#  logger.setLevel(logging.DEBUG)




class DontLock(Exception):
    pass

class MemcachedRLock(object):

    recursive = True

    def __init__(self,client,key,timeout=30,intervall=0.05):

        self.mc = client
        self.uid = client.storage.uid
        self.key = key
        self.timeout = timeout
        self.intervall = intervall

        self.__owner = _marker
        self.__count = 0

        self._update()


    def __repr__(self):
        return "<%s(owner: %s, count: %d)>" % (
                self.__class__.__name__,
                self.__owner,
                self.__count)


    def acquire(self,blocking=True,timeout=None):

        waiting = False

        logger.debug('acquire (%s,%r)'   % (self.key,self))

        self._update()

        while True:
            
            if self.__count > 0:
                if self.__owner == self.uid:

                    if self.recursive:
                        self.__count += 1
                    break
                
                elif not blocking:
                    return False

            if self.__count == 0:
                if self.__owner is _marker and waiting:
                    logger.warning('%s.acquire(%s) expired' % (self,blocking,)) 
                self.__owner = self.uid
                self.__count = 1
                
                break
            
            if waiting is False:
                logger.warning('%s.acquire(%s) wait' % (self,blocking,))
                waiting = True

            time.sleep(self.intervall)
            
            self._update()

        
        res = not not self._set(timeout=timeout)

        if res:
            logger.debug('%s.acquire(%s) lock' % (self,blocking,))

        else:
            logger.warning('%s.acquire(%s) lock failed' % (self,blocking,)) 

        return res

    
    def release(self):

        assert self.__owner == self.uid, '%s.release() of un-acquire()d lock (owner)' % (self,)
        assert self.__count > 0, '%s.release() of un-acquire()d lock (count)' % (self,)

        self.__count-=1

        release = self._set()
        
        if release:
            logger.debug('%s.release()' % (self,))
        else:
            logger.warning('%s.release() failed' % (self,)) 


    def _update(self):

        key = self._make_key()
        value = self.mc.query(key)
        
        if value is None:
            self.__owner = _marker
            self.__count = 0
            return value

        self.__owner = value['owner']
        self.__count = value['count']


    def _set(self,timeout=None):

        if timeout is None:
            timeout = self.timeout

        value = dict(owner=self.__owner,count=self.__count)
        key = self._make_key()
        return self.mc.set(value,key,lifetime=timeout)

 
    def _make_key(self):
        return md5.new(self.key).hexdigest()



class MemcachedLock(MemcachedRLock):
    recursive = False



def lock_servers():
    servers = os.environ.get('MEMCACHEDLOCK_SERVERS',None)

    if not servers:
        return None

    servers = servers.split(",")

    for i, s in enumerate(servers):

        servers[i] = s.strip()

    return servers
    

def lock_getter(key,timeout=30,intervall=0.05):
    servers = lock_servers()
    client = MemcachedClient(servers=servers,defaultNS=unicode(PROJECTNAME),
                             defaultAge=timeout,trackKeys=True)
    return MemcachedLock(client,key,timeout=timeout,intervall=intervall)


def rlock_getter(key,timeout=30,intervall=0.05):
    servers = lock_servers()
    client = MemcachedClient(servers=servers,defaultNS=unicode(PROJECTNAME),
                             defaultAge=timeout,trackKeys=True)
    return MemcachedRLock(client,key,timeout=timeout,intervall=intervall)


def lock(get_key,timeout=30,intervall=0.05):
    def decorator(fun):
        def replacement(*args, **kwargs):

            try:
                key = get_key(fun, *args, **kwargs)
            except DontLock:
                return fun(*args, **kwargs)

            key = '%s.%s:%s' % (fun.__module__, fun.__name__, key)
            
            lock=lock_getter(key,timeout,intervall)

            try:
                lock.acquire()
                result = fun(*args, **kwargs)
            finally:
                lock.release()

            return result

        return replacement
    return decorator


def rlock(get_key,timeout=30,intervall=0.05):
    def decorator(fun):
        def replacement(*args, **kwargs):

            try:
                key = get_key(fun, *args, **kwargs)
            except DontLock:
                return fun(*args, **kwargs)

            key = '%s.%s:%s' % (fun.__module__, fun.__name__, key)
            
            lock=rlock_getter(key,timeout,intervall)

            try:
                lock.aquire()
                result = fun(*args, **kwargs)
            finally:
                lock.release()

            return result

        return replacement
    return decorator



if ZLOCK:

    def zlock(get_key,timeout=30,intervall=0.05):
        def decorator(fun):
            def replacement(*args, **kwargs):
                try:
                    key = get_key(fun, *args, **kwargs)
                except DontLock:
                    return fun(*args, **kwargs)

                key = '%s.%s:%s' % (fun.__module__, fun.__name__, key)
            
                lock = lock_getter(key,timeout,intervall)

                reserved = False
                try:

                    locked = lock.acquire(blocking=0)
                    if locked:
                        try:
                            result = fun(*args, **kwargs)
                        except ConflictError , msg:
                            reserved = lock.acquire(blocking=0,timeout=1)
                        
                            if reserved:
                                logger.error('Unexpected ConflictError, lock reserved (1s) for retry')
                            
                            raise ConflictError , msg
                    else:
                        reserved = lock.acquire(timeout=1)
                        
                        logger.warning('Raise ConflictError, lock reserved (1s) for retry')

                        raise ConflictError
                        
                finally:

                    # only release if not raised a ConflictError
                    if not reserved:
                        lock.release()

                return result

            return replacement
        return decorator
