# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, os, time
from base64 import urlsafe_b64decode as decode, urlsafe_b64encode as encode

from stellaris.utils import Property

log = logging.getLogger('stellaris')

# Caching protocol to be used if the object wants to implement caching
# functionality.

# - Implement a method load() which returns the object to be cached
# For a disk-based graph, this could take the graph from disk and return
# a representation of it to be used for the cache

class CacheEntryNotFound(Exception): pass

class Cache(object):
    """
    Implements the LRU caching strategy for any objects.
    """
    
    def __init__(self, size=1000):
        """
        Creates a cache instance with place for ``size`` objects.
        
        ``store`` - an instance of the store which the cache is for. The 
                    instance must implement a load(key)-method which returns
                    the item stored under the name key.
        ``size`` - indicates the max number of objects kept in the cache
        """
        self._size = size
        self._cache = {}
        #self._store = store
        self._lru = {}

    def __setitem__(self, key, value):
        if not len(self._cache) > self._size:
            self._cache[key] = value
            return
        
        # find the element to kick out, O(N)
        lru_key, val = min(self._lru.items(), key=lambda a: a[1])
        try:
            del self._cache[lru_key]
        except KeyError, e:
            # this is ok, the key is not in the cache
            pass
            
        self._cache[key] = value
        self._lru[key] = time.time()

    def __getitem__(self, key):
        try:
            self._lru[key] = time.time()
            return self._cache[key]
        except KeyError, e:
#            graph = self._store.load(key)
#            self[key] = graph
#            return graph
            raise CacheEntryNotFound(key)

    def __delitem__(self, key):
        del self._lru[key]
        del self._cache[key]            
