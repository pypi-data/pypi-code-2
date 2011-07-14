"""Things to do when the TurboGears server is started."""

__all__ = [
    'call_on_startup',
    'call_on_shutdown',
    'reloader_thread',
    'start_bonjour',
    'stop_bonjour',
    'start_server',
    'startTurboGears',
    'stopTurboGears',
    'webpath',
]

import atexit
import errno
import logging
import os
import sys
import signal
import time

from os.path import abspath, exists

import pkg_resources
import cherrypy
from cherrypy import _cputil, request, server
from cherrypy._cpwsgi import wsgiApp, CPHTTPRequest
from cherrypy._cpwsgiserver import CherryPyWSGIServer

pkg_resources.require("TurboGears")

from turbogears import config, database, scheduler, view
from turbogears.database import hub_registry, EndTransactionsFilter
from turbogears.filters import (MonkeyDecodingFilter, NestedVariablesFilter,
    SafeMultipartFilter, VirtualPathFilter)


# module globals
DNS_SD_PID = None
call_on_startup = []
call_on_shutdown = []
webpath = ''
log = logging.getLogger("turbogears.startup")


# module private functions
def reloader_thread(freq):
    """Monkeypatch for the reloader provided by CherryPy.

    This reloader is designed to reload a single package. This is
    more efficient and, more important, compatible with zipped
    libraries that may not provide access to the individual files."""

    def archive_selector(module):
        if hasattr(module, '__loader__'):
            if hasattr(module.__loader__, 'archive'):
                return module.__loader__.archive
        return module

    mtimes = {}
    package = config.get("autoreload.package", None)
    if package is None:
        print ("TurboGears requires autoreload.package to be set. "
            "It can be an empty value, which will use CherryPy's default "
            "behavior which is to check every module. Setting an actual "
            "package makes the check much faster.")
        return
    while cherrypy.lib.autoreload.RUN_RELOADER:
        if package:
            modnames = filter(lambda modname: modname.startswith(package),
                                sys.modules.keys())
            modlist = [sys.modules[modname] for modname in modnames]
        else:
            modlist = map(archive_selector, sys.modules.values())
        for filename in filter(lambda v: v,
                map(lambda m: getattr(m, "__file__", None), modlist)):
            if filename.endswith(".kid") or filename == "<string>":
                continue
            orig_filename = filename
            if filename.endswith(".pyc"):
                filename = filename[:-1]
            try:
                mtime = os.stat(filename).st_mtime
            except OSError, e:
                if orig_filename.endswith('.pyc') and e[0] == errno.ENOENT:
                    # This prevents us from endlessly restarting
                    # if there is an old .pyc lying around
                    # after a .py file has been deleted
                    try: os.unlink(orig_filename)
                    except: pass
                sys.exit(3) # force reload
            if filename not in mtimes:
                mtimes[filename] = mtime
                continue
            if mtime > mtimes[filename]:
                sys.exit(3) # force reload
        time.sleep(freq)

cherrypy.lib.autoreload.reloader_thread = reloader_thread

old_object_trail = _cputil.get_object_trail

# hang on to object trail to use it to find an app root if need be
def get_object_trail(object_path=None):
    trail = old_object_trail(object_path)
    try:
        request.object_trail = trail
    except AttributeError:
        pass
    return trail

_cputil.get_object_trail = get_object_trail


# module public functions
def start_bonjour(package=None):
    """Register the TurboGears server with the Bonjour framework.

    Currently only Unix-like systems are supported where either the 'avahi'
    daemon (Linux etc.) is available or the 'dns-sd' program (Mac OS X).

    """
    global DNS_SD_PID
    if DNS_SD_PID:
        return
    if not getattr(cherrypy, 'root', None):
        return
    if not package:
        package = cherrypy.root.__module__
        package = package[:package.find('.')]

    host = config.get('server.socket_host', '')
    port = str(config.get('server.socket_port'))
    env = config.get('server.environment')
    name = package + ": " + env
    type = "_http._tcp"

    cmds = [['/usr/bin/avahi-publish-service', ["-H", host, name, type, port]],
            ['/usr/bin/dns-sd', ['-R', name, type, "."+host, port, "path=/"]]]

    for cmd, args in cmds:
        # TODO:. This check is flawed.  If one has both services installed and
        # avahi isn't the one running, then this won't work.  We should either
        # try registering with both or checking what service is running and use
        # that.  Program availability on the filesystem was never enough...
        if exists(cmd):
            DNS_SD_PID = os.spawnv(os.P_NOWAIT, cmd, [cmd]+args)
            atexit.register(stop_bonjour)
            break

