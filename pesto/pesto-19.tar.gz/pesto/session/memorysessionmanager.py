# Copyright (c) 2007-2010 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
pesto.session.memorysessionmanager
-----------------------------------

Store request sessions in memory

Usage::

    >>> from pesto.session import session_middleware
    >>> from pesto.session.memorysessionmanager import MemorySessionManager
    >>> def my_app(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/html')])
    ...     yield "<html>Whoa nelly!</html>"
    ...
    >>> manager = MemorySessionManager()
    >>> app = session_middleware(manager)(my_app)


"""

__docformat__ = 'restructuredtext en'
__all__ = ['MemorySessionManager']

from pesto.session.base import ThreadsafeSessionManagerBase
from pesto.lrucache import LRUCache

class MemorySessionManager(ThreadsafeSessionManagerBase):
    """
    An in-memory session manager.

    Synopsis::

        >>> from pesto.session import session_middleware
        >>> from pesto.session.memorysessionmanager import MemorySessionManager
        >>> manager = MemorySessionManager()
        >>> def app(environ, start_response):
        ...     "WSGI application code here"
        ...
        >>> app = session_middleware(manager)(app)
        >>>
    """

    def __init__(self, cache_size=200):
        """
        cache_size
            The maximum number of session objects to store. If zero this will
            be unlimited, otherwise, a least recently used cache mechanism
            will be used to store only up to ``cache_size`` objects.
        """

        super(MemorySessionManager, self).__init__()

        if cache_size == 0:
            self._cache = {}
        else:
            self._cache = LRUCache(cache_size, purge_listener=self._lru_overflow)

    def _store(self, session):
        """
        Store session ``session``.
        """
        self._cache[session.session_id] = session.data

    def _get_session_data(self, session_id):
        """
        Retrieve session identified by ``session_id``.
        """
        return self._cache.get(session_id, None)

    def _remove(self, session_id):
        try:
            super(MemorySessionManager, self)._remove(session_id)
            del self._cache[session_id]
        except KeyError:
            pass

    def __contains__(self, session_id):
        return session_id in self._cache

    def _lru_overflow(self, sessions):
        """
        Called when the LRUCache overflows and discards sessions
        """
        import logging
        logging.warn(
            "MemorySessionManager: "
            "d session(s) prematurely removed due to cache overflow",
            len(sessions)
        )


