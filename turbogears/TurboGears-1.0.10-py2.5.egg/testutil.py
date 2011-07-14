import Cookie
import cStringIO as StringIO
import logging
import os
import string
import types
import unittest

import cherrypy
from cherrypy import _cphttptools

try:
    import sqlobject
    from sqlobject.inheritance import InheritableSQLObject
except ImportError:
    sqlobject = None
try:
    import sqlalchemy
except ImportError:
    sqlalchemy = None

from turbogears import startup, config, update_config, \
    controllers, database, validators
from turbogears.identity import current_provider
from turbogears.util import get_model

# For clean tests, remove all compiled Kid templates
for w in os.walk('.'):
    if not os.sep + '.' in w[0]:
        for f in w[2]:
            if f.endswith('.kid'):
                f = os.path.join(w[0], f[:-3] + 'pyc')
                if os.path.exists(f):
                    os.remove(f)

# Load test configuration
if os.path.exists('test.cfg'):
    # Look for a 'config' package
    for dirpath, dirs, dummy2 in os.walk('.'):
        basename = os.path.basename(dirpath)
        dirname = os.path.basename(os.path.dirname(dirpath))
        init_py = os.path.join(dirpath, '__init__.py')
        if basename == 'config' and dirname[0] in string.ascii_letters + '_' \
                and os.path.exists(init_py):
            modulename = "%s.app" % dirpath[2:].replace(os.sep, ".")
            break
    else:
        modulename = None
    # XXX This is a temporary workaround, the code above to find the config
    # package should really be improved and moved elsewhere.
    # See http://trac.turbogears.org/ticket/2043
    try:
        update_config(configfile="test.cfg", modulename=modulename)
    except ImportError, exc:
        import warnings
        warnings.warn("Could not import configuration from module: %s" % exc,
            RuntimeWarning)
        update_config(configfile="test.cfg", modulename=None)
else:
    database.set_db_uri("sqlite:///:memory:")

config.update({'global':
        {'autoreload.on': False, 'tg.new_style_logging': True}})


def start_cp():
    if not config.get("cherrypy_started", False):
        cherrypy.server.start(serverClass=None, initOnly=True)
        config.update({"cherrypy_started" : True})


test_user = None

def set_identity_user(user):
    """Setup a user for configuring request's identity."""
    global test_user
    test_user = user


def attach_identity(req):
    if config.get("identity.on", False):
        req.identity = (test_user
            and current_provider.authenticated_identity(test_user)
            or current_provider.anonymous_identity())


def create_request(request, method="GET", protocol="HTTP/1.1",
        headers={}, rfile=None, clientAddress="127.0.0.1",
        remoteHost="localhost", scheme="http"):
    start_cp()
    if not rfile:
        rfile = StringIO.StringIO("")
    if type(headers) != dict:
        headerList = headers
    else:
        headerList = [(key, value) for key, value in headers.items()]
    headerList.append(("Host", "localhost"))
    if not hasattr(cherrypy.root, "started"):
        startup.startTurboGears()
        cherrypy.root.started = True
    req = _cphttptools.Request(clientAddress, 80, remoteHost, scheme)
    cherrypy.serving.request = req
    attach_identity(req)
    cherrypy.serving.response = _cphttptools.Response()
    req.run(" ".join((method, request, protocol)), headerList, rfile)

createRequest = create_request # deprecated


class BrowsingSession(object):

    def __init__(self):
        self.visit = None
        self.response, self.status = None, None
        self.cookie = Cookie.SimpleCookie()

    def goto(self, *args, **kwargs):
        if self.cookie:
            headers = kwargs.setdefault('headers', {})
            headers['Cookie'] = self.cookie.output()
        create_request(*args, **kwargs)
        # If we were given an encoding in the content type we should use it to
        # decode the response:
        ctype_parts = cherrypy.response.headers['Content-Type'].split(';')
        for parameter in ctype_parts[1:]:
            attribute, value = parameter.strip().split('=')
            try:
                self.unicode_response = cherrypy.response.body[0].decode(value)
                break
            except:
                # If the named encoding doesn't work then it doesn't work.  We
                # just won't create the unicode_response field.
                pass
        self.response = cherrypy.response.body[0]
        self.status = cherrypy.response.status
        if cherrypy.response.simple_cookie:
            self.cookie.update(cherrypy.response.simple_cookie)


def _return_directly(output, *args):
    return output


class DummySession:
    session_storage = dict
    to_be_loaded = None


class DummyRequest(_cphttptools.Request):
    """A very simple dummy request."""

    remote_host = "127.0.0.1"

    def __init__(self, method='GET', path='/', headers=None):
        super(DummyRequest, self).__init__("127.0.0.1", "4711", "127.0.0.1")
        self.headers = headers or {}
        self.method = method
        self.path = path
        self.path_info = ''
        self.query_string = ''
        self.base = ''
        self.params = {}
        self.object_trail = []
        self._session = DummySession()

    def purge__(self):
        pass