def stop_bonjour():
    """Stop the bonjour publishing daemon if it is running."""
    if not DNS_SD_PID:
        return
    try:
        os.kill(DNS_SD_PID, signal.SIGTERM)
    except OSError:
        pass

def startTurboGears():
    """Handles TurboGears tasks when the CherryPy server starts.

    This performs the following initialization tasks (in given order):

    * Turns off CherryPy's logging filter when in development mode
    * If logging is not already set up, turns on old-style stdlib logging.
    * Adds a static filter for TurboGears's static files (URL '/tg_static').
    * Adds a static filter for TurboGears's JavaScript files (URL '/tg_js').
    * Loads the template engines and the base templates.
    * Adds the CherryPy request filters to the root controller.
    * Adds the decoding filter to the root URL ('/') if enabled in the
      configuration.
    * Registers the server with the Bonjour framework, if available.
    * Calls 'turbogears.database.bind_metadata' when using SQLAlchemy.
    * Loads all turbogears.extensions entry points and calls their
      'start_extension' method.
    * Calls the callables registered in 'turbogears.call_on_startup'.
    * Starts the TurboGears scheduler.

    """
    global webpath
    conf = config.get
    rfn = pkg_resources.resource_filename

    cherrypy.config.environments['development'][
        'log_debug_info_filter.on'] = False

    # XXX: obsolete --> to be removed
    # Set up old-style logging
    if not conf('tg.new_style_logging', False):
        if conf('server.log_to_screen'):
            setuplog = logging.getLogger()
            setuplog.setLevel(logging.DEBUG)
            fmt = logging.Formatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s")
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(fmt)
            setuplog.addHandler(handler)

        logfile = conf('server.log_file')
        if logfile:
            setuplog = logging.getLogger('turbogears.access')
            setuplog.propagate = 0
            fmt = logging.Formatter("%(message)s")
            handler = logging.FileHandler(logfile)
            handler.setLevel(logging.INFO)
            handler.setFormatter(fmt)
            setuplog.addHandler(handler)

    # Add static filters
    config.update({'/tg_static': {
        'static_filter.on': True,
        'static_filter.dir': abspath(rfn(__name__, 'static')),
        'log_debug_info_filter.on': False,
    }})
    config.update({'/tg_js': {
        'static_filter.on': True,
        'static_filter.dir': abspath(rfn(__name__, 'static/js')),
        'log_debug_info_filter.on': False,
    }})
    # Add decoding filter
    if conf('decoding_filter.on', path='/') is None:
        config.update({'/': {
            'decoding_filter.on': True,
            'decoding_filter.encoding': conf('kid.encoding', 'utf8')
        }})

    # Initialize template engines and load base templates
    view.load_engines()
    view.loadBaseTemplates()

    # Add request filters
    webpath = conf('server.webpath') or ''

    if getattr(cherrypy, 'root', None):
        if not hasattr(cherrypy.root, '_cp_filters'):
            cherrypy.root._cp_filters = []
        extra_filters = [
            VirtualPathFilter(webpath),
            EndTransactionsFilter(),
            NestedVariablesFilter(),
            SafeMultipartFilter()
        ]
        # Do not add filters twice which are already present
        for cp_filter in cherrypy.root._cp_filters[:]:
            for candidate in extra_filters:
                if candidate.__class__ is cp_filter.__class__:
                    extra_filters.remove(candidate)
                    break
        cherrypy.root._cp_filters.extend(extra_filters)

    # Monkey patch CherryPy Decoding filter: injects our replacement filter
    # MonkeyDecodingFilter into the CherryPy filter chain
    decoding_filter = MonkeyDecodingFilter()
    for index, active_filter in enumerate(
            cherrypy.filters._filterhooks.get('before_main', [])):
        if (active_filter.im_class is
                cherrypy.filters.decodingfilter.DecodingFilter):
            cherrypy.filters._filterhooks['before_main'].pop(index)
            if conf('decoding_filter.on', False, path='/'):
                log.info("Request decoding filter activated.")
                cherrypy.filters._filterhooks['before_main'].insert(
                        index, decoding_filter.before_main)


    webpath = webpath.lstrip('/')
    if webpath and not webpath.endswith('/'):
        webpath += '/'

    # Register server with Bonjour framework
    bonjoursetting = conf('tg.bonjour', None)
    if bonjoursetting or conf('server.environment') == 'development':
        start_bonjour(bonjoursetting)

    # Bind metadata for SQLAlchemy
    if conf('sqlalchemy.dburi'):
        database.bind_metadata()

    # Start all TurboGears extensions
    extensions = pkg_resources.iter_entry_points('turbogears.extensions')
    for entrypoint in extensions:
        # We try to load the extension and run its 'start_extension'
        # method ,if present. If either fails, we simply log the exception and
        # continue, because a) when the autoreloader is active, unhandled
        # exceptions in the startup phase will not stop the server and
        # b) faulty extensions (which may be from a different package)
        # should not crash the server.
        try:
            ext = entrypoint.load()
        except Exception, e:
            log.exception("Error loading TurboGears extension plugin '%s': %s",
                entrypoint, e)
            continue
        if hasattr(ext, 'start_extension'):
            try:
                ext.start_extension()
            except Exception, e:
                log.exception("Error starting TurboGears extension '%s': %s",
                    entrypoint, e)

    # Call registered startup functions
    for item in call_on_startup:
        item()

    # Start the scheduler
    if conf('tg.scheduler', False):
        scheduler._start_scheduler()
        log.info("Scheduler started")

