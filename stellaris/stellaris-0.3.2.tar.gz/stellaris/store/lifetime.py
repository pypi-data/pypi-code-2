# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, os, time

from threading import Thread
from rdflib.Graph import Graph
from cStringIO import StringIO
from benri.db import Index
from sched import scheduler
from Queue import Queue, Empty

from stellaris.store import VersionStore
from stellaris.exceptions import ConfigAttributeMissing

log = logging.getLogger('stellaris')

class LifetimeStore(VersionStore):
    """
    Maintains the lifetime of a graph. The user must actively assign a lifetime
    to the graph, which is not 
    """
    
    def __init__(self, config):
        try:
            self.__db = config['internal']['db_instance']
        except KeyError, e:
            raise ConfigAttributeMissing('internal', 'db_instance')
        
        try:
            self.__cb = config['internal']['lifetime_callback']
        except KeyError, e:
            raise ConfigAttributeMissing('internal', 'lifetime_callback')

        # this is the persistent store with absolute values of when the graph
        # should be removed from the system
        self.__ttls = Index('lifetime.db', self.__db)
        self.__scheduler = scheduler(time.time, time.sleep)
        self.__events = {}

        self.__scheduler_thread = Thread(target=self.__scheduler_run)
        self.__scheduler_thread.start()
        self.__shutdown_queue = Queue(0)
                        
        VersionStore.__init__(self, config)

    def __scheduler_run(self):
        while True:
            try:
                val = self.__shutdown_queue.get(timeout=1.0)
                # stop the thread if something is in the shutdown queue
                return 
            except Empty:
                # continue running the scheduler while the thread is active
                self.__scheduler.run()
            
    def assign_ttl(self, name, ttl, user=None):
        """
        Set the TTL for a graph. Graphs with a TTL assigned already are 
        overwritten.
        
        ``name`` - The name of the graph.
        ``ttl`` - the relative time in seconds before the graph is removed
        ``user`` - the user that will be used when removing the graph
        """
        try:
            self.__scheduler.cancel(self.__events[name])
        except KeyError, e:
            # nothing bad happened here
            pass
            
        trigger_t = time.time() + ttl

        event = self.__scheduler.enterabs(trigger_t, 0, self.__cb, (name, user))
        self.__events[name] = event
        
        # mapping from graph name -> trigger_t which is necessary for graph
        # recovery
        self.__ttls[name] = trigger_t

    def remove_ttl(self, name):
        """
        Removes the TTL assigned to the graph.
        
        ``name`` - The name of the graph from which the TTL should be removed
        """
        self.__scheduler.cancel(self.__events[name])
        del self.__events[entry]       
        del self.__index[entry]
        
    def close(self):
        self.__shutdown_queue.put(True)
        self.__ttls.close()
        VersionStore.close(self)
