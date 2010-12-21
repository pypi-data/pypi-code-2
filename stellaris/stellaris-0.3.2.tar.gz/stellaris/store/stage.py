# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, os
from threading import Thread
from Queue import Queue, Empty

log = logging.getLogger('stellaris')

class RequestTimedOut(Exception): pass

class StageVersioned(Thread):
    """
    Execute requests to the instance in order based on a version number.
    
    ``instance`` - the instance
    ``request_timeout`` - cancel requests running for longer than this time
    """
    def __init__(self, instance, request_timeout=60.0):
        Thread.__init__(self)
        self.__q = Queue(0)
        self.__instance = instance
        self.__request_timeout = request_timeout

    def run(self):
        active = True
        current_version = 0
        waiting_msgs = []
        
        while active:
            try:
                (method, args, kwargs, return_q) = self.__q.get(timeout=1)
            except Empty:
                continue
#            except Exception, e:
#                raise

            if method == None and return_q == None:
                active = False
            else:
                # with no version, this message can be executed at any time
                version = kwargs.get('version', None)

                if version == current_version or version == None:
                    try:
                        f = getattr(self.__instance, method)
                        # dont pass on the message version
                        try:
                            kwargs['version']
                        except KeyError, e:
                            pass
                            
                        ret = f(*args, **kwargs)
                        
                        if return_q:
                            return_q.put(ret)
                    except Exception, e:
                        if return_q:
                            return_q.put(e)
                    
                    # re-insert all the waiting messages
                    for w_method, w_args, w_kwargs, w_return_q in waiting_msgs:
                        if w_kwargs['version'] > current_version:
                            self.__q.put((w_method, w_args, w_kwargs, w_return_q))
                    
                    waiting_msgs = []
                    if version != None:
                        current_version += 1
                                            
                elif version > current_version:
                    waiting_msgs.append((method, args, kwargs, return_q))


    def schedule(self, method, *args, **kwargs):
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
        
        self.__q.put((method, args, kwargs, block_q))

        timeout = 0.1
        
        if self.__request_timeout < timeout:
            timeout = self.__request_timeout
            
        timeout_sum = 0.0
        active = True
        
        while active:

            try:
                results = block_q.get(timeout=timeout)
                    
                if isinstance(results, Exception):
                    raise results

                return results
            except Empty, e:
                timeout_sum += timeout
                
                # if the request has timed out, raise RequestTimedOut
                if self.__request_timeout < timeout_sum:
                    raise RequestTimedOut('Request cancelled after %s seconds.' % self.__request_timeout)
                
    def stop(self):
        self.__q.put((None, None, None, None))
#        Thread.stop(self)

# this class cannot inherit from Store since __getattr__ would not work
# if there is any class in the hierarch implementing the called method
# the class-implementation will be used before __getattr__ is called
class StageStore(object):
    """
    The stage store serializes requests to the underlaying stores. All methods
    calling the stage store must have a keyword argument ``version``. The 
    version is the logical time of the message and the version must be 
    monotonically increased for each new method call. If there is a gap between
    versions, the system will wait until all previous versions have executed.
    """

    def __init__(self, store, timeout=60.0):
        self.__store = store
        self.__ordered_stage = StageVersioned(store, request_timeout=timeout)
        
        self.__ordered_stage.start()
        
    def __getattr__(self, name):
        """
        Return a function that when called, passes a message to the ordered
        event stage.
        """
        # make sure the store has the method
        try:
            func = getattr(self.__store, name)
        except AttributeError:
            raise

        # define a method that when called passes all the data
        # through the ordered stage with the method name.
        # this is then used in the handler to execute the method, which
        # returns the data from the blocking send.
        def message(*args, **kwargs):
            try:
                return self.__ordered_stage.schedule(name, *args, **kwargs)
            except Exception, e:
                raise

        return message
                    
    def close(self):
        self.__ordered_stage.stop()

