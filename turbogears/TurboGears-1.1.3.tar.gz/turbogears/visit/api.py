# -*- coding: UTF-8 -*-
"""Base API of the TurboGears Visit Framework."""

__all__ = [
    'BaseVisitManager',
    'Visit',
    'VisitFilter',
    'create_extension_model',
    'current',
    'enable_visit_plugin',
    'set_current',
    'start_extension',
    'shutdown_extension',
]


import logging
try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1
import threading
import time

from random import random
from datetime import timedelta, datetime

import cherrypy
import pkg_resources

from cherrypy.filters.basefilter import BaseFilter
from turbogears import config
from turbogears.util import load_class

log = logging.getLogger("turbogears.visit")

# Global VisitManager
_manager = None

# Global list of plugins for the Visit Tracking framework
_plugins = list()

# Accessor functions for getting and setting the current visit information.
def current():
    """Retrieve the current visit record from the cherrypy request."""
    return getattr(cherrypy.request, "tg_visit", None)

def set_current(visit):
    """Set the current visit record on the cherrypy request being processed."""
    cherrypy.request.tg_visit = visit

def _create_visit_manager(timeout):
    """Create a VisitManager based on the plugin specified in the config file."""
    plugin_name = config.get("visit.manager", "sqlalchemy")
    plugins = pkg_resources.iter_entry_points(
        "turbogears.visit.manager", plugin_name)
    log.debug("Loading visit manager from plugin: %s", plugin_name)
    provider_class = None
    for entrypoint in plugins:
        try:
            provider_class = entrypoint.load()
            break
        except ImportError, e:
            log.error("Error loading visit plugin '%s': %s", entrypoint, e)

    if not provider_class and '.' in plugin_name:
        try:
            provider_class = load_class(plugin_name)
        except ImportError, e:
            log.error("Error loading visit class '%s': %s", plugin_name, e)
    if not provider_class:
        raise RuntimeError("VisitManager plugin missing: %s" % plugin_name)
    return provider_class(timeout)


# Interface for the TurboGears extension

def start_extension():
    global _manager

    # Bail out if the application hasn't enabled this extension
    if not config.get("visit.on", False):
        return

    # Bail out if this extension is already running
    if _manager:
        log.warning("Visit manager already running.")
        return

    # How long may the visit be idle before a new visit ID is assigned?
    # The default is 20 minutes.
    timeout = timedelta(minutes=config.get("visit.timeout", 20))
    log.info("Visit Tracking starting (timeout = %i sec).", timeout.seconds)
    # Create the thread that manages updating the visits
    _manager = _create_visit_manager(timeout)

    visit_filter = VisitFilter()
    # Install Filter into the root filter chain
    if not hasattr(cherrypy.root, "_cp_filters"):
        cherrypy.root._cp_filters = list()
    if not visit_filter in cherrypy.root._cp_filters:
        cherrypy.root._cp_filters.append(visit_filter)

def shutdown_extension():
    # Bail out if this extension is not running.
    global _manager
    if not _manager:
        return
    log.info("Visit Tracking shutting down.")
    _manager.shutdown()
    _manager = None

def create_extension_model():
    """Create the data model of the VisitManager if one exists."""
    if _manager:
        _manager.create_model()

def enable_visit_plugin(plugin):
    """Register a visit tracking plugin.

    These plugins will be called for each request.

    """
    _plugins.append(plugin)


class Visit(object):
    """Basic container for visit related data."""

    def __init__(self, key, is_new):
        self.key = key
        self.is_new = is_new


