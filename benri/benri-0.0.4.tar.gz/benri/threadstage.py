# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import random

from threading import Thread
from Queue import Queue, Empty

SHUTDOWN = 0
SELF = 1
OTHER = 2

class EventHandler(object):
    pass
    
#    def __getattribute__(self, name):
#        try:
#            func = getattr(self, "event_%s" % name)
#        except AttributeError:
#            raise
#        else:
#            return func
            
class ThreadStage(object):
    """
    A stage is a single thread with a queue. The main idea with the stage is
    to serialize access to state in order to avoid locking problems with
    concurrent access. This stage class is simple in the way that calls to a
    single user-defined function is serialized.
    
    Usage example:
    
    >>> import time
    >>> h = {'a':0}
    >>> def f(state):
    ...     k, htable = state
    ...     htable[k] += 1
    >>> stage = ThreadStage(f)
    >>> stage.start()
    >>> stage.send_async(('a', h))
    >>> h
    {'a': 0}
    >>> time.sleep(0.01)
    >>> h
    {'a': 1}
    >>> stage.stop()
    """
    def __init__(self, f):
        self.q = Queue(0)
        self.__f = f
        self.__thread = Thread(target=self.worker)

    def worker(self):
        active = True
        
        while active:
            try:
                (sender, state) = self.q.get(timeout=1)
            except Empty:
                continue
            
            if sender == SELF and state == SHUTDOWN:
                active = False
            else:
                self.__f(state)

    def send_async(self, state):
        self.q.put((OTHER, state))

    def send(self, state):
        self.q.put((OTHER, state))
    
    def start(self):
        self.__thread.start()
        
    def stop(self):
        self.q.put((SELF, SHUTDOWN))
        self.__thread.join()

class ThreadStageEvent(object):
    """
    The ThreadStageEvent-class takes an instance that inherits from the
    EventHandler-class and implements event handler methods.
    
    Example usage:
    
    >>> import time
    >>> class C(EventHandler):
    ...     def __init__(self):
    ...         self.state = 0
    ...     def event_test(self, state):
    ...         self.state += state
    ...         return self.state
    >>> c = C()
    >>> stage = ThreadStageEvent(c)
    >>> stage.start()
    >>> stage.send(None, 'test', 5)
    >>> c.state
    0
    >>> time.sleep(0.01)
    >>> c.state
    5
    >>> stage.stop()
    """
    
    def __init__(self, instance):
        self.q = Queue(0)
        self._thread = Thread(target=self.worker)
        self._instance = instance
#        self.__thread.start()        

    def worker(self):
        active = True
        
        while active:
            try:
                (sender, event, state) = self.q.get(timeout=1)
            except Empty:
                continue
            except Exception, e:
                raise

            if sender == SELF and event == SHUTDOWN:
                active = False
            else:
                try:
                    f = getattr(self._instance, "event_%s" % event)
                    f(state)
                except AttributeError:
                    # if the event does not exist, message is lost
                    pass

    def send(self, sender, event, state):
        """
        Sends a message event to the local stage.
        
        `sender` - an instance of the stage that sent the message, this is used
                   for sending a message back with the results.
        `event`  - the event passed to the stage
        `state`  - the state passed together with the event
        """
        self.q.put((sender, event, state))

    def start(self):
        self._thread.start()
        
    def stop(self):
        self.q.put((SELF, SHUTDOWN, None))
        self._thread.join()

class ThreadStageOrderedEvent(ThreadStageEvent):
    """
    The ThreadStageEventOrdered-class extends ThreadStageEvents by executing
    the incoming messages according to their version. A message with version
    v must execute before a message with version v+1. If there are any gaps in
    the versioning, the stage will wait until it receives all messages filling
    the gap. Messages with a version number less than the current are dropped.
    
    Example usage:
    
    >>> import time  
    >>> class C(EventHandler):
    ...     def __init__(self):
    ...         self.state = 0
    ...     def event_test(self, state):
    ...         self.state += state
    ...         return self.state
    >>> c = C()
    >>> stage = ThreadStageOrderedEvent(c)
    >>> stage.start()
    >>> stage.send(None, 'test', 1, 0)
    >>> c.state
    0
    >>> time.sleep(0.01)    
    >>> c.state
    1
    >>> stage.send(None, 'test', 1, 1)
    >>> stage.send(None, 'test', 1, 3)
    >>> time.sleep(0.01)
    >>> c.state
    2
    >>> stage.send(None, 'test', 1, 2)
    >>> time.sleep(0.01)
    >>> c.state
    4
    >>> stage.send(None, 'test', 1, 2)
    >>> time.sleep(0.01)
    >>> c.state
    4
    >>> stage.send_blocking(None, 'test', 1, 4)
    5
    >>> stage.stop()
    """

    def __init__(self, instance):
        ThreadStageEvent.__init__(self, instance)
        self.__running = False
    
    def send(self, sender, event, state, version):
        """
        Sends a message event to the local stage.
        
        `sender` - an instance of the stage that sent the message, this is used
                   for sending a message back with the results.
        `event`  - the event passed to the stage
        `state`  - the state passed together with the event
        `version` - version of the message
        """
        self.q.put((sender, event, state, version, None))

    def send_blocking(self, sender, event, state, version):
        """
        Sends a message event to the local stage. Blocks the calling thread
        until the results are returned. If the called method instance raises
        an exception, this is re-raised here.
        
        `sender` - an instance of the stage that sent the message, this is used
                   for sending a message back with the results.
        `event`  - the event passed to the stage
        `state`  - the state passed together with the event
        `version` - version of the message
        """
        block_q = Queue(0)
        
        self.q.put((sender, event, state, version, block_q))

        while True:

            try:
                results = block_q.get(timeout=0.1)
                    
                if isinstance(results, Exception):
                    raise results

                return results
            except Empty, e:
                pass
                
    def worker(self):
        active = True
        current_version = 0
        waiting_msgs = []
        
        while active:
            try:
                (sender, event, state, version, block_q) = self.q.get(timeout=1)
            except Empty:
                continue