def call(method, *args, **kw):
    start_cp()
    output, response = call_with_request(method, DummyRequest(), *args, **kw)
    return output


def call_with_request(method, request, *args, **kw):
    """More fine-grained version of call method.

    This allows using request/response.

    """
    orig_proc_output = controllers._process_output
    controllers._process_output = _return_directly
    cherrypy.serving.response = _cphttptools.Response()
    cherrypy.serving.response.version = "1.1"
    cherrypy.serving.request = request
    if not hasattr(request, "identity"):
        attach_identity(request)
    output = None
    try:
        output = method(*args, **kw)
    finally:
        del cherrypy.serving.request
        controllers._process_output = orig_proc_output
    response = cherrypy.serving.response
    return output, response


class DBTest(unittest.TestCase):

    model = None

    def _get_soClasses(self):
        try:
            return [self.model.__dict__[x] for x in self.model.soClasses]
        except AttributeError:
            return self.model.__dict__.values()

    def setUp(self):
        if not self.model:
            self.model = get_model()
            if not self.model:
                raise "Unable to run database tests without a model"


        # list of constraints we will collect
        constraints = list()

        for item in self._get_soClasses():
            if isinstance(item, types.TypeType) and issubclass(item,
                sqlobject.SQLObject) and item != sqlobject.SQLObject \
                and item != InheritableSQLObject:
                # create table without applying constraints, collect
                # all the constaints for later creation.
                # see http://sqlobject.org/FAQ.html#mutually-referencing-tables
                # for more info
                collected_constraints = item.createTable(ifNotExists=True,
                        applyConstraints=False)

                if collected_constraints:
                    constraints.extend(collected_constraints)

        # now that all tables are created, add the constaints we collected
        for postponed_constraint in constraints:
            # item is the last processed item and we borrow its connection
            item._connection.query(postponed_constraint)


    def tearDown(self):
        database.rollback_all()
        for item in self._get_soClasses()[::-1]:
            if isinstance(item, types.TypeType) and issubclass(item,
                sqlobject.SQLObject) and item != sqlobject.SQLObject \
                and item != InheritableSQLObject:
                item.dropTable(ifExists=True)


def reset_cp():
    cherrypy.root = None


def catch_validation_errors(widget, value):
    """Catch and unpack validation errors (for testing purposes)."""
    try:
        value = widget.validate(value)
    except validators.Invalid, errors:
        try:
            errors = errors.unpack_errors()
        except AttributeError:
            pass
    else:
        errors = {}
    return value, errors


class MemoryListHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self, level=logging.DEBUG)
        self.log = []

    def emit(self, record):
        print "Got record: %s" % record
        print "formatted as: %s" % self.format(record)
        self.log.append(self.format(record))

    def print_log(self):
        print "\n".join(self.log)
        self.log = []

    def get_log(self):
        log = self.log
        self.log = []
        return log

_memhandler = MemoryListHandler()


_currentcat = None


def capture_log(category):
    """Capture log for one category.

    The category can either be a single category (a string like 'foo.bar')
    or a list of them. You *must* call print_log() to reset when you're done.

    """
    global _currentcat
    assert not _currentcat
    if not isinstance(category, list) and not isinstance(category, tuple):
        category = [category]
    _currentcat = category
    for cat in category:
        log = logging.getLogger(cat)
        log.setLevel(logging.DEBUG)
        log.addHandler(_memhandler)


def _reset_logging():
    """Manage the resetting of the loggers."""
    global _currentcat
    if not _currentcat:
        return
    for cat in _currentcat:
        log = logging.getLogger(cat)
        log.removeHandler(_memhandler)
    _currentcat = None


def print_log():
    """Print the log captured by capture_log to stdout.

    Resets that log and resets the temporarily added handlers.

    """
    _reset_logging()
    _memhandler.print_log()


def get_log():
    """Return the list of log messages captured by capture_log.

    Resets that log and resets the temporarily added handlers.

    """
    _reset_logging()
    return _memhandler.get_log()


def sqlalchemy_cleanup():
    database.metadata.clear()
    try:
        database.metadata.dispose()
    except AttributeError: # not threadlocal
        if database.metadata.bind:
            database.metadata.bind.dispose()
    database._engine = None
    if database.mapper == database.session.mapper:
        # the following does not work for SA < 0.4
        sqlalchemy.orm.clear_mappers()


__all__ = ["call", "create_request", "createRequest", "DBTest",
    "attach_identity", "set_identity_user",
    "capture_log", "print_log", "get_log", "sqlalchemy_cleanup"]
