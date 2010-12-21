# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

from __future__ import with_statement

import logging, os

from rdflib.Graph import Graph
from cStringIO import StringIO
from benri.db import DB
from threading import Lock

from stellaris.exceptions import ConfigAttributeMissing
from stellaris.store import StageStore, SecureStore
from stellaris.store.secure import SYSTEM_USER

log = logging.getLogger('stellaris')

class Store(object):
    """
    A Store combines functionality from different store-types. The store is
    used directly by the backend service interface.
    """
    
    def __init__(self, config):
        """
        Initializes a store with a ``config`` as read by the frontend. The 
        config should contain the following keys.
        
        ``store:db_path`` - path where different sub-components such as the
                              lifetime and user management can access their
                              databases.
        """
#         ``services:hayai`` - URL to the hayai service.
#         ``backend:type`` - Defines the backend to be used. Can be any of: 
#                            'rdflib-memory', 'rdflib-bdb', 'rdflib-mysql', 
#                            'virtuoso'. When a backend is defined, several other
#                            parameters must be defined as described below.

        #self.__stage_store = StageStore(config)
        try:
            db_path = config['store']['db_path']
        except Exception,e:
            ConfigAttributeMissing('store', 'db_path')
        
        self.__db = DB(db_path)
        # set the callback to use for lifetime
        # goes via the stage-store to circumvent the version-requirement
        config['internal'] = {'lifetime_callback': lambda graph, user: self.__stage_store.delete_graph(graph, user=user)}
        config['internal']['db_instance'] = self.__db
        
        self.__version = 0
        self.__store = SecureStore(config)
        self.__stage_store = StageStore(self.__store)

        self.__version_lock = Lock()
            
    def __getattr__(self, name):
        """
        Return a function that when called, passes a message to the ordered
        event stage. A call through the store must always contain a message
        version for the serialization of graph operations.        
        """
        # make sure the store has the method
        try:
            func = getattr(self.__stage_store, name)
        except AttributeError:
            raise

        # define a method that when called passes all the data
        # through the ordered stage with the method name.
        # this is then used in the handler to execute the method, which
        # returns the data from the blocking send.
        def f(*args, **kwargs):
            try:
                if not 'version' in kwargs:
 
 #                   kwargs['version'] = self.__version
                
                    raise KeyError('version not in keyword args')
                    
                    # version increase must be thread-safe
 #                   with self.__version_lock:
 #                       self.__version += 1
 #               else:
 #                   v = kwargs['version']
 #                   if v > self.__version:
 #                       self.__version = v
                    
                return func(*args, **kwargs)
            except Exception, e:
                raise

        return f

    def close(self):
        self.__stage_store.close()    
        self.__store.close()
        # close db last since some of the stores may have indices open using
        # the db-handle
        self.__db.close()        