class VisitFilter(BaseFilter):
    """A filter that automatically tracks visitors."""

    def __init__(self):
        get = config.get
        # Where to look for the session key in the request and in which order
        self.source = [s.strip().lower() for s in
            get("visit.source", "cookie").split(',')]
        if set(self.source).difference(('cookie', 'form')):
            log.warning("Unsupported 'visit.source' '%s' in configuration.")
        # Get the name to use for the identity cookie.
        self.cookie_name = get("visit.cookie.name", "tg-visit")
        # and the name of the request param. MUST NOT contain dashes or dots,
        # otherwise the NestedVariablesFilter will choke on it.
        self.visit_key_param = get("visit.form.name", "tg_visit")
        # TODO: The path should probably default to whatever
        # the root is masquerading as in the event of a
        # virtual path filter.
        self.cookie_path = get("visit.cookie.path", "/")
        # The secure bit should be set for HTTPS only sites
        self.cookie_secure = get("visit.cookie.secure", False)
        # By default, I don't specify the cookie domain.
        self.cookie_domain = get("visit.cookie.domain", None)
        assert self.cookie_domain != "localhost", "localhost" \
            " is not a valid value for visit.cookie.domain. Try None instead."
        # Use max age only if the cookie shall explicitly be permanent
        self.cookie_max_age = get("visit.cookie.permanent",
            False) and int(get("visit.timeout", "20")) * 60 or None
        log.info("Visit filter initialized")

    def before_main(self):
        """Check whether submitted request belongs to an existing visit."""
        if not config.get("visit.on", True):
            set_current(None)
            return
        visit = current()
        if not visit:
            visit_key = None
            for source in self.source:
                if source == 'cookie':
                    visit_key = cherrypy.request.simple_cookie.get(
                        self.cookie_name)
                    if visit_key:
                        visit_key = visit_key.value
                        log.debug("Retrieved visit key '%s' from cookie '%s'.",
                            visit_key, self.cookie_name)
                elif source == 'form':
                    visit_key = cherrypy.request.params.pop(
                        self.visit_key_param, None)
                    log.debug(
                        "Retrieved visit key '%s' from request param '%s'.",
                            visit_key, self.visit_key_param)
                if visit_key:
                    visit = _manager.visit_for_key(visit_key)
                    break
            if visit:
                log.debug("Using visit from request with key: %s", visit_key)
            else:
                visit_key = self._generate_key()
                visit = _manager.new_visit_with_key(visit_key)
                log.debug("Created new visit with key: %s", visit_key)
            self.send_cookie(visit_key)
            set_current(visit)
        # Inform all the plugins that a request has been made for the current
        # visit. This gives plugins the opportunity to track click-path or
        # retrieve the visitor's identity.
        try:
            for plugin in _plugins:
                plugin.record_request(visit)
        except cherrypy.InternalRedirect, e:
            # Can't allow an InternalRedirect here because CherryPy is dumb,
            # instead change cherrypy.request.object_path to the url desired.
            cherrypy.request.object_path = e.path

    @staticmethod
    def _generate_key():
        """Return a (pseudo)random hash based on seed."""
        # Adding remoteHost and remotePort doesn't make this any more secure,
        # but it makes people feel secure... It's not like I check to make
        # certain you're actually making requests from that host and port. So
        # it's basically more noise.
        key_string = '%s%s%s%s' % (random(), datetime.now(),
            cherrypy.request.remote_host, cherrypy.request.remote_port)
        return sha1(key_string).hexdigest()

    def clear_cookie(self):
        """Clear any existing visit ID cookie."""
        cookies = cherrypy.response.simple_cookie
        # clear the cookie
        log.debug("Clearing visit ID cookie")
        cookies[self.cookie_name] = ''
        cookies[self.cookie_name]['path'] = self.cookie_path
        cookies[self.cookie_name]['expires'] = ''
        cookies[self.cookie_name]['max-age'] = 0

    def send_cookie(self, visit_key):
        """Send an visit ID cookie back to the browser."""
        cookies = cherrypy.response.simple_cookie
        cookies[self.cookie_name] = visit_key
        cookies[self.cookie_name]['path'] = self.cookie_path
        if self.cookie_secure:
            cookies[self.cookie_name]['secure'] = True
        if self.cookie_domain:
            cookies[self.cookie_name]['domain'] = self.cookie_domain
        max_age = self.cookie_max_age
        if max_age:
            # use 'expires' because MSIE ignores 'max-age'
            cookies[self.cookie_name]['expires'] = '"%s"' % time.strftime(
                "%a, %d-%b-%Y %H:%M:%S GMT",
                time.gmtime(time.time() + max_age))
            # 'max-age' takes precedence on standard conformant browsers
            # (this is better because it has no time sync issues)
            cookies[self.cookie_name]['max-age'] = max_age
        log.debug("Sending visit ID cookie: %s",
            cookies[self.cookie_name].output())


class BaseVisitManager(threading.Thread):

    def __init__(self, timeout):
        super(BaseVisitManager, self).__init__(name="VisitManager")
        self.timeout = timeout
        self.queue = dict()
        self.lock = threading.Lock()
        self._shutdown = threading.Event()
        self.interval = config.get('visit.interval', 30) # seconds
        # We must create the visit model before the manager thread is started.
        self.create_model()
        self.setDaemon(True)
        self.start()

    def create_model(self):
        pass

    def new_visit_with_key(self, visit_key):
        """Return a new Visit object with the given key."""
        raise NotImplementedError

    def visit_for_key(self, visit_key):
        """Return the visit for this key.

        Return None if the visit doesn't exist or has expired.

        """
        raise NotImplementedError

    def update_queued_visits(self, queue):
        """Extend the expiration of the queued visits."""
        raise NotImplementedError

    def update_visit(self, visit_key, expiry):
        try:
            self.lock.acquire()
            self.queue[visit_key] = expiry
        finally:
            self.lock.release()

    def shutdown(self, timeout=None):
        try:
            self.lock.acquire()
            self._shutdown.set()
            self.join(timeout)
        finally:
            self.lock.release()
        if self.isAlive():
            log.error("Visit Manager thread failed to shutdown.")

    def run(self):
        while not self._shutdown.isSet():
            self.lock.acquire()
            if self._shutdown.isSet():
                self.lock.release()
                continue
            queue = None
            try:
                # make a copy of the queue and empty the original
                if self.queue:
                    queue = self.queue.copy()
                    self.queue.clear()
                if queue is not None:
                    self.update_queued_visits(queue)
            finally:
                self.lock.release()
            self._shutdown.wait(self.interval)
