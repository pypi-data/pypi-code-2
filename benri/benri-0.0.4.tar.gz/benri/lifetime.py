# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import time
from Queue import Queue, Empty
from sched import scheduler
from threading import Thread

from benri.db import DB, Index
from benri.threadstage import ThreadStageEvent, ThreadStagePoolEvent, EventHandler

class SchedulerHandler(EventHandler):

    def __init__(self, db_path, scheduler, scheduler_event):
        self.__db = DB(db_path)
        self.__index = Index('lifetime.db', self.__db)
        self.__scheduler = scheduler
        self.__events = {} # key -> event
        self.__scheduler_event = scheduler_event
        self.recover()

    def recover(self):
        # the scheduler thread is not started yet, so there is no risk for 
        # conflicts
        for (entry, ttl) in self.__index:
            event = self.__scheduler.enterabs(float(ttl), 0, self.__scheduler_event, [entry])
            self.__events[entry] = event

    def event_update(self, state):
        entry, trigger_time = state

        try:
            # cancel any previous events registered with this entry
            self.__scheduler.cancel(self.__events[entry])
            del self.__events[entry]
        except KeyError, e:
            # entry does not have an assigned event
            pass
        except RuntimeError, e:
            # this happens when a non-active event was cancelled
            pass
        except Exception, e:
            #print self.__events[entry]
            #print e
            pass
        
#        print "event update: ", state
        # what thread is the scheduler executing in, data_stage thread?
        event = self.__scheduler.enterabs(trigger_time, 0, self.__scheduler_event, [entry])
        self.__events[entry] = event
        self.__index[entry] = str(trigger_time)
        
    def event_delete(self, entry):
        try:
            self.__scheduler.cancel(self.__events[entry])
            del self.__events[entry]            
            del self.__index[entry]
        except ValueError, e:
            # if value error is raised, the event has been triggered, but 
            # worker_done or worker_failed has not yet been called, it is ok
            # to ignore this error since a cleanup of the state will be done
            # when worker_done is called
            pass
        except KeyError, e:
            # key error is ok here, just means that there where no events
            # registered for this key
            pass

    # this event is called when the worker is done with his task
    def event_worker_done(self, entry):
        try:
            del self.__events[entry]
            del self.__index[entry]
        # this means that the event was already removed, because event delete
        # was called after the event was executed by the scheduler but before
        # the worker_done message was sent.
        except KeyError, e:
            pass
            #pass

    def event_worker_failed(self, entry):
        # worker failure removes the event from the event lists, however,
        # TODO: the failure should be passed on as an exception to the user
        # then they can react by for example re-inserting the event.
        try:
            del self.__events[entry]
            del self.__index[entry]
        # this means that the event was already removed, because event delete
        # was called after the event was executed by the scheduler but before
        # the worker_done message was sent.
        except KeyError, e:
            pass
        
#        print "event worker_failed: ", entry, time.time()    

    def close(self):
        self.__index.close()
        self.__db.close()

# TODO: change into persistent scheduler and not lifetime
             
class Lifetime(Thread):
    """
    Maintains a lifetime (Time-To-Live) for keys. Calls a user-defined callback
    with the key as argument when the its lifetime has expired. The time 
    resolution is seconds.
    """
    
    # re-design to use the python sched-module
    # single stage handling both memory and persistent state, since a stage is
    # a single thread, we don't need to lock during change of lifetime for a key
    #
    # memory state: - hash-table with key -> scheduler event, used to cancel 
    #                 active events for a key
    #               - the scheduler itself
    #
    # persistent state: key and timestamp indicating when in seconds after 
    #                   epoch the event should be fired. This is used to rebuild
    #                   the hash-table and the scheduler state.
    #
    # worker pool: The event action is a put to a queue taken care of by a set
    #              of worker threads. This is necessary to not delay the
    #              scheduler when the action is blocking.
    
    def __init__(self, db_path, callback):
        Thread.__init__(self)
        # persistent state of the system
        self.__cb = callback
        
        self.__scheduler = scheduler(time.time, time.sleep)
        self.__sched_handler = SchedulerHandler(db_path, self.__scheduler, self.__scheduler_cb)
        self.__data_stage = ThreadStageEvent(self.__sched_handler)
        self.__worker_pool = ThreadStagePoolEvent(self.__cb, self.__data_stage, 15)

    def run(self):       
        self.__worker_pool.start()
        self.__data_stage.start()
        self.__running = True
        while self.__running:
            time.sleep(0.1)
            self.__scheduler.run()

    def stop(self):
        self.__worker_pool.stop()
        self.__data_stage.stop()
        self.__sched_handler.close()
        self.__running = False

    def change_callback(self, cb):
        self.__cb = cb
        self.__worker_pool.change_callback(cb)
        
    def __scheduler_cb(self, entry):
        # insert into the worker pool, make sure that empty entries
        # triggered by the sched-module are ignored
        if entry != None:
            self.__worker_pool.send(entry)          
                
    def __setitem__(self, entry, ttl):
        """
        Updates the ttl for the given entry. If the entry does not exist, it
        is created.
        """
        # current time + ttl is the time when to fire the event
        trigger_t = time.time() + ttl
        self.__data_stage.send(None, 'update', (entry, trigger_t))

    def __delitem__(self, entry):
        """
        Deletes a previously registered ttl for an entry.
        """
        self.__data_stage.send(None, 'delete', entry)
