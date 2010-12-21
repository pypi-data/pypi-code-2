# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging

from threading import Thread
from Queue import Queue, Empty

log = logging.getLogger('stellaris.store')

class IntervalThread(Thread):
    def __init__(self, gc_func, interval=60.0, log=None):
        Thread.__init__(self)
        self.__gc_q = Queue()
        self.__cb = gc_func
        self.__interval = interval
        self.__log = log

    def run(self):
        total_timeout = 0.0
        timeout = 0.5
        while True:
            try:
                self.__gc_q.get(timeout=timeout)
                return
            except Empty, e:
                total_timeout += timeout
                
                if total_timeout < self.__interval:
                    continue
                
                total_timeout = 0.0
                
                try:
                    self.__cb()
                except Exception, e:
                    if self.__log:
                        self.__log.info('Garbage collection failed: %s' % (str(e)))

    def stop(self):
        self.__gc_q.put(None)
        self.join()
                           
class Store(object):
    
    def __init__(self, gc_interval=3600, backup_interval=86400, backup_path=None, log=None):
#        self.config = config
        if gc_interval > 0:
            self.__gc_t = IntervalThread(self.garbage_collection, interval=gc_interval, log=log)
            self.__gc = True
        else:
            self.__gc = False

        if backup_interval > 0 and backup_path:
            self.__backup_t = IntervalThread(self.backup, interval=backup_interval)
            self.__backup = True
        else:
            self.__backup = False

        self.backup_path = backup_path

        self.log = log
        
    def create(self, graph):
        pass

    def open(self):
        if self.__gc:
            self.__gc_t.start()
        
        if self.__backup:
            self.__backup_t.start()

    # these are graph modifiers, shouldnt the interface only deal with
    # things that are relevant to the store? 
    # (update, replace, append, remove, atomic_ops, change ttl, etc.)
    # These operations are already part of the Graph class
    
#    def update(self, name, graph):
#        pass

#    def replace(self, name, graph):
#        pass

#    def append(self, name, graph):
#        pass

#    def remove(self, name, graph):
#        pass
    
#    def atomic_operations(self, name, ops):
#        pass

    def retrieve(self, name, version=None):
        pass
    
    def update(self, graph):
        pass
        
    def delete(self, name):
        pass
    
    def exists(self, name, prefix_lookup=False):
        """
        Check if the graph with the given name exists. If prefix_lookup is
        ``True``, each prefix in the hierarchy of the name is checked for
        existence. Returns the prefix if any is found, otherwise ``None``.
        
        Note: Even if this returns the prefix, there may be another thread in 
              the system that removes the graph before it has a chance to be 
              retrieved.
              
        ``name`` - the (hierarchical) name of the graph
        ``prefix_lookup`` - indicates if an hierarchical prefix search should be
                            performed. Default is ``False``.
        """
   
    def garbage_collection(self):
        """
        Runs a garbage collection routine for the store. This includes removal
        of expired graphs etc. .
        """

    def backup(self):
        """
        Performs a backup in a store specific manner.
        """

    def close(self):
        """
        Closes the store.
        """
        if self.__gc:
            if self.log:
                self.log.debug("Shutting down garbage collection")
            self.__gc_t.stop()
            self.__gc_t.join()

        if self.__backup:
            self.__backup_t.stop()
            self.__backup_t.join()

# define imports

from stellaris.store.federation import FederationStore
from stellaris.store.stage import StageStore
from stellaris.store.version import VersionStore
from stellaris.store.lifetime import LifetimeStore
from stellaris.store.secure import SecureStore
#from stellaris.store.store import Store
from stellaris.store.backend import BackendStore
from stellaris.store.frontend import FrontendStore
        
