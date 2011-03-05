from cStringIO import StringIO
import datetime
import gzip
import os
import re
import sys
import traceback
import urllib
import urllib2

from pylons import config
from webob import Request, Response
try:
    import json
except ImportError:
    import simplejson as json

__version__ = '0.1.0'

EXCEPTIONAL_PROTOCOL_VERSION = 6
EXCEPTIONAL_API_ENDPOINT = "http://api.getexceptional.com/api/errors"

def memoize(func):
    """A simple memoize decorator (with no support for keyword arguments)."""

    cache = {}
    def wrapper(*args):
        if args in cache:
            return cache[args]
        cache[args] = value = func(*args)
        return value

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    if hasattr(func, '__module__'):
        wrapper.__module__ = func.__module__
    wrapper.clear = cache.clear

    return wrapper


class ExceptionalMiddleware(object):
    """
    Middleware to interface with the Exceptional service.

    Requires very little intervention on behalf of the user; you just need to
    add `exceptional.api_key` to your pylons settings.
    """

    def __init__(self, app, api_key):
        self.app = app
        self.active = False

        try:
            self.api_key = api_key
            self.api_endpoint = EXCEPTIONAL_API_ENDPOINT + "?" + urllib.urlencode({
                    "api_key": self.api_key,
                    "protocol_version": EXCEPTIONAL_PROTOCOL_VERSION
                    })
            self.active = True
        except AttributeError:
            pass
    
    def _submit(self, exc):
        """Submit the actual exception to getexceptional
        """
        info = {}
        info.update(self.environment_info())
        info.update(self.request_info(None))
        info.update(self.exception_info(exc, sys.exc_info()[2]))

        payload = self.compress(json.dumps(info))
        req = urllib2.Request(self.api_endpoint, data=payload)
        req.headers['Content-Encoding'] = 'gzip'
        req.headers['Content-Type'] = 'application/json'

        conn = urllib2.urlopen(req)
        try:
            conn.read()
        finally:
            conn.close()

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            response = req.get_response(self.app)
        except Exception, e:
            try:
                if self.active:
                    self._submit(e)
            except:
                pass
            response = Response()
            response.status_int = 500
            response.body = 'Datadog says: An error has occured.'
        return response(environ, start_response)


    @staticmethod
    def compress(bytes):
        """Compress a bytestring using gzip."""

        stream = StringIO()
        # Use `compresslevel=1`; it's the least compressive but it's fast.
        gzstream = gzip.GzipFile(fileobj=stream, compresslevel=1, mode='wb')
        try:
            try:
                gzstream.write(bytes)
            finally:
                gzstream.close()
            return stream.getvalue()
        finally:
            stream.close()

    @memoize
    def environment_info(self):
        """
        Return a dictionary representing the server environment.

        The idea is that the result of this function will rarely (if ever)
        change for a given app instance. Ergo, the result can be cached between
        requests.
        """

        return {
                "application_environment": {
                    "framework": "pylons",
                    "env": dict(os.environ),
                    "language": "python",
                    "language_version": sys.version.replace('\n', ''),
                    "application_root_directory": self.project_root()
                    },
                "client": {
                    "name": "pylons-exceptional",
                    "version": __version__,
                    "protocol_version": EXCEPTIONAL_PROTOCOL_VERSION
                    }
                }

    def request_info(self, request):
        """
        Return a dictionary of information for a given request.

        This will be run once for every request.
        """
        # FIXME stubbed out
#         return {
#                 "request": {
#                     "session": dict(request.session),
#                     "remote_ip": request.META["REMOTE_ADDR"],
#                     "parameters": parameters,
#                     "action": view.__name__,
#                     "controller": view.__module__,
#                     "url": request.build_absolute_uri(),
#                     "request_method": request.method,
#                     "headers": meta_to_http(request.META)
#                     }
#                 }

        return {}

    def exception_info(self, exception, tb, timestamp=None):
        backtrace = []
        for tb_part in traceback.format_tb(tb):
            backtrace.extend(tb_part.rstrip().splitlines())

        if timestamp is None:
            timestamp = datetime.datetime.utcnow()

        return {
                "exception": {
                    "occurred_at": timestamp.isoformat(),
                    "message": str(exception),
                    "backtrace": backtrace,
                    "exception_class": self.exception_class(exception)
                    }
                }

    def exception_class(self, exception):
        """Return a name representing the class of an exception."""

        cls = type(exception)
        if cls.__module__ == 'exceptions':  # Built-in exception.
            return cls.__name__
        return "%s.%s" % (cls.__module__, cls.__name__)

    @memoize
    def project_root(self):

        """
        Return the root of the current pylons project on the filesystem.
        """

        if "exceptional.root" in config.keys():
            return config["exceptional.root"]
        else:
            return "/I/don/t/know"

    @staticmethod
    def filter_params(params):
        """Filter sensitive information out of parameter dictionaries.
        """

        for key in params.keys():
            if "password" in key:
                del params[key]
        return params
