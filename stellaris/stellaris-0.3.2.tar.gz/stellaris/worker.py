# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import os, time, random
from threading import Thread
from thread import get_ident
from Queue import Empty, Queue as TQueue
from processing import Queue, Process

from stellaris.utils import id_generator
from stellaris.exceptions import WorkerNotConfigured, WorkerTimeout, ConfigAttributeMissing
from stellaris.message import MethodCallMsg, MethodCallResultMsg

class Worker(Process):

    def __init__(self, cancel_timeout=60.0, queue_timeout=1.0, log=None):
        """
        ``config`` - a nested hash-map used in setup to initiate process-local
                     state. This will be pickled.
        ``cancel_timeout`` - cancels requests after the given timeout
        ``queue_timeout`` - timeout passed to a get from ``Queue.Queue``.
        """
        self.__input_q = Queue()
        self.__output_q = Queue()
        self.__queues = {}

        self.__cancel_timeout = cancel_timeout
        self.__timeout = queue_timeout
        self.__id_generator = id_generator()

        self.__queue_handler_t = Thread(target=self.__handle_output_q)
        
        self.__is_configured = False
        Process.__init__(self)
        self.log = log
        self.start()
        # let the thread start
        time.sleep(0.1)

    def __handle_output_q(self):
        if self.log:
            self.log.debug("Thread handling output starting: %s" % (str(get_ident())))
        
        while True:
            try:
                msg = self.__output_q.get(timeout=self.__timeout)
                if msg == None:
                    break
                
                self.__queues[msg.msgid].put(msg)
            except Empty, e:
                continue
            except KeyError, e:
                if self.log:
                    self.log.error('Queue for the message with id %s does not exist.' % str(e))
            except Exception, e:
                if self.log:
                    import traceback
                    self.log.error('Generic exception returned by worker %s: %s\n%s' %(self.getName(), str(e), traceback.format_exc()))

        if self.log:
            self.log.debug("Thread handling output stopping: %s" % (str(get_ident())))

    def setup(self):
        """
        The class inheriting ``Worker`` must implement this method. It will
        be called before the main-loop in run() is started. The state of a
        worker must _not_ be initiated in __init__, since it is not always
        possible to pass this state along when the new process spawns.
        
        ``config`` - a dictionary with configuration variables used to initiate
                     the worker state.
        """
        return NotImplemented
    
    def dispatch(self, msg):
        """
        Dispatches the message to the right method according to the internal
        state. This method must be implemented by the user of this class. 
        Returns the result of the processing or raises an exception.
        
        ``msg`` - dispatch this message
        """
        return NotImplemented
        
    def teardown(self):
        """
        Called after the main-loop has finished or when the process receives
        a shutdown (SIGTERM, SIGKILL)-signal.
        """
        return NotImplemented

    def start(self):
        #self.__queue_handler_t.start()
        Process.start(self)
    
    def configure(self, config):
        """
        Configures the worker. This must be run before any other methods of
        the backend is called.
        """
        # insert the config for the worker
        self.__input_q.put(config)
        
        while True:
            try:
                res = self.__output_q.get(timeout=self.__timeout)
                
                if res == None:
                # shutdown received before configuration has finished
                    return

                if not res == True:
                    # 
                    #self.__output_q.put(None)
                    raise res
                break
            except Empty, e:
                pass
#            except Exception, e:
#                raise e
                
        # ready to receive requests, this must be set _outside_ the
        # worker process since method calls are initiated from
        # a thread running on the controller side.
        self.__is_configured = True                 

        # start the queue handler thread which will handle any
        # calls to the worker
        self.__queue_handler_t.start()
                    
    def run(self):
        # startup loop, waiting for the configuration
        
        while True:
            try:
                config = self.__input_q.get(timeout=self.__timeout)
                
                if config == None:
                    self.__output_q.put(None)
                    self.stop()
                    return
                
                try:
                    # pass the locally initiated config, otherwise __getattr__ gets 
                    # called
                    self.setup(config)
                    # let the caller know that config went fine
                    self.__output_q.put(True)
                    # stop the config-loop
                    break
                except Exception, e:
                    if self.log:
                        self.log.debug('Stopping worker %s due to unhandled exception: %s,%s' %(self._name, type(e), str(e)))
#                    print "got exception, stopping worker", self._name, e
                    #self.__input_q.put(None)
                    # return the exception to the waiting thread
                    # for some reason, the ConfigAttributeMissing exception
                    # cannot be passed over the queue.
                    self.__output_q.put(Exception(str(e)))
                    time.sleep(0.1)
                    return
                                
            except Empty, e:
                continue
        
#        print "starting configured worker", self._name
        while True:
            try:
                msg = self.__input_q.get(timeout=self.__timeout)
                
                if msg == None:
                    break
            except Empty:
                continue
            except (KeyboardInterrupt, SystemExit):
                # someone wants to stop the service
                break

            # do the processing of the message
            res_msg = MethodCallResultMsg(msgid=msg.msgid)
            
            try:
                res_msg.result = self.dispatch(msg)
            except Exception, e:
                res_msg.fail = True
                res_msg.result = e

            #print "Method call results: ", res_msg
            self.__output_q.put(res_msg)
            
        self.teardown()

        # stop the thread waiting for output
        self.__output_q.put(None)
        
    def stop(self):
        self.__input_q.put(None)
        
        # note: the thread waiting for output is stopped from the main worker
        #       loop. When this joins, both the worker and the output handler
        #       thread should be stopped.
        try:
            self.__queue_handler_t.join()

            # stop any other threads blocking while waiting for result
            for queue in self.__queues.values():
                queue.put(None)

        except AssertionError, e:
            # thrown when the thread is not started, don't care about this
            # since stop was called before the worker was configured
            pass

    def __getattr__(self, name):
        if self.__is_configured == False:
            raise WorkerNotConfigured('%s was called before the Worker was configured.' % (name))
        
        def f(*args, **kwargs):
            # the msg contains a queue id, the queue id is used to get the queue
            # where the result should be inserted
            
            m = MethodCallMsg(random.random(), name, *args, **kwargs)
            self.__queues[m.msgid] = TQueue()
            self.__input_q.put(m)

            if self.log:
                self.log.debug('Request: %s' %(repr(m)))

            total_time = 0
            
            while total_time < self.__cancel_timeout:
                try:
                    res = self.__queues[m.msgid].get(timeout=self.__timeout)

                    if self.log:
                        self.log.debug('Response: %s' %(repr(res)))
                        
                    if res == None:
                        break
                        
                    del self.__queues[m.msgid]
                    
                    if res.fail:
                        raise res.result
                        
                    return res.result
                    
                except Empty, e:
                    total_time += self.__timeout
                except Exception, e:
                    raise

            raise WorkerTimeout('Worker timed out while executing %s.' % name)

        return f
                      
if __name__ == '__main__':
    w = Worker(cancel_timeout=1.0)

    print "main thread: ", get_ident()
    
    print "time: ", time.time()
    w.update(34)
    w.update(12)
#    print "time: ", time.time()
#    print "return\n ", w.sleep(10.0)
    print "time: ", time.time()    

    try:
        print "calling w.exc"
        w.exc()
    except Exception,e:
        print "exc: ", e

    print "time: ", time.time()        
    w.sleep(10.0)
    print "time: ", time.time()            
    print "stop is called already?"
    w.stop()
