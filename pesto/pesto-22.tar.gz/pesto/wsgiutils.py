# Copyright (c) 2007-2011 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
pesto.wsgiutils
---------------

Utility functions for WSGI applications
"""

__docformat__ = 'restructuredtext en'
__all__ = [
    'use_x_forwarded', 'mount_app', 'use_redirect_url',
    'make_absolute_url', 'run_with_cgi', 'make_uri_component', 'static_server',
    'serve_static_file', 'uri_join', 'make_query', 'with_request_args',
]

import inspect
import itertools
import os
import posixpath
import re
import sys
import unicodedata
import time
import mimetypes
try:
    from email.utils import parsedate_tz, mktime_tz
except ImportError:
    from email.Utils import parsedate_tz, mktime_tz

from cStringIO import StringIO
from urlparse import urlparse, urlunparse
from urllib import quote, quote_plus

try:
    from functools import wraps
except ImportError:
    def wraps(wrappedfunc):
        """
        No-op replacement for ``functools.wraps`` for python < 2.5
        """
        def call(func):
            """
            Call wrapped function
            """
            return lambda *args, **kwargs: func(*args, **kwargs)
        return call

from pesto.response import Response
from pesto.utils import MultiDict

def use_x_forwarded(trusted=("127.0.0.1", "localhost")):
    """
    Return a middleware application that modifies the WSGI environment so that
    the X_FORWARDED_* headers are observed and generated URIs are correct in a
    proxied environment.

    Use this whenever the WSGI application server is sitting behind
    Apache or another proxy server.

    HTTP_X_FORWARDED_FOR is substituted for REMOTE_ADDR and
    HTTP_X_FORWARDED_HOST for SERVER_NAME. If HTTP_X_FORWARDED_SSL is set, then
    the wsgi.url_scheme is modified to ``https`` and ``HTTPS`` is set to
    ``on``.

    Example::

        >>> from pesto.core import to_wsgi
        >>> from pesto.testing import TestApp
        >>> def app(request):
        ...     return Response(["URL is ", request.request_uri, "; REMOTE_ADDR is ", request.remote_addr])
        ...
        >>> app = TestApp(use_x_forwarded()(to_wsgi(app)))
        >>> response = app.get('/',
        ...     SERVER_NAME='wsgiserver-name',
        ...     SERVER_PORT='8080',
        ...     HTTP_HOST='wsgiserver-name:8080',
        ...     REMOTE_ADDR='127.0.0.1',
        ...     HTTP_X_FORWARDED_HOST='real-name:81',
        ...     HTTP_X_FORWARDED_FOR='1.2.3.4'
        ... )
        >>> response.body
        'URL is http://real-name:81/; REMOTE_ADDR is 1.2.3.4'
        >>> response = app.get('/',
        ...     SERVER_NAME='wsgiserver-name',
        ...     SERVER_PORT='8080',
        ...     HTTP_HOST='wsgiserver-name:8080',
        ...     REMOTE_ADDR='127.0.0.1',
        ...     HTTP_X_FORWARDED_HOST='real-name:443',
        ...     HTTP_X_FORWARDED_FOR='1.2.3.4',
        ...     HTTP_X_FORWARDED_SSL='on'
        ... )
        >>> response.body
        'URL is https://real-name/; REMOTE_ADDR is 1.2.3.4'

    In a non-forwarded environment, the environ dictionary will not be
    changed::

        >>> response = app.get('/',
        ...     SERVER_NAME='wsgiserver-name',
        ...     SERVER_PORT='8080',
        ...     HTTP_HOST='wsgiserver-name:8080',
        ...     REMOTE_ADDR='127.0.0.1',
        ... )
        >>> response.body
        'URL is http://wsgiserver-name:8080/; REMOTE_ADDR is 127.0.0.1'

    """

    trusted = dict.fromkeys(trusted, None)
    def middleware(app):
        """
        Create ``use_x_forwarded`` middleware for WSGI callable ``app``
        """
        def call(environ, start_response):
            """
            Call the decorated WSGI callable ``app`` with the modified environ
            """
            if environ.get('REMOTE_ADDR') in trusted:

                try:
                    environ['REMOTE_ADDR'] = environ['HTTP_X_FORWARDED_FOR']
                except KeyError:
                    pass

                is_ssl = bool(environ.get('HTTP_X_FORWARDED_SSL'))

                if 'HTTP_X_FORWARDED_HOST' in environ:
                    host = environ['HTTP_X_FORWARDED_HOST']

                    if ':' in host:
                        port = host.split(':')[1]
                    else:
                        port = is_ssl and '443' or '80'

                    environ['HTTP_HOST'] = host
                    environ['SERVER_PORT'] = port

                if is_ssl:
                    environ['wsgi.url_scheme'] = 'https'
                    environ['HTTPS'] = 'on'

            return app(environ, start_response)
        return call
    return middleware

def mount_app(appmap):
    """
    Create a composite application with different mount points.

    Synopsis::

        >>> def app1(e, sr):
        ...     return [1]
        ...
        >>> def app2(e, sr):
        ...     return [2]
        ...
        >>> app = mount_app({
        ...     '/path/one' : app1,
        ...     '/path/two' : app2,
        ... })
    """
    apps = appmap.items()
    apps.sort()
    apps.reverse()

    def mount_app_application(env, start_response):
        """
        WSGI callable that invokes one of the WSGI applications in ``appmap``
        depending on the WSGI ``PATH_INFO`` environ variable>
        """
        script_name = env.get("SCRIPT_NAME")
        path_info = env.get("PATH_INFO")
        for key, app in apps:
            if path_info[:len(key)] == key:
                env["SCRIPT_NAME"] = script_name + key
                env["PATH_INFO"] = path_info[len(key):]
                if env["SCRIPT_NAME"] == "/":
                    env["SCRIPT_NAME"] = ""
                    env["PATH_INFO"] = "/" + env["PATH_INFO"]
                return app(env, start_response)
        else:
            return Response.not_found()(env, start_response)

    return mount_app_application

def static_server(document_root, default_charset="ISO-8859-1", bufsize=8192):
    """
    Create a simple WSGI static file server application

    Synopsis::

        >>> from pesto.dispatch import dispatcher_app
        >>> dispatcher = dispatcher_app()
        >>> dispatcher.match('/static/<path:path>',
        ...     GET=static_server('/docroot'),
        ...     HEAD=static_server('/docroot')
        ... )
    """
    from pesto.core import to_wsgi

    document_root = os.path.abspath(os.path.normpath(document_root))

    @to_wsgi
    def static_server_application(request, path=None):
        """
        WSGI static server application
        """

        if path is None:
            path = request.path_info

        path = posixpath.normpath(path)
        while path[0] == '/':
            path = path[1:]

        path = os.path.join(document_root, *path.split('/'))
        path = os.path.normpath(path)

        if not path.startswith(document_root):
            return Response.forbidden()
        return serve_static_file(request, path, default_charset, bufsize)

    return static_server_application

def serve_static_file(request, path, default_charset="ISO-8859-1", bufsize=8192):
    """
    Serve a static file located at ``path``. It is the responsibility of the
    caller to check that the path is valid and allowed.

    Synopsis::

        >>> from pesto.dispatch import dispatcher_app
        >>> def view_important_document(request):
        ...     return serve_static_file(request, '/path/to/very_important_document.pdf')
        ...
        >>> def download_important_document(request):
        ...     return serve_static_file(request, '/path/to/very_important_document.pdf').add_headers(
        ...         content_disposition='attachment; filename=very_important_document.pdf'
        ...     )
        ...
    """
    from pesto.response import STATUS_OK, STATUS_NOT_MODIFIED

    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return Response.not_found()

    mod_since = request.get_header('if-modified-since')
    if mod_since is not None:
        mod_since = mktime_tz(parsedate_tz(mod_since))
        if int(mtime) <= int(mod_since):
            return Response(status=STATUS_NOT_MODIFIED)

    typ, enc = mimetypes.guess_type(path)
    if typ is None:
        typ = 'application/octet-stream'
    if typ.startswith('text/'):
        typ = typ + '; charset=%s' % default_charset

    if 'wsgi.file_wrapper' in request.environ:
        content_iterator = lambda fileob: request.environ['wsgi.file_wrapper'](fileob, bufsize)
    else:
        content_iterator = lambda fileob: ClosingIterator(iter(lambda: fileob.read(bufsize), ''), fileob.close)
    try:
        _file = open(path, 'rb')
    except IOError:
        return Response.forbidden()

    return Response(
        status = STATUS_OK,
        content_length = str(os.path.getsize(path)),
        last_modified = time.strftime('%w, %d %b %Y %H:%M:%S +0000', time.gmtime(mtime)),
        content_type = typ,
        content_encoding = enc,
        content = content_iterator(_file)
    )

def normpath(path):
    """
    Return ``path`` normalized to remove '../' etc.
    This differs from ``posixpath.normpath`` in that:

        * trailing slashes are preserved
        * multiple consecutive slashes are *always* condensed to a single slash

    Examples::

        >>> normpath('/hello/../goodbye')
        '/goodbye'
        >>> normpath('//etc/passwd')
        '/etc/passwd'
        >>> normpath('../../../../etc/passwd')
        'etc/passwd'
        >>> normpath('/etc/passwd/')
        '/etc/passwd/'
    """
    segments = path.split('/')
    newpath = []
    last = len(segments) - 1
    for pos, seg in enumerate(segments):
        if seg == '.':
            seg = ''

        if seg == '':
            allow_empty = (
                pos == 0
                or pos == last and newpath and newpath[-1] != ''
                or pos == last and newpath == ['']
            )
            if not allow_empty:
                continue

        if seg == '..':
            if newpath and newpath != ['']:
                newpath.pop()
            continue

        newpath.append(seg)

    return '/'.join(newpath)

def use_redirect_url(use_redirect_querystring=True):
    """
    Replace the ``SCRIPT_NAME`` and ``QUERY_STRING`` WSGI environment variables with
    ones taken from Apache's ``REDIRECT_URL`` and ``REDIRECT_QUERY_STRING`` environment
    variable, if set.

    If an application is mounted as CGI and Apache RewriteRules are used to
    route requests, the ``SCRIPT_NAME`` and ``QUERY_STRING`` parts of the environment
    may not be meaningful for reconstructing URLs.

    In this case Apache puts an extra key, ``REDIRECT_URL`` into the path which
    contains the full path as requested.

    See also:

        * `URL reconstruction section of PEP 333 <http://www.python.org/dev/peps/pep-0333/#url-reconstruction>`_.
        * `Apache mod_rewrite reference <http://httpd.apache.org/docs/2.0/mod/mod_rewrite.html>`_.

    **Example**: assume a handler similar to the below has been made available
    at the address ``/cgi-bin/myhandler.cgi``::

        >>> from pesto import to_wsgi
        >>> @to_wsgi
        ... def app(request):
        ...     return Response(["My URL is " + request.request_uri])
        ...
 
    Apache has been configured to redirect requests
    using the following RewriteRules in a ``.htaccess`` file in the server's
    document root, or the equivalents in the apache configuration file::

        RewriteEngine On
        RewriteBase /
        RewriteRule ^pineapple(.*)$ /cgi-bin/myhandler.cgi [PT]

    The following code creates a simulation of the request headers Apache will
    pass to the application with the above rewrite rules. Without the
    middleware, the output will be as follows::

        >>> from pesto.testing import TestApp
        >>> TestApp(app).get(
        ...     SERVER_NAME = 'example.com',
        ...     REDIRECT_URL = '/pineapple/cake',
        ...     SCRIPT_NAME = '/myhandler.cgi',
        ...     PATH_INFO = '/cake',
        ... ).body
        'My URL is http://example.com/myhandler.cgi/cake'


    The ``use_redirect_url`` middleware will correctly set the
    ``SCRIPT_NAME`` and ``QUERY_STRING`` values::

        >>> app = use_redirect_url()(app)

    With this change the application will now output the correct values::

        >>> TestApp(app).get(
        ...     SERVER_NAME = 'example.com',
        ...     REDIRECT_URL = '/pineapple/cake',
        ...     SCRIPT_NAME = '/myhandler.cgi',
        ...     PATH_INFO = '/cake',
        ... ).body
        'My URL is http://example.com/pineapple/cake'



    """
    def use_redirect_url(wsgiapp):
        def use_redirect_url(env, start_response):
            if "REDIRECT_URL" in env:
                env['SCRIPT_NAME'] = env["REDIRECT_URL"]
                path_info = env["PATH_INFO"]
                if env["SCRIPT_NAME"][-len(path_info):] == path_info:
                    env["SCRIPT_NAME"] = env["SCRIPT_NAME"][:-len(path_info)]

            if use_redirect_querystring:
                if "REDIRECT_QUERY_STRING" in env:
                    env["QUERY_STRING"] = env["REDIRECT_QUERY_STRING"]
            return wsgiapp(env, start_response)
        return use_redirect_url
    return use_redirect_url

def make_absolute_url(wsgi_environ, url):
    """
    Return an absolute url from ``url``, based on the current url.

    Synopsis::

        >>> from pesto.testing import make_environ
        >>> environ = make_environ(wsgi_url_scheme='https', SERVER_NAME='example.com', SERVER_PORT='443', PATH_INFO='/foo')
        >>> make_absolute_url(environ, '/bar')
        'https://example.com/bar'
        >>> make_absolute_url(environ, 'baz')
        'https://example.com/foo/baz'
        >>> make_absolute_url(environ, 'http://anotherhost/bar')
        'http://anotherhost/bar'

    Note that the URL is constructed using the PEP-333 URL
    reconstruction method
    (http://www.python.org/dev/peps/pep-0333/#url-reconstruction) and the
    returned URL is normalized::

        >>> environ = make_environ(
        ...     wsgi_url_scheme='https',
        ...     SERVER_NAME='example.com',
        ...     SERVER_PORT='443',
        ...     SCRIPT_NAME='/colors',
        ...     PATH_INFO='/red',
        ... )

        >>> make_absolute_url(environ, 'blue')
        'https://example.com/colors/red/blue'

        >>> make_absolute_url(environ, '../blue')
        'https://example.com/colors/blue'

        >>> make_absolute_url(environ, 'blue/')
        'https://example.com/colors/red/blue/'
    
    """
    env = wsgi_environ.get
    if '://' not in url:
        scheme = env('wsgi.url_scheme', 'http')

        if scheme == 'https':
            port = ':' + env('SERVER_PORT', '443')
        else:
            port = ':' + env('SERVER_PORT', '80')

        if scheme == 'http' and port == ':80' or scheme == 'https' and port == ':443':
            port = ''

        parsed = urlparse(url)
        url = urlunparse((
            env('wsgi.url_scheme',''),
            env('HTTP_HOST', env('SERVER_NAME', '') + port),
            normpath(
                posixpath.join(
                    quote(env('SCRIPT_NAME', '')) + quote(env('PATH_INFO', '')),
                    parsed[2]
                )
            ),
            parsed[3],
            parsed[4],
            parsed[5],
        ))
    return url

def uri_join(base, link):
    """
    Example::

        >>> uri_join('http://example.org/', 'http://example.com/')
        'http://example.com/'

        >>> uri_join('http://example.com/', '../styles/main.css')
        'http://example.com/styles/main.css'

        >>> uri_join('http://example.com/subdir/', '../styles/main.css')
        'http://example.com/styles/main.css'

        >>> uri_join('http://example.com/login', '?error=failed+auth')
        'http://example.com/login?error=failed+auth'

        >>> uri_join('http://example.com/login', 'register')
        'http://example.com/register'
    """
    SCHEME, NETLOC, PATH, PARAM, QUERY, FRAGMENT = range(6)
    plink = urlparse(link)

    # Link is already absolute, return it unchanged
    if plink[SCHEME]:
        return link

    pbase = urlparse(base)
    path = pbase[PATH]
    if plink[PATH]:
        path = normpath(posixpath.join(posixpath.dirname(pbase[PATH]), plink[PATH]))

    return urlunparse((
        pbase[SCHEME],
        pbase[NETLOC],
        path,
        plink[PARAM],
        plink[QUERY],
        plink[FRAGMENT]
    ))

def _qs_frag(key, value, charset=None):
    u"""
    Return a fragment of a query string in the format 'key=value'.

    >>> _qs_frag('search-by', 'author, editor')
    'search-by=author%2C+editor'

    If no encoding is specified, unicode values are encoded using the character set
    specified by ``pesto.DEFAULT_CHARSET``.
    """
    from pesto import DEFAULT_CHARSET
    if charset is None:
        charset = DEFAULT_CHARSET

    return quote_plus(_make_bytestr(key, charset)) \
            + '=' \
            + quote_plus(_make_bytestr(value, charset))

def _make_bytestr(ob, charset):
    u"""
    Return a byte string conversion of the given object. If the object is a
    unicode string, encode it with the given encoding.

    Example::

        >>> _make_bytestr(1, 'utf-8')
        '1'
        >>> _make_bytestr(u'a', 'utf-8')
        'a'
    """
    if isinstance(ob, unicode):
        return ob.encode(charset)
    return str(ob)

def _repeat_keys(iterable):
    u"""
    Return a list of ``(key, scalar_value)`` tuples given an iterable
    containing ``(key, iterable_or_scalar_value)``.

    Example::

        >>> list(
        ...     _repeat_keys([('a', 'b')])
        ... )
        [('a', 'b')]
        >>> list(
        ...     _repeat_keys([('a', ['b', 'c'])])
        ... )
        [('a', 'b'), ('a', 'c')]
    """

    for key, value in iterable:
        if isinstance(value, basestring):
            value = [value]
        else:
            try:
                value = iter(value)
            except TypeError:
                value = [value]

        for subvalue in value:
            yield key, subvalue

def make_query(data=None, separator=';', charset=None, **kwargs):
    """
    Return a query string formed from the given dictionary data.

    Note that the pairs are separated using a semicolon, in accordance with
    `the W3C recommendation <http://www.w3.org/TR/1999/REC-html401-19991224/appendix/notes.html#h-B.2.2>`_

    If no encoding is given, unicode values are encoded using the character set
    specified by ``pesto.DEFAULT_CHARSET``.

    Synopsis::

        >>> # Basic usage
        >>> make_query({ 'eat' : u'more cake', 'drink' : u'more tea' })
        'drink=more+tea;eat=more+cake'

        >>> # Use an ampersand as the separator
        >>> make_query({ 'eat' : u'more cake', 'drink' : u'more tea' }, separator='&')
        'drink=more+tea&eat=more+cake'

        >>> # Can also be called using ``**kwargs`` style
        >>> make_query(eat=u'more cake', drink=u'more tea')
        'drink=more+tea;eat=more+cake'

        >>> # Non-string values
        >>> make_query(eat=[1, 2], drink=3.4)
        'drink=3.4;eat=1;eat=2'

        >>> # Multiple values per key
        >>> make_query(eat=[u'more', u'cake'], drink=u'more tea')
        'drink=more+tea;eat=more;eat=cake'

        >>> # Anything with a value of ``None`` is excluded from the query
        >>> make_query(x='1', y=None)
        'x=1'

    """
    from pesto import DEFAULT_CHARSET

    if isinstance(data, MultiDict):
        items = data.allitems()
    elif isinstance(data, dict):
        items = data.items()
    elif data is None:
        items = []
    else:
        items = list(data)
    items += kwargs.items()

    if charset is None:
        charset = DEFAULT_CHARSET

    # Sort data items for a predictable order in tests
    items.sort()
    items = _repeat_keys(items)
    items = ((k, v) for k, v in items if v is not None)
    return separator.join([
        _qs_frag(k, v, charset=charset) for k, v in items
    ])



def make_wsgi_environ_cgi():
    """
    Create a wsgi environment dictionary based on the CGI environment
    (taken from ``os.environ``)
    """

    environ = dict(
        PATH_INFO = '',
        SCRIPT_NAME = '',
    )
    environ.update(os.environ)

    environ['wsgi.version'] = (1, 0)
    if environ.get('HTTPS','off') in ('on', '1'):
        environ['wsgi.url_scheme'] = 'https'
    else:
        environ['wsgi.url_scheme'] = 'http'

    environ['wsgi.input']        = sys.stdin
    environ['wsgi.errors']       = sys.stderr
    environ['wsgi.multithread']  = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once']     = True

    # PEP 333 insists that these be present and non-empty
    assert 'REQUEST_METHOD' in environ
    assert 'SERVER_PROTOCOL' in environ
    assert 'SERVER_NAME' in environ
    assert 'SERVER_PORT' in environ

    return environ

def run_with_cgi(application, environ=None):
    """
    Run application ``application`` as a CGI script
    """

    if environ is None:
        environ = make_wsgi_environ_cgi()

    headers_set = []
    headers_sent = []

    def write(data):
        """
        WSGI write for CGI: write output to ``sys.stdout``
        """
        if not headers_set:
            raise AssertionError("write() before start_response()")

        elif not headers_sent:
            # Before the first output, send the stored headers
            status, response_headers = headers_sent[:] = headers_set
            sys.stdout.write('Status: %s\r\n' % status)
            for header in response_headers:
                sys.stdout.write('%s: %s\r\n' % header)
            sys.stdout.write('\r\n')

        sys.stdout.write(data)
        sys.stdout.flush()

    def start_response(status, response_headers, exc_info=None):
        """
        WSGI ``start_response`` function
        """
        if exc_info:
            try:
                if headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None     # avoid dangling circular ref
        elif headers_set:
            raise AssertionError("Headers already set!")

        headers_set[:] = [status, response_headers]
        return write

    result = application(environ, start_response)
    try:
        for data in result:
            if data:    # don't send headers until body appears
                write(data)
        if not headers_sent:
            write('')   # send headers now if body was empty
    finally:
        if hasattr(result, 'close'):
            result.close()


def make_uri_component(s, separator="-"):
    """
    Turn a string into something suitable for a URI component.

    Synopsis::

        >>> import pesto.wsgiutils
        >>> pesto.wsgiutils.make_uri_component(u"How now brown cow")
        'how-now-brown-cow'


    Unicode characters are mapped to ASCII equivalents where appropriate, and
    characters which would normally have to be escaped are translated into
    hyphens to ease readability of the generated URI.

    s
        The (unicode) string to translate.

    separator
        A single ASCII character that will be used to replace spaces and other
        characters that are inadvisable in URIs.

    returns
        A lowercase ASCII string, suitable for inclusion as part of a URI.

    """
    if isinstance(s, unicode):
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    s = s.strip().lower()
    s = re.sub(r'[\s\/]+', separator, s)
    s = re.sub(r'[^A-Za-z0-9\-\_]', '', s)
    return s

class RequestArgsConversionError(ValueError):
    """
    Raised by ``with_request_args`` when a value cannot be converted to the
    requested type
    """

class RequestArgsKeyError(KeyError):
    """
    Raised by ``with_request_args`` when a value cannot be converted to the
    requested type
    """

def with_request_args(**argspec):
    """
    Function decorator to map request query/form arguments to function arguments.

    Synopsis::

        >>> from pesto.dispatch import dispatcher_app
        >>> from pesto import to_wsgi
        >>> from pesto.testing import TestApp
        >>>
        >>> dispatcher = dispatcher_app()
        >>>
        >>> @dispatcher.match('/recipes/<category:unicode>/view', 'GET')
        ... @with_request_args(id=int)
        ... def my_handler(request, category, id):
        ...     return Response([
        ...         u'Recipe #%d in category "%s".' % (id, category)
        ...     ])
        ... 
        >>> print TestApp(dispatcher).get('/recipes/rat-stew/view', QUERY_STRING='id=2')
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        Recipe #2 in category "rat-stew".

    If specified arguments are not present in the request (and no default value
    is given in the function signature), or a ValueError is thrown during type
    conversion an appropriate error will be raised::

        >>> print TestApp(dispatcher).get('/recipes/rat-stew/view') #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        RequestArgsKeyError: 'id'
        >>> print TestApp(dispatcher).get('/recipes/rat-stew/view?id=elephant') #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        RequestArgsConversionError: Could not convert parameter 'id' to requested type (invalid literal for int() with base 10: 'elephant')
 
    A default argument value in the handler function will protect against this::

        >>> dispatcher = dispatcher_app()
        >>> @dispatcher.match('/recipes/<category:unicode>/view', 'GET')
        ... @with_request_args(category=unicode, id=int)
        ... def my_handler(request, category, id=1):
        ...     return Response([
        ...         u'Recipe #%d in category "%s".' % (id, category)
        ...     ])
        ... 
        >>> print TestApp(dispatcher).get('/recipes/mouse-pie/view')
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        Recipe #1 in category "mouse-pie".
 
    Sometimes it is necessary to map multiple request values to a single
    argument, for example in a form where two or more input fields have the
    same name. To do this, put the type-casting function into a list when
    calling ``with_request_args``::

        >>> @to_wsgi
        ... @with_request_args(actions=[unicode])
        ... def app(request, actions):
        ...     return Response([
        ...         u', '.join(actions)
        ...     ])
        ... 
        >>> print TestApp(app).get('/', QUERY_STRING='actions=up;actions=up;actions=and+away%21')
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        up, up, and away!

    """

    def decorator(func):
        """
        Decorate function ``func``.
        """

        f_args, f_varargs, f_varkw, f_defaults = inspect.getargspec(func)

        for arg in argspec:
            if arg not in f_args and f_varkw is None:
                raise AssertionError(
                    "with_request_args parameter %r missing from function signature" % (
                        arg,
                    )
                )

        # Produce a mapping of { argname: default }
        if f_defaults is None:
            f_defaults = []
        defaults = dict(zip(f_args[-len(f_defaults):], f_defaults))

        def decorated(request, *args, **kwargs):
            """
            Call ``func`` with arguments extracted from ``request``.
            """

            args = (request,) + args
            given_arguments = dict(
                zip(f_args[:len(args)], args)
            )
            given_arguments.update(kwargs)
            newargs = given_arguments.copy()

            for name, type_fn in argspec.items():
                try:
                    try:
                        value = given_arguments[name]
                    except KeyError:
                        if isinstance(type_fn, list):
                            value = request.form.getlist(name)
                        else:
                            value = request.form[name]

                    try:
                        if isinstance(type_fn, list):
                            value = [ cast(v) for cast, v in zip(itertools.cycle(type_fn), value) ]
                        else:
                            value = type_fn(value)
                    except ValueError, e:
                        raise RequestArgsConversionError(
                            "Could not convert parameter %r to requested type (%s)" % (
                                name, e.args[0]
                            )
                        )

                except KeyError:
                    try:
                        value = defaults[name]
                    except KeyError:
                        raise RequestArgsKeyError(name)

                newargs[name] = value

            return func(**newargs)

        return wraps(func)(decorated)

    return decorator

def overlay(*args):
    u"""
    Run each application given in ``*args`` in turn and return the response from
    the first that does not return a 404 response.
    """

    def app(environ, start_response):
        """
        WSGI callable that will iterate through each application in ``args``
        and return the first that does not return a 404 status.
        """
        for app in args:
            response = Response.from_wsgi(app, environ, start_response)
            result = response(environ, start_response)
            if response.status[:3] != '404':
                return result
            else:
                close = getattr(result, 'close', None)
                if close is not None:
                    close()
        return Response.not_found()(environ, start_response)
    return app

class StartResponseWrapper(object):
    """
    Wrapper class for the ``start_response`` callable, which allows middleware
    applications to intercept and interrogate the proxied start_response arguments.

    Synopsis::

        >>> from pesto.testing import TestApp
        >>> def my_wsgi_app(environ, start_response):
        ...     start_response('200 OK', [('Content-Type', 'text/plain')])
        ...     return ['Whoa nelly!']
        ...
        >>> def my_other_wsgi_app(environ, start_response):
        ...     responder = StartResponseWrapper(start_response)
        ...     result = my_wsgi_app(environ, responder)
        ...     print "Got status", responder.status
        ...     print "Got headers", responder.headers
        ...     responder.call_start_response()
        ...     return result
        ...
        >>> result = TestApp(my_other_wsgi_app).get('/')
        Got status 200 OK
        Got headers [('Content-Type', 'text/plain')]

    See also ``Response.from_wsgi``, which takes a wsgi callable, environ and
    start_response, and returns a ``Response`` object, allowing the client to
    further interrogate and customize the WSGI response.

    Note that it is usually not advised to use this directly in middleware as
    start_response may not be called directly from the WSGI application, but
    rather from the iterator it returns. In this case the middleware may need
    logic to accommodate this. It is usually safer to use
    ``Response.from_wsgi``, which takes this into account.
    """

    def __init__(self, start_response):
        self.start_response = start_response
        self.status = None
        self.headers = []
        self.called = False
        self.buf = StringIO()
        self.exc_info = None

    def __call__(self, status, headers, exc_info=None):
        """
        Dummy WSGI ``start_response`` function that stores the arguments for
        later use.
        """
        self.status = status
        self.headers = headers
        self.exc_info = exc_info
        self.called = True
        return self.buf.write

    def call_start_response(self):
        """
        Invoke the wrapped WSGI ``start_response`` function.
        """
        try:
            write = self.start_response(
                self.status,
                self.headers,
                self.exc_info
            )
            write(self.buf.getvalue())
            return write
        finally:
            # Avoid dangling circular ref
            self.exc_info = None

class ClosingIterator(object):
    """
    Wrap an WSGI iterator to allow additional close functions to be called on
    application exit.

    Synopsis::

        >>> from pesto.testing import TestApp
        >>> class filelikeobject(object):
        ...
        ...     def read(self):
        ...         print "file read!"
        ...         return ''
        ...
        ...     def close(self):
        ...         print "file closed!"
        ...
        >>> def app(environ, start_response):
        ...     f = filelikeobject()
        ...     start_response('200 OK', [('Content-Type', 'text/plain')])
        ...     return ClosingIterator(iter(f.read, ''), f.close)
        ...
        >>> m = TestApp(app).get('/')
        file read!
        file closed!

    """

    def __init__(self, iterable, *close_funcs):
        """
        Initialize a ``ClosingIterator`` to wrap iterable ``iterable``, and
        call any functions listed in ``*close_funcs`` on the instance's
        ``.close`` method.
        """
        self.__dict__['_iterable'] = iterable
        self.__dict__['_next'] = iter(self._iterable).next
        self.__dict__['_close_funcs'] = close_funcs
        iterable_close = getattr(self._iterable, 'close', None)
        if iterable_close is not None:
            self.__dict__['_close_funcs'] = (iterable_close,) + close_funcs
        self.__dict__['_closed'] = False

    def __iter__(self):
        """
        ``__iter__`` method
        """
        return self

    def next(self):
        """
        Return the next item from ``iterator``
        """
        return self._next()

    def close(self):
        """
        Call all close functions listed in ``*close_funcs``.
        """
        self.__dict__['_closed'] = True
        for func in self._close_funcs:
            func()

    def __getattr__(self, attr):
        return getattr(self._iterable, attr)

    def __setattr__(self, attr, value):
        return getattr(self._iterable, attr, value)

    def __del__(self):
        """
        Emit a warning if the iterator is deleted with ``close`` having been
        called.
        """
        if not self._closed:
            import warnings
            warnings.warn("%r deleted without close being called" % (self,))