#            except Exception, e:
#                raise

            
            if sender == SELF and event == SHUTDOWN:
                active = False
            else:
                if version == current_version:
                    try:
                        f = getattr(self._instance, "event_%s" % event)
                        ret = f(state)
                        
                        if block_q:
                            block_q.put(ret)
                    except Exception, e:
                        if block_q:
                            block_q.put(e)
                    
                    # re insert all the waiting messages
                    for sender, event, state, msg_version in waiting_msgs:
                        if msg_version > current_version:
                            self.q.put((sender, event, state, msg_version, block_q))
                    
                    waiting_msgs = []
                    current_version += 1
                                            
                elif version > current_version:
                    waiting_msgs.append((sender, event, state, version))

    def start(self):
        self.__running = True    
        self._thread.start()

    def stop(self):
        self.__running = False
        self.q.put((SELF, SHUTDOWN, None, None, None))
        self._thread.join()

class ThreadStagePeriodic(ThreadStage):
    def __init__(self, trigger, interval):
        ThreadStage.__init__(self, trigger)
        self.__interval = interval

    def worker(self):
        active = True
        
        while active:
            try:
                (sender, state) = self.__q.get(timeout=self.__interval)
            except Empty:
                self.__f()
                continue
            
            if sender == SELF and state == SHUTDOWN:
                active = False

# in a thread stage pool, we have several threads sharing a common queue
# i.e. we cant ensure serialized access to state
# this class is just a simple worker pool
class ThreadStagePool(ThreadStage):
    """
    A simple thread pool which executes a user-defined function. Unlike the
    ThreadStage-class, this function may be executed concurrently by any of the
    `num_workers` threads in the thread-pool.
    
    Example usage:
    
    >>> def f(state):
    ...     state + 1
    >>> pool = ThreadStagePool(f, 5)
    >>> pool.start()
    >>> pool.send_async(12)
    >>> pool.stop()
    """
    def __init__(self, f, num_workers):
        ThreadStage.__init__(self, f)
        self.__num_workers = num_workers
        self.__threads = []

        for i in range(self.__num_workers):
            self.__threads.append(Thread(target=self.worker))

    def start(self):
        for t in self.__threads:
            t.start()

    def stop(self):
        for i in range(self.__num_workers):
            self.q.put((SELF, SHUTDOWN))

class ThreadStagePoolEvent(ThreadStage):
    """
    A thread pool which executes a user-defined function and replies to another
    stage. The events passed back are `worker_done` and `worker_failed`. Unlike
    the ThreadStageEvent-class, this function may be executed concurrently by any
    of the `num_workers` threads in the thread-pool.
    
    Example usage:
    
    >>> import time
    >>> def f(state):
    ...     return state + 1
    >>> class Handler(EventHandler):
    ...     def event_worker_done(self, res):
    ...         return res
    ...     def event_worker_failed(self, exc):
    ...         raise exc
    >>> stage = ThreadStageEvent(Handler())
    >>> stage.start()
    >>> pool = ThreadStagePoolEvent(f, stage, 5)
    >>> pool.start()
    >>> pool.send(12)
    >>> time.sleep(0.1)
    >>> pool.stop()
    >>> stage.stop()
    """
    def __init__(self, f, stage, num_workers):
        ThreadStage.__init__(self, f)
        self.__f = f
        self.__num_workers = num_workers
        self.__threads = []
        self.__stage = stage
        
        for i in range(self.__num_workers):
            self.__threads.append(Thread(target=self.worker))

    def worker(self):
        active = True
        
        while active:
            try:
                (sender, state) = self.q.get(timeout=1)
            except Empty:
                continue
            
            if sender == SELF and state == SHUTDOWN:
                active = False
            else:
                try:
                    ret = self.__f(state)
                    self.__stage.send(self, 'worker_done', state)
                except Exception, e:
                    self.__stage.send(self, 'worker_failed', e)

    def change_callback(self, cb):
        self.__f = cb
        
    def start(self):
        for t in self.__threads:
            t.start()

    def stop(self):
        for i in range(self.__num_workers):
            self.q.put((SELF, SHUTDOWN))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
