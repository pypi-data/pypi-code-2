# Copyright (c) 2007-2011 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
pesto.request
-------------

Request object for WSGI applications.
"""

import posixpath
import re
import threading
from urllib import quote

from urlparse import urlunparse
try:
    from functools import partial
except ImportError:
    # Roughly equivalent implementation for Python < 2.5
    # Taken from http://docs.python.org/library/functools.html
    def partial(func, *args, **keywords):
        def newfunc(*fargs, **fkeywords):
            newkeywords = keywords.copy()
            newkeywords.update(fkeywords)
            return func(*(args + fargs), **newkeywords)
        newfunc.func = func
        newfunc.args = args
        newfunc.keywords = keywords
        return newfunc


from pesto.utils import MultiDict
from pesto.httputils import FileUpload
from pesto.wsgiutils import make_query
from pesto.cookie import parse_cookie_header
from pesto import DEFAULT_CHARSET

__all__ = ['Request', 'currentrequest']

KB = 1024
MB = 1024 * KB

# This object will contain a reference to the current request
__local__ = threading.local()

def currentrequest():
    """
    Return the current Request object, or ``None`` if no request object is
    available.
    """
    try:
        return __local__.request
    except AttributeError:
        return None

class Request(object):
    """
    Models an HTTP request, given a WSGI ``environ`` dictionary.
    """

    # Maximum size for application/x-www-form-urlencoded post data, or maximum
    # field size in multipart/form-data encoded data (not including file
    # uploads)
    MAX_SIZE = 16 * KB

    # Maximum size for multipart/form-data encoded post data
    MAX_MULTIPART_SIZE = 2 * MB

    _session = None
    _form = None
    _files = None
    _query = None
    _cookies = None
    environ = None

    charset = DEFAULT_CHARSET

    def __new__(
        cls,
        environ,
        parse_content_type = re.compile(r'\s*(?:.*);\s*charset=([\w\d\-]+)\s*$')
    ):
        u"""
        Ensure the same instance is returned when called multiple times on the
        same environ object.

        Example usage::

            >>> from pesto.testing import TestApp
            >>> env1 = TestApp.make_environ()
            >>> env2 = TestApp.make_environ()
            >>> Request(env1) is Request(env1)
            True
            >>> Request(env2) is Request(env2)
            True
            >>> Request(env1) is Request(env2)
            False
        """
        try:
            return environ['pesto.request']
        except KeyError:
            request = object.__new__(cls)
            __local__.request = request
            request.environ = environ
            request.environ['pesto.request'] = request
            if 'CONTENT_TYPE' in environ:
                match = parse_content_type.match(environ['CONTENT_TYPE'])
                if match:
                    request.charset = match.group(1)
            return request

    def form(self):
        """
        Return the contents of any submitted form data

        If the form has been submitted via POST, GET parameters are also
        available via ``Request.query``.
        """
        if self._form is None:
            if self.request_method in ('PUT', 'POST'):
                self._form = MultiDict(
                    parse_post(
                        self.environ,
                        self.environ['wsgi.input'],
                        self.charset,
                        self.MAX_SIZE,
                        self.MAX_MULTIPART_SIZE,
                    )
                )
            else:
                self._form = MultiDict(
                    parse_querystring(
                        self.environ['QUERY_STRING'],
                        self.charset
                    )
                )
        return self._form
    form = property(form)

    def files(self):
        """
        Return ``FileUpload`` objects for all uploaded files
        """
        if self._files is None:
            self._files = MultiDict(
                (k, v)
                for k, v in self.form.iterallitems()
                if isinstance(v, FileUpload)
            )
        return self._files
    files = property(files)

    def query(self):
        """
        Return a ``MultiDict`` of any querystring submitted data.

        This is available regardless of whether the original request was a
        ``GET`` request.

        Synopsis::

            >>> from pesto.testing import TestApp
            >>> request = Request(TestApp.make_environ(QUERY_STRING="animal=moose"))
            >>> request.query.get('animal')
            u'moose'

        Note that this property is unaffected by the presence of POST data::

            >>> from pesto.testing import TestApp
            >>> from StringIO import StringIO
            >>> postdata = 'animal=hippo'
            >>> request = Request(TestApp.make_environ(
            ...     QUERY_STRING="animal=moose",
            ...     REQUEST_METHOD="POST",
            ...     CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8",
            ...     CONTENT_LENGTH=len(postdata),
            ...     wsgi_input=postdata
            ... ))
            >>> request.form.get('animal')
            u'hippo'
            >>> request.query.get('animal')
            u'moose'
        """
        if self._query is None:
            self._query = MultiDict(
                parse_querystring(self.environ.get('QUERY_STRING'))
            )

        return self._query
    query = property(query)

    def __getitem__(self, key):
        """
        Return the value of ``key`` from submitted form values.
        """
        marker = []
        v = self.get(key, marker)
        if v is marker:
            raise KeyError(key)
        return v

    def get(self, key, default=None):
        """
        Look up ``key`` in submitted form values
        """
        return self.form.get(key, default)

    def getlist(self, key):
        """
        Return a list of submitted form values for ``key``
        """
        return self.form.getlist(key)

    def __contains__(self, key):
        """
        Return ``True`` if ``key`` is in the submitted form values
        """
        return key in self.form

    def cookies(self):
        """
        Return a ``pesto.utils.MultiDict`` of cookies read from the request headers::

            >>> from pesto.testing import TestApp
            >>> request = Request(TestApp.make_environ(
            ...     HTTP_COOKIE='''$Version="1";
            ...     Customer="WILE_E_COYOTE";
            ...     Part="Rocket_0001";
            ...     Part="Catapult_0032"
            ... '''))
            >>> [c.value for c in request.cookies.getlist('Customer')]
            ['WILE_E_COYOTE']
            >>> [c.value for c in request.cookies.getlist('Part')]
            ['Rocket_0001', 'Catapult_0032']


        See rfc2109, section 4.4
        """
        if self._cookies is None:
            self._cookies = MultiDict(
                (cookie.name, cookie)
                for cookie in parse_cookie_header(self.get_header("Cookie"))
            )
        return self._cookies
    cookies = property(
        cookies, None, None,
        cookies.__doc__
    )

    def get_header(self, name, default=None):
        """
        Return an arbitrary HTTP header from the request.

        name
            HTTP header name, eg 'User-Agent' or 'If-Modified-Since'.

        default
            default value to return if the header is not set.

        Technical note:

        Headers in the original HTTP request are always formatted like this::

            If-Modified-Since: Thu, 04 Jan 2007 21:41:08 GMT

        However, in the WSGI environ dictionary they appear as follows::

            {
                ...
                'HTTP_IF_MODIFIED_SINCE': 'Thu, 04 Jan 2007 21:41:08 GMT'
                ...
            }

        Despite this, this method expects the *former* formatting (with
        hyphens), and is not case sensitive.

        """
        return self.environ.get(
            'HTTP_' + name.upper().replace('-', '_'),
            default
        )

    def request_path(self):
        """
        Return the path component of the requested URI
        """
        scheme, netloc, path, params, query, frag = self.parsed_uri
        return path
    request_path = property(request_path, doc=request_path.__doc__)

    @property
    def request_uri(self):
        """
        Return the absolute URI, including query parameters.
        """
        return urlunparse(self.parsed_uri)

    @property
    def application_uri(self):
        """
        Return the base URI of the WSGI application (ie the URI up to
        SCRIPT_NAME, but not including PATH_INFO or query information).

        Synopsis::

            >>> from pesto.testing import make_environ
            >>> request = Request(make_environ(SCRIPT_NAME='/animals', PATH_INFO='/alligator.html'))
            >>> request.application_uri
            'http://localhost/animals'
        """
        uri = self.parsed_uri
        scheme, netloc, path, params, query, frag = self.parsed_uri
        return urlunparse((scheme, netloc, self.script_name, '', '', ''))

    def parsed_uri(self):
        """
        Returns the current URI as a tuple of the form::

            (
             addressing scheme, network location, path,
             parameters, query, fragment identifier
            )

        Synopsis::

            >>> from pesto.testing import make_environ
            >>> request = Request(make_environ(
            ...     wsgi_url_scheme = 'https',
            ...     HTTP_HOST = 'example.com',
            ...     SCRIPT_NAME = '/animals',
            ...     PATH_INFO = '/view',
            ...     SERVER_PORT = '443',
            ...     QUERY_STRING = 'name=alligator'
            ... ))
            >>> request.parsed_uri
            ('https', 'example.com', '/animals/view', '', 'name=alligator', '')

        Note that the port number is stripped if the addressing scheme is
        'http' and the port is 80, or the scheme is https and the port is 443::

            >>> request = Request(make_environ(
            ...     wsgi_url_scheme = 'http',
            ...     HTTP_HOST = 'example.com:80',
            ...     SCRIPT_NAME = '/animals',
            ...     PATH_INFO = '/view',
            ...     QUERY_STRING = 'name=alligator'
            ... ))
            >>> request.parsed_uri
            ('http', 'example.com', '/animals/view', '', 'name=alligator', '')
        """
        env = self.environ.get
        script_name = env("SCRIPT_NAME", "")
        path_info = env("PATH_INFO", "")
        query_string = env("QUERY_STRING", "")
        scheme = env('wsgi.url_scheme', 'http')

        try:
            host = self.environ['HTTP_HOST']
            if ':' in host:
                host, port = host.split(':', 1)
            else:
                port = self.environ['SERVER_PORT']
        except KeyError:
            host = self.environ['SERVER_NAME']
            port = self.environ['SERVER_PORT']

        if (scheme == 'http' and port == '80') \
            or (scheme == 'https' and port == '443'):
            netloc = host
        else:
            netloc = host + ':' + port

        return (
            scheme,
            netloc,
            script_name + path_info,
            '', # Params
            query_string,
            '', # Fragment
        )
    parsed_uri = property(parsed_uri, doc=parsed_uri.__doc__)

     # getters for environ properties
    def _get_env(self, name, default=None):
        """
        Return a value from the WSGI environment
        """
        return self.environ.get(name, default)

    env_prop = lambda name, doc, default=None, _get_env=_get_env: property(
        partial(_get_env, name=name, default=None), doc=doc
    )

    content_type  = env_prop('CONTENT_TYPE', "HTTP Content-Type header")
    document_root = env_prop('DOCUMENT_ROOT', "Server document root")
    path_info     = env_prop('PATH_INFO', "WSGI PATH_INFO value", '')
    query_string  = env_prop('QUERY_STRING', "WSGI QUERY_STRING value")
    script_name   = env_prop('SCRIPT_NAME', "WSGI SCRIPT_NAME value")
    server_name   = env_prop('SERVER_NAME', "WSGI SERVER_NAME value")
    remote_addr   = env_prop('REMOTE_ADDR', "WSGI REMOTE_ADDR value")

    def referrer(self):
        """
        Return the HTTP referer header, or ``None`` if this is not available.
        """
        return self.get_header('Referer')
    referrer = property(referrer, doc=referrer.__doc__)

    def user_agent(self):
        """
        Return the HTTP user agent header, or ``None`` if this is not available.
        """
        return self.get_header('User-Agent')
    user_agent = property(user_agent, doc=user_agent.__doc__)

    def request_method(self):
        """
        Return the HTTP method used for the request, eg ``GET`` or ``POST``.
        """
        return self.environ.get("REQUEST_METHOD").upper()
    request_method = property(request_method, doc=request_method.__doc__)


    def session(self):
        """
        Return the session associated with this request.

        Requires a session object to have been inserted into the WSGI
        environment by a middleware application (see
        ``pesto.session.base.sessioning_middleware`` for an example).
        """
        return self.environ["pesto.session"]

    session = property(
        session, None, None,
        doc = session.__doc__
    )

    def make_uri(
        self, scheme=None, netloc=None,
        path=None, parameters=None,
        query=None, fragment=None,
        script_name=None,
        path_info=None
    ):
        r"""
        Make a new URI based on the current URI, replacing any of the six
        URI elements (scheme, netloc, path, parameters, query or fragment)

        A ``path_info`` argument can also be given instead of the ``path``
        argument. In this case the generated URI path will be 
        ``<SCRIPT_NAME>/<path_info>``.

        Synopsis:

        Calling request.make_uri with no arguments will return the current URI::

            >>> from pesto.testing import make_environ
            >>> request = Request(make_environ(HTTP_HOST='example.com', SCRIPT_NAME='', PATH_INFO='/foo'))
            >>> request.make_uri()
            'http://example.com/foo'

        Using keyword arguments it is possible to override any part of the URI::

            >>> request.make_uri(scheme='ftp')
            'ftp://example.com/foo'

            >>> request.make_uri(path='/bar')
            'http://example.com/bar'

            >>> request.make_uri(query={'page' : '2'})
            'http://example.com/foo?page=2'

        If you just want to replace the PATH_INFO part of the URI, you can pass
        ``path_info`` to the ``make_uri``. This will generate a URI relative to
        wherever your WSGI application is mounted::

            >>> # Sample environment for an application mounted at /fruitsalad
            >>> env = make_environ(
            ...     HTTP_HOST='example.com',
            ...     SCRIPT_NAME='/fruitsalad',
            ...     PATH_INFO='/banana'
            ... )
            >>> Request(env).make_uri(path_info='/kiwi')
            'http://example.com/fruitsalad/kiwi'

        The path and query values are URL escaped before being returned::

            >>> request.make_uri(path=u'/caff\u00e8 latte')
            'http://example.com/caff%C3%A8%20latte'

        The ``query`` argument can be a string, a dictionary, a ``MultiDict``,
        or a list of ``(name, value)`` tuples::

            >>> request.make_uri(query=u'a=tokyo&b=milan')
            'http://example.com/foo?a=tokyo&b=milan'

            >>> request.make_uri(query={'a': 'tokyo', 'b': 'milan'})
            'http://example.com/foo?a=tokyo;b=milan'

            >>> request.make_uri(query=MultiDict([('a', 'tokyo'), ('b', 'milan'), ('b', 'paris')]))
            'http://example.com/foo?a=tokyo;b=milan;b=paris'

            >>> request.make_uri(query=[('a', 'tokyo'), ('b', 'milan'), ('b', 'paris')])
            'http://example.com/foo?a=tokyo;b=milan;b=paris'

        If a relative path is passed, the returned URI is joined to the old in
        the same way as a web browser would interpret a relative HREF in a
        document at the current location::

            >>> request = Request(make_environ(HTTP_HOST='example.com', SCRIPT_NAME='', PATH_INFO='/banana/milkshake'))
            >>> request.make_uri(path='pie')
            'http://example.com/banana/pie'

            >>> request.make_uri(path='../strawberry')
            'http://example.com/strawberry'

            >>> request.make_uri(path='../../../plum')
            'http://example.com/plum'

        Note that a URI with a trailing slash will have different behaviour
        from one without a trailing slash::

            >>> request = Request(make_environ(HTTP_HOST='example.com', SCRIPT_NAME='', PATH_INFO='/banana/milkshake/'))
            >>> request.make_uri(path='mmmm...')
            'http://example.com/banana/milkshake/mmmm...'

            >>> request = Request(make_environ(HTTP_HOST='example.com', SCRIPT_NAME='', PATH_INFO='/banana/milkshake'))
            >>> request.make_uri(path='mmmm...')
            'http://example.com/banana/mmmm...'


        """
        uri = []

        parsed_uri = self.parsed_uri

        if path is not None:
            if isinstance(path, unicode):
                path = path.encode(DEFAULT_CHARSET)
            if path[0] != '/':
                path = posixpath.join(posixpath.dirname(parsed_uri[2]), path)
                path = posixpath.normpath(path)

        elif script_name is not None or path_info is not None:

            if script_name is None:
                script_name = self.environ['SCRIPT_NAME']

            if path_info is None:
                path_info = self.environ['PATH_INFO']

            path = script_name + path_info

        else:
            path = parsed_uri[2]

        if isinstance(path, unicode):
            path = path.encode(DEFAULT_CHARSET)

        path = quote(path)

        if query is not None:
            if not isinstance(query, basestring):
                query = make_query(query)
            elif isinstance(query, unicode):
                query = query.encode(DEFAULT_CHARSET)

        for specified, parsed in zip((scheme, netloc, path, parameters, query, fragment), parsed_uri):
            if specified is not None:
                uri.append(specified)
            else:
                uri.append(parsed)

        return urlunparse(uri)

    def text(self):
        """
        Return a useful text representation of the request
        """
        import pprint
        return "<%s\n\trequest_uri=%s\n\trequest_path=%s\n\t%s\n\t%s>" % (
                self.__class__.__name__,
                self.request_uri,
                self.request_path,
                pprint.pformat(self.environ),
                pprint.pformat(self.form.items()),
        )

# Imports at end to avoid circular dependencies
from pesto.httputils import parse_querystring, parse_post
