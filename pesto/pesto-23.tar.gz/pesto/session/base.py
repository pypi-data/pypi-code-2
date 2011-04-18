# Copyright (c) 2007-2010 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
Web session management.
"""

__docformat__ = 'restructuredtext en'
__all__ = ['session_middleware']

import logging
import os
import random
import re
import threading
from time import sleep, time

from pesto.request import Request
from pesto.response import Response
from pesto.cookie import Cookie
from pesto.wsgiutils import ClosingIterator

def get_session_id_from_querystring(environ):
    """
    Return the session from the query string or None if no session can be read.
    """
    pattern = re.escape(environ['pesto.sessionmanager'].COOKIE_NAME) + '=([0-9a-z]{%d})' % ID_LENGTH
    try:
        return re.search(pattern, environ.get("QUERY_STRING", "")).group(1)
    except AttributeError:
        return None

def get_session_id_from_cookie(environ):
    """
    Return the session from a cookie or None if no session can be read
    """
    cookie = Request(environ).cookies.get(environ['pesto.sessionmanager'].COOKIE_NAME)
    if cookie and is_valid_id(cookie.value):
        return cookie.value
    return None


try:
    import hashlib
    ID_LENGTH = hashlib.sha256().digest_size * 2
    def generate_id():
        """Generate a unique session ID"""
        return hashlib.sha256(
              str(os.getpid())
            + str(time())
            + str(random.random())
        ).hexdigest()

except ImportError:
    import sha
    ID_LENGTH = 40
    def generate_id():
        """Generate a unique session ID"""
        return sha.new(
              str(os.getpid())
            + str(time())
            + str(random.random())
        ).hexdigest()


def is_valid_id(session_id, pattern=re.compile('^[a-f0-9]{%d}$' % ID_LENGTH)):
    """
    Return True if ``session_id`` is a well formed session id. This must be
    a hex string as produced by hashlib objects' ``hexdigest`` method.

    Synopsis::

        >>> is_valid_id('a' * ID_LENGTH)
        True
        >>> is_valid_id('z' * ID_LENGTH)
        False
        >>> is_valid_id('a' * (ID_LENGTH - 1))
        False
    """
    try:
        return pattern.match(session_id) is not None
    except TypeError:
        return False


class Session(object):
    """
    Session objects store information about the http sessions
    """


    # Indicates whether the session is newly created (ie within the current request)
    is_new = True

    def __init__(self, session_manager, session_id, is_new, data=None):
        """
        Create a new session object within the given session manager.
        """

        self.session_manager = session_manager
        self._changed = False
        self.session_id = session_id
        self.is_new = is_new
        self.data = {}

        if data is not None:
            self.data.update(data)

    def save_if_changed(self):
        """
        Save the session in the underlying storage mechanism if the session is
        new or if it has been changed since being loaded.

        Note that this will only detect changes to the session object itself.
        If you store a mutable object within the session and change that
        then you must explicity call ``request.session.save`` to ensure
        your change is saved.

        Return
            ``True`` if the session was saved, or ``False`` if it
            was not necessary to save the session.
        """
        if self._changed or self.is_new:
            self.save()
            self._changed = False
            self.is_new = False
            return True
        return False

    def save(self):
        """
        Saves the session to the underlying storage mechanism.
        """
        self.session_manager.store(self)

    def setdefault(self, key, value=None):
        self._changed = True
        return self.data.setdefault(key, value)

    def pop(self, key, default):
        self._changed = True
        return self.data.pop(key, default)

    def popitem(self):
        self._changed = True
        return self.data.popitem()

    def clear(self):
        self._changed = True
        return self.data.clear()

    def has_key(self, key):
        return self.data.has_key(key)

    def items(self):
        return self.data.items()

    def iteritems(self):
        return self.data.iteritems()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()

    def update(self, other, **kwargs):
        self._changed = True
        return self.data.update(other, **kwargs)

    def values(self):
        return self.data.values()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return self.data.__iter__()

    def invalidate(self):
        """
        invalidate and remove this session from the sessionmanager
        """
        self.session_manager.remove(self.session_id)
        self.session_id = None

    def __setitem__(self, key, val):
        self._changed = True
        return self.data.__setitem__(key, val)

    def __delitem__(self, key):
        self._changed = True
        return self.data.__delitem__(key)

    def text(self):
        """
        Return a useful text representation of the session
        """
        import pprint
        return "<%s id=%s, is_new=%s\n%s\n>" % (
                self.__class__.__name__, self.session_id, self.is_new,
                pprint.pformat(self)
        )

class SessionManagerBase(object):
    """
    Manages Session objects using an ObjectStore to persist the
    sessions.
    """
    # Which version of the pickling protocol to select.
    PICKLE_PROTOCOL = -1

    # Key to use in HTTP cookies
    COOKIE_NAME = "pesto_session"

    def load(self, session_id):
        """
        Load a session object from this sessionmanager.

        Note that if ``session_id`` cannot be found in the underlying storage,
        a new session id will be created.
        """
        self.acquire_lock(session_id)
        try:
            data = self._get_session_data(session_id)
            if data is None:
                # Generate a fresh session with a new id
                session = Session(self, generate_id(), is_new=True, data=data)
            else:
                session = Session(self, session_id, is_new=False, data=data)
            self.update_access_time(session.session_id)
            return session
        finally:
            self.release_lock(session_id)

    def update_access_time(self, session_id):
        raise NotImplementedError

    def get_access_time(self, session_id):
        raise NotImplementedError

    def acquire_lock(self, session_id=None):
        """
        Acquire a lock for the given session_id.

        If session_id is none, then the whole storage should be locked.
        """
        raise NotImplementedError

    def release_lock(self, session_id=None):
        raise NotImplementedError

    def read_session(self, session_id):
        """
        Return a session object from the given ``session_id``. If
        ``session_id`` is None a new session will be generated.

        Synopsis::

            >>> from pesto.session.memorysessionmanager import MemorySessionManager
            >>> sm = MemorySessionManager()
            >>> sm.read_session(None) #doctest: +ELLIPSIS
            <pesto.session.base.Session object at 0x...>

        """
        if session_id is not None:
            session = self.load(session_id)
        else:
            session = Session(self, generate_id(), is_new=True)
        self.update_access_time(session.session_id)
        return session

    def __contains__(self, session_id):
        """
        Return true if the given session id exists in this sessionmanager
        """
        raise NotImplementedError

    def store(self, session):
        """
        Save the given session object in this sessionmanager.
        """
        self.acquire_lock(session.session_id)
        try:
            self._store(session)
        finally:
            self.release_lock(session.session_id)

    def _store(self, session):
        """
        Write session data to the underlying storage.
        Subclasses must implement this method
        """

    def remove(self, session_id):
        """
        Remove the specified session from the session manager.
        """
        self.acquire_lock(session_id)
        try:
            self._remove(session_id)
        finally:
            self.release_lock(session_id)

    def _remove(self, session_id):
        """
        Remove the specified session from the underlying storage.
        Subclasses must implement this method
        """
        raise NotImplementedError

    def _get_session_data(self, session_id):
        """
        Return a dict of the session data from the underlying storage, or
        ``None`` if the session does not exist.
        """
        raise NotImplementedError

    def close(self):
        """
        Close the persistent store cleanly.
        """
        self.acquire_lock()
        try:
            self._close()
        finally:
            self.release_lock()

    def _close(self):
        """
        Default implementation: do nothing
        """

    def purge(self, olderthan=1800):
        for session_id in self._purge_candidates(olderthan):
            self.remove(session_id)

    def _purge_candidates(self, olderthan=1800):
        """
        Return a list of session ids ready to be purged from the session
        manager.
        """
        raise NotImplementedError


class ThreadsafeSessionManagerBase(SessionManagerBase):
    """
    Base class for sessioning to run in a threaded environment.

    DOES NOT GUARANTEE PROCESS-LEVEL SAFETY!
    """

    def __init__(self):
        super(ThreadsafeSessionManagerBase, self).__init__()
        self._access_times = {}
        self._lock = threading.RLock()

    def _purge_candidates(self, olderthan=1800):
        """
        Purge all sessions older than ``olderthan`` seconds.
        """
        # Re-importing time fixes exception raised on interpreter shutdown
        from time import time
        expiry = time() - olderthan
        self.acquire_lock()
        try:
            return [
                id for id, access_time in self._access_times.iteritems() if access_time < expiry
            ]
        finally:
            self.release_lock()

    def acquire_lock(self, session_id=None):
        self._lock.acquire()

    def release_lock(self, session_id=None):
        self._lock.release()

    def update_access_time(self, session_id):
        self.acquire_lock()
        try:
            self._access_times[session_id] = time()
        finally:
            self.release_lock()

    def get_access_time(self, session_id):
        """
        Return the time the given session_id was last accessed
        """
        return self._access_times[session_id]

    def _remove(self, session_id):
        """
        Subclasses should call this implementation to ensure the access_times
        dictionary is kept up to date.
        """
        try:
            del self._access_times[session_id]
        except KeyError:
            logging.warn("tried to remove non-existant session id %r", session_id)

    def __contains__(self, session_id):
        return session_id in self._access_times

def start_thread_purger(sessionmanager, howoften=60, olderthan=1800, lock=threading.Lock()):
    """
    Start a thread to purge sessions older than ``olderthan`` seconds every
    ``howoften`` seconds.
    """

    def _purge():
        while True:
            sleep(howoften)
            sessionmanager.purge(olderthan)

    lock.acquire()
    try:
        if hasattr(sessionmanager, '_purge_thread'):
            # Don't start the thread twice
            return
        sessionmanager._purge_thread = threading.Thread(target=_purge)
        sessionmanager._purge_thread.setDaemon(True)
        sessionmanager._purge_thread.start()

    finally:
        lock.release()

def session_middleware(
    session_manager,
    auto_purge_every=60,
    auto_purge_olderthan=1800,
    persist='cookie',
    cookie_path=None,
    cookie_domain=None
):
    """
    WSGI middleware application for sessioning.

    Synopsis::

        >>> from pesto.session.memorysessionmanager import MemorySessionManager
        >>> def my_wsgi_app(environ, start_response):
        ...     session = environ['pesto.session']
        ... 
        >>> app = session_middleware(MemorySessionManager())(my_wsgi_app)
        >>> 

    session_manager
        An implementation of ``pesto.session.base.SessionManagerBase``

    auto_purge_every
        If non-zero, a separate thread will be launched which will purge
        expired sessions every ``auto_purge_every`` seconds. In a CGI
        environment (or equivalent, detected via, ``environ['wsgi.run_once']``)
        the session manager will be purged after every request.

    auto_purge_olderthan
        Auto purge sessions older than ``auto_purge_olderthan`` seconds.

    persist
        Either ``cookie`` or ``querystring``. If set to ``cookie`` then
        sessions will be automatically persisted via a session cookie.

        If ``querystring`` then the session-id will be read from the
        querystring. However it is up to the underlying application to ensure
        that the session-id is embedded into all links generated by the
        application.

    cookie_path
        The path to use when setting cookies. If ``None`` this will be taken
        from the ``SCRIPT_NAME`` variable.

    cookie_domain
        The domain to use when setting cookies. If ``None`` this will not be
        set and the browser will default to the domain used for the request.
    """

    get_session_id = {
        'cookie': get_session_id_from_cookie,
        'querystring': get_session_id_from_querystring,
    }[persist]

    def middleware(app):

        def sessionmanager_middleware(environ, start_response):

            if environ['wsgi.run_once'] and auto_purge_every > 0:
                session_manager.purge(auto_purge_olderthan)

            environ['pesto.sessionmanager'] = session_manager
            session = session_manager.read_session(get_session_id(environ))
            environ['pesto.session'] = session

            my_start_response = start_response

            if persist == 'cookie' and session.is_new:
                def my_start_response(status, headers, exc_info=None):
                    _cookie_path = cookie_path
                    if _cookie_path is None:
                        _cookie_path = environ.get('SCRIPT_NAME')
                    if not _cookie_path:
                        _cookie_path = '/'
                    cookie = Cookie(
                        session_manager.COOKIE_NAME,
                        session.session_id,
                        path=_cookie_path,
                        domain=cookie_domain,
                        http_only=True
                    )
                    return start_response(
                        status,
                        list(headers) + [("Set-Cookie", str(cookie))],
                        exc_info
                    )

            elif persist == 'querystring':
                request = Request(environ)
                if session.is_new and environ['REQUEST_METHOD'] == 'GET':
                    query_session_id = request.query.get(session_manager.COOKIE_NAME)
                    if query_session_id != session.session_id:
                        new_query = [
                            item for item in request.query.iterallitems()
                            if item[0] != session_manager.COOKIE_NAME
                        ]
                        new_query.append((session_manager.COOKIE_NAME, session.session_id))
                        return ClosingIterator(
                            Response.redirect(
                                request.make_uri(query=new_query)
                            )(environ, my_start_response),
                            session.save_if_changed
                        )

            return ClosingIterator(app(environ, my_start_response), session.save_if_changed)

        if auto_purge_every > 0:
            start_thread_purger(
                session_manager,
                howoften = auto_purge_every,
                olderthan = auto_purge_olderthan
            )


        return sessionmanager_middleware

    return middleware