def stopTurboGears():
    """Handles TurboGears tasks when the CherryPy server stops.

    Ends all open database transactions, shuts down all extensions, calls user
    provided shutdown functions and stops the scheduler.

    """
    # end all transactions and clear out the hubs to
    # help ensure proper reloading in autoreload situations
    for hub in hub_registry:
        hub.end()
    hub_registry.clear()

    stop_bonjour()

    # Shut down all TurboGears extensions
    extensions= pkg_resources.iter_entry_points( "turbogears.extensions" )
    for entrypoint in extensions:
        try:
            ext = entrypoint.load()
        except Exception, e:
            log.exception("Error loading TurboGears extension plugin '%s': %s",
                entrypoint, e)
            continue
        if hasattr(ext, "shutdown_extension"):
            try:
                ext.shutdown_extension()
            except Exception, e:
                log.exception(
                    "Error shutting down TurboGears extension '%s': %s",
                    entrypoint, e)

    for item in call_on_shutdown:
        item()

    if config.get("tg.scheduler", False):
        scheduler._stop_scheduler()
        log.info("Scheduler stopped")

def start_server(root):
    cherrypy.tree.mount(root)
    if config.get('tg.fancy_exception', False):
        server.start(server=SimpleWSGIServer())
    else:
        server.start()

# module classes
class SimpleWSGIServer(CherryPyWSGIServer):
    """A WSGI server that accepts a WSGI application as a parameter."""
    RequestHandlerClass = CPHTTPRequest

    def __init__(self):
        conf = cherrypy.config.get
        wsgi_app = wsgiApp
        if conf('server.environment') == 'development':
            try:
                from paste.evalexception.middleware import EvalException
            except ImportError:
                pass
            else:
                wsgi_app = EvalException(wsgi_app, global_conf={})
                cherrypy.config.update({'server.throw_errors':True})
        bind_addr = (conf('server.socket_host'), conf('server.socket_port'))
        CherryPyWSGIServer.__init__(self, bind_addr, wsgi_app,
            conf("server.thread_pool"), conf("server.socket_host"),
            request_queue_size = conf("server.socket_queue_size"))


if startTurboGears not in server.on_start_server_list:
    server.on_start_server_list.append(startTurboGears)

if stopTurboGears not in server.on_stop_server_list:
    server.on_stop_server_list.append(stopTurboGears)
