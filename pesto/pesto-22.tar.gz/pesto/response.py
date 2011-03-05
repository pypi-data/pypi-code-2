# Copyright (c) 2007-2010 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
pesto.response
--------------

Response object for WSGI applications
"""

import cgi
import datetime
import re
import urllib
import copy
from itertools import chain

from pesto import cookie

__all__ = [
    'STATUS_CONTINUE', 'STATUS_SWITCHING_PROTOCOLS',
    'STATUS_OK', 'STATUS_CREATED', 'STATUS_ACCEPTED',
    'STATUS_NON_AUTHORITATIVE_INFORMATION', 'STATUS_NO_CONTENT',
    'STATUS_RESET_CONTENT', 'STATUS_PARTIAL_CONTENT',
    'STATUS_MULTIPLE_CHOICES', 'STATUS_MOVED_PERMANENTLY', 'STATUS_FOUND',
    'STATUS_SEE_OTHER', 'STATUS_NOT_MODIFIED', 'STATUS_USE_PROXY',
    'STATUS_TEMPORARY_REDIRECT', 'STATUS_BAD_REQUEST', 'STATUS_UNAUTHORIZED',
    'STATUS_PAYMENT_REQUIRED', 'STATUS_FORBIDDEN', 'STATUS_NOT_FOUND',
    'STATUS_METHOD_NOT_ALLOWED', 'STATUS_NOT_ACCEPTABLE',
    'STATUS_PROXY_AUTHENTICATION_REQUIRED', 'STATUS_REQUEST_TIME_OUT',
    'STATUS_CONFLICT', 'STATUS_GONE', 'STATUS_LENGTH_REQUIRED',
    'STATUS_PRECONDITION_FAILED', 'STATUS_REQUEST_ENTITY_TOO_LARGE',
    'STATUS_REQUEST_URI_TOO_LARGE', 'STATUS_UNSUPPORTED_MEDIA_TYPE',
    'STATUS_REQUESTED_RANGE_NOT_SATISFIABLE', 'STATUS_EXPECTATION_FAILED',
    'STATUS_INTERNAL_SERVER_ERROR', 'STATUS_NOT_IMPLEMENTED',
    'STATUS_BAD_GATEWAY', 'STATUS_SERVICE_UNAVAILABLE',
    'STATUS_GATEWAY_TIME_OUT', 'STATUS_HTTP_VERSION_NOT_SUPPORTED',
    'Response'
]


# All HTTP/1.1 status codes as listed in http://www.ietf.org/rfc/rfc2616.txt
HTTP_STATUS_CODES = {
      100 : 'Continue',
      101 : 'Switching Protocols',
      200 : 'OK',
      201 : 'Created',
      202 : 'Accepted',
      203 : 'Non-Authoritative Information',
      204 : 'No Content',
      205 : 'Reset Content',
      206 : 'Partial Content',
      300 : 'Multiple Choices',
      301 : 'Moved Permanently',
      302 : 'Found',
      303 : 'See Other',
      304 : 'Not Modified',
      305 : 'Use Proxy',
      307 : 'Temporary Redirect',
      400 : 'Bad Request',
      401 : 'Unauthorized',
      402 : 'Payment Required',
      403 : 'Forbidden',
      404 : 'Not Found',
      405 : 'Method Not Allowed',
      406 : 'Not Acceptable',
      407 : 'Proxy Authentication Required',
      408 : 'Request Time-out',
      409 : 'Conflict',
      410 : 'Gone',
      411 : 'Length Required',
      412 : 'Precondition Failed',
      413 : 'Request Entity Too Large',
      414 : 'Request-URI Too Large',
      415 : 'Unsupported Media Type',
      416 : 'Requested range not satisfiable',
      417 : 'Expectation Failed',
      500 : 'Internal Server Error',
      501 : 'Not Implemented',
      502 : 'Bad Gateway',
      503 : 'Service Unavailable',
      504 : 'Gateway Time-out',
      505 : 'HTTP Version not supported',
}

# Symbolic names for the HTTP status codes
STATUS_CONTINUE = 100
STATUS_SWITCHING_PROTOCOLS = 101
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_ACCEPTED = 202
STATUS_NON_AUTHORITATIVE_INFORMATION = 203
STATUS_NO_CONTENT = 204
STATUS_RESET_CONTENT = 205
STATUS_PARTIAL_CONTENT = 206
STATUS_MULTIPLE_CHOICES = 300
STATUS_MOVED_PERMANENTLY = 301
STATUS_FOUND = 302
STATUS_SEE_OTHER = 303
STATUS_NOT_MODIFIED = 304
STATUS_USE_PROXY = 305
STATUS_TEMPORARY_REDIRECT = 307
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_PAYMENT_REQUIRED = 402
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_METHOD_NOT_ALLOWED = 405
STATUS_NOT_ACCEPTABLE = 406
STATUS_PROXY_AUTHENTICATION_REQUIRED = 407
STATUS_REQUEST_TIME_OUT = 408
STATUS_CONFLICT = 409
STATUS_GONE = 410
STATUS_LENGTH_REQUIRED = 411
STATUS_PRECONDITION_FAILED = 412
STATUS_REQUEST_ENTITY_TOO_LARGE = 413
STATUS_REQUEST_URI_TOO_LARGE = 414
STATUS_UNSUPPORTED_MEDIA_TYPE = 415
STATUS_REQUESTED_RANGE_NOT_SATISFIABLE = 416
STATUS_EXPECTATION_FAILED = 417
STATUS_INTERNAL_SERVER_ERROR = 500
STATUS_NOT_IMPLEMENTED = 501
STATUS_BAD_GATEWAY = 502
STATUS_SERVICE_UNAVAILABLE = 503
STATUS_GATEWAY_TIME_OUT = 504
STATUS_HTTP_VERSION_NOT_SUPPORTED = 505

def encoder(stream, charset):
    r"""
    Encode a response iterator using the given character set.

    >>> list(encoder([u'Price \u00a3200'], 'latin1'))
    ['Price \xa3200']
    """
    if charset is None:
        charset = 'UTF-8'

    for chunk in stream:
        if isinstance(chunk, unicode):
            yield chunk.encode(charset)
        else:
            yield chunk


class Response(object):
    r"""
    WSGI response object.

    Example usage::

        >>> # Construct a response
        >>> response = Response(
        ...     content=['hello world\n'],
        ...     status='200 OK',
        ...     headers=[('Content-Type', 'text/plain')]
        ... )
        >>> 
        >>> # We can manipulate the response before outputting it
        >>> response = response.add_header('X-Header', 'hello!')
        >>>
        >>> # To output the response, we call it as a WSGI application
        >>> from pesto.testing import TestApp
        >>> print TestApp(response).get('/').text()
        200 OK
        Content-Type: text/plain
        X-Header: hello!
        <BLANKLINE>
        hello world
        <BLANKLINE>
        >>>

    """

    default_content_type = "text/html; charset=UTF-8"

    def __init__(self, content=None, status="200 OK", headers=None, onclose=None, add_default_content_type=True, **kwargs):
        """
        Create a new Response object.

        content
            An iterator over the response content

        status
            The WSGI status line, eg ``200 OK`` or ``404 Not Found``.

        headers
            A list of headers, eg ``[('Content-Type', 'text/plain'), ('Content-Length', 193)]``

        add_default_content_type
            If true (and the status is not 204 or 304) a default
            ``Content-Type`` header will be added if one is not provided, using
            the value of ``pesto.response.Response.default_content_type``.

        **kwargs
            Arbitrary headers, provided as keyword arguments. Replace hyphens
            with underscores where necessary.

        """

        if content is None:
            content = []
        self._content = content
        self._status = self.make_status(status)
        if onclose is None:
            self.onclose = []
        elif callable(onclose):
            self.onclose = [onclose]
        else:
            self.onclose = list(onclose)

        if headers is None:
            headers = []
        self._headers = sorted(self.make_headers(headers, kwargs))
        if self.status_code not in (204, 304) and add_default_content_type:
            for key, value in self._headers:
                if key == 'Content-Type':
                    break
            else:
                self._headers.insert(0, ('Content-Type', self.default_content_type))

    def __call__(self, environ, start_response):
        """
        WSGI callable. Calls ``start_response`` with assigned headers and
        returns an iterator over ``content``.
        """
        start_response(
            self.status,
            self.headers,
        )
        result = _copy_close(self.content, encoder(self.content, self.charset))
        if self.onclose:
            result = ClosingIterator(result, *self.onclose)
        return result


    def add_onclose(self, *funcs):
        """
        Add functions to be called as part of the response iterators ``close``
        method.
        """
        return self.__class__(
            self.content,
            self.status,
            self.headers,
            self.onclose + list(funcs),
            add_default_content_type=False
        )

    @classmethod
    def from_wsgi(cls, wsgi_callable, environ, start_response):
        """
        Return a ``Response`` object constructed from the result of calling
        ``wsgi_callable`` with the given ``environ`` and ``start_response``
        arguments.
        """
        if isinstance(wsgi_callable, PestoWSGIApplication):
            return wsgi_callable.pesto_app(
                Request(environ),
                *wsgi_callable.app_args,
                **wsgi_callable.app_kwargs
            )
        responder = StartResponseWrapper(start_response)
        content = wsgi_callable(environ, responder)
        if responder.buf.tell():
            content = _copy_close(content, chain(content, [responder.buf.getvalue()]))

        if responder.called:
            return cls(content, responder.status, headers=responder.headers)

        # Iterator has not called start_response yet. Call content.next()
        # to force the application to call start_response
        try:
            chunk = content.next()
        except StopIteration:
            return cls(content, responder.status, headers=responder.headers)
        except Exception:
            close = getattr(content, 'close', None)
            if close is not None:
                close()
            raise
        content = _copy_close(content, chain([chunk], content))
        return cls(
            content,
            responder.status,
            headers=responder.headers
        )

    @classmethod
    def make_status(cls, status):
        """
        Return a status line from the given status, which may be a simple integer.

        Example usage::

            >>> Response.make_status(200)
            '200 OK'

        """
        if isinstance(status, int):
            return '%d %s' % (status, HTTP_STATUS_CODES[status])
        return status

    @classmethod
    def make_headers(cls, header_list, header_dict):
        """
        Return a list of header (name, value) tuples from the combination of
        the header_list and header_dict.

        Example usage::

            >>> Response.make_headers(
            ...     [('Content-Type', 'text/html')],
            ...     {'content_length' : 54}
            ... )
            [('Content-Type', 'text/html'), ('Content-Length', '54')]

            >>> Response.make_headers(
            ...     [('Content-Type', 'text/html')],
            ...     {'x_foo' : ['a1', 'b2']}
            ... )
            [('Content-Type', 'text/html'), ('X-Foo', 'a1'), ('X-Foo', 'b2')]

        """

        headers = header_list + header_dict.items()
        headers = [
            (make_header_name(key), val) for key, val in headers if val is not None
        ]

        # Join multiple headers. [see RFC2616, section 4.2]
        newheaders = []
        for key, val in headers:
            if isinstance(val, list):
                for item in val:
                    newheaders.append((key, str(item)))
            else:
                newheaders.append((key, str(val)))
        return newheaders

    @property
    def content(self):
        """
        Iterator over the response content part
        """
        return self._content

    @property
    def headers(self):
        """
        Return a list of response headers in the format ``[(<header-name>, <value>), ...]``
        """
        return self._headers

    def get_headers(self, name):
        """
        Return the list of headers set with the given name.

        Synopsis::

            >>> r = Response(set_cookie = ['cookie1', 'cookie2'])
            >>> r.get_headers('set-cookie')
            ['cookie1', 'cookie2']

        """
        return [value for header, value in self.headers if header.lower() == name.lower()]

    def get_header(self, name, default=''):
        """
        Return the concatenated values of the named header(s) or ``default`` if
        the header has not been set.

        As specified in RFC2616 (section 4.2), multiple headers will be
        combined using a single comma.

        Example usage::

            >>> r = Response(set_cookie = ['cookie1', 'cookie2'])
            >>> r.get_header('set-cookie')
            'cookie1,cookie2'
        """
        headers = self.get_headers(name)
        if not headers:
            return default
        return ','.join(headers)

    @property
    def status(self):
        """
        HTTP status message for the response, eg ``200 OK``
        """
        return self._status

    @property
    def status_code(self):
        """
        Return the numeric status code for the response as an integer::

            >>> Response(status='404 Not Found').status_code
            404
            >>> Response(status=200).status_code
            200
        """
        return int(self._status.split(' ', 1)[0])

    @property
    def content_type(self):
        """
        Return the value of the ``Content-Type`` header if set, otherwise ``None``.
        """
        for key, val in self.headers:
            if key.lower() == 'content-type':
                return val
        return None

    def add_header(self, name, value):
        """
        Return a new response object with the given additional header.

        Synopsis::

            >>> r = Response(content_type = 'text/plain')
            >>> r.headers
            [('Content-Type', 'text/plain')]
            >>> r.add_header('Cache-Control', 'no-cache').headers
            [('Cache-Control', 'no-cache'), ('Content-Type', 'text/plain')]
        """
        return self.replace(self._content, self._status, self._headers + [(name, value)])

    def add_headers(self, headers=[], **kwheaders):
        """
        Return a new response object with the given additional headers.

        Synopsis::

            >>> r = Response(content_type = 'text/plain')
            >>> r.headers
            [('Content-Type', 'text/plain')]
            >>> r.add_headers(
            ...     cache_control='no-cache',
            ...     expires='Mon, 26 Jul 1997 05:00:00 GMT'
            ... ).headers
            [('Cache-Control', 'no-cache'), ('Content-Type', 'text/plain'), ('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')]
        """
        return self.replace(headers=self.make_headers(self._headers + headers, kwheaders))

    def remove_headers(self, *headers):
        """
        Return a new response object with the given headers removed.

        Synopsis::

            >>> r = Response(content_type = 'text/plain', cache_control='no-cache')
            >>> r.headers
            [('Cache-Control', 'no-cache'), ('Content-Type', 'text/plain')]
            >>> r.remove_headers('Cache-Control').headers
            [('Content-Type', 'text/plain')]
        """
        toremove = [ item.lower() for item in headers ]
        return self.replace(
            headers=[ h for h in self._headers if h[0].lower() not in toremove ],
        )

    def add_cookie(
        self, name, value, maxage=None, expires=None, path=None,
        secure=None, domain=None, comment=None, http_only=False, version=1
    ):
        """
        Return a new response object with the given cookie added.

        Synopsis::

            >>> r = Response(content_type = 'text/plain', cache_control='no-cache')
            >>> r.headers
            [('Cache-Control', 'no-cache'), ('Content-Type', 'text/plain')]
            >>> r.add_cookie('foo', 'bar').headers
            [('Cache-Control', 'no-cache'), ('Content-Type', 'text/plain'), ('Set-Cookie', 'foo=bar;Version=1')]
        """
        return self.replace(
            headers=self._headers + [
                (
                    'Set-Cookie',
                    cookie.Cookie(
                        name, value, maxage, expires, path,
                        secure, domain,
                        comment=comment,
                        http_only=http_only,
                        version=version
                    )
                )
            ]
        )

    def replace(self, content=None, status=None, headers=None, **kwheaders):
        """
        Return a new response object with any of content, status or headers changed.

        Synopsis::

            >>> Response(allow='GET', foo='bar', add_default_content_type=False).replace(allow='POST').headers
            [('Allow', 'POST'), ('Foo', 'bar')]

            >>> Response(allow='GET', add_default_content_type=False).replace(headers=[('allow', 'POST')]).headers
            [('Allow', 'POST')]

            >>> Response(location='http://www.google.com').replace(status=301).status
            '301 Moved Permanently'

            >>> Response(content=['donald']).replace(content=['pluto']).content
            ['pluto']

        """

        res = self

        if content is not None:
            close = getattr(self.content, 'close', None)
            onclose = self.onclose
            if close:
                onclose = [close,] + onclose
            res = res.__class__(content, res._status, res._headers, onclose=onclose, add_default_content_type=False)

        if headers is not None:
            res = res.__class__(res._content, res._status, headers, onclose=res.onclose, add_default_content_type=False)

        if status is not None:
            res = res.__class__(res._content, status, res._headers, onclose=res.onclose, add_default_content_type=False)

        if kwheaders:
            toremove = set(make_header_name(k) for k in kwheaders)
            kwheaders = self.make_headers([], kwheaders)
            res = res.__class__(
                res._content,
                res._status,
                [(key, value) for key, value in res._headers if key not in toremove] + kwheaders,
                onclose=res.onclose,
                add_default_content_type=False
            )

        return res

    def buffered(self):
        """
        Return a new response object with the content buffered into a list. This will also add a content-length header.

        Example usage::

            >>> def generate_content():
            ...     yield "one two "
            ...     yield "three four five"
            ...
            >>> Response(content=generate_content()).content # doctest: +ELLIPSIS
            <generator object ...>
            >>> Response(content=generate_content()).buffered().content
            ['one two ', 'three four five']
        """
        content = list(self.content)
        content_length = sum(map(len, content))
        return self.replace(content=content, content_length=content_length)

    @property
    def charset(
        self,
        _parser=re.compile(r'.*;\s*charset=([\w\d\-]+)', re.I).match
    ):
        for key, val in self.headers:
            if key.lower() == 'content-type':
                mo = _parser(val)
                if mo:
                    return mo.group(1)
                else:
                    return None
        return None

    @classmethod
    def not_found(cls, request=None):
        """
        Returns an HTTP not found response (404). This method also outputs the
        necessary HTML to be used as the return value for a pesto handler.

        Synopsis::

            >>> from pesto.testing import TestApp
            >>> from pesto import to_wsgi
            >>> @to_wsgi
            ... def app(request):
            ...     return Response.not_found()
            ...
            >>> print TestApp(app).get('/')
            404 Not Found\r
            Content-Type: text/html; charset=UTF-8\r
            \r
            <html>
            <body>
                <h1>Not found</h1>
                <p>The requested resource could not be found.</p>
            </body>
            </html>
        """
        return cls(
            status = STATUS_NOT_FOUND,
            content = [
                "<html>\n"
                "<body>\n"
                "    <h1>Not found</h1>\n"
                "    <p>The requested resource could not be found.</p>\n"
                "</body>\n"
                "</html>"
            ]
        )

    @classmethod
    def forbidden(cls, message='Sorry, access is denied'):
        """
        Return an HTTP forbidden response (403)::

            >>> from pesto.testing import TestApp
            >>> from pesto import to_wsgi
            >>> @to_wsgi
            ... def app(request):
            ...     return Response.forbidden()
            ...
            >>> print TestApp(app).get('/')
            403 Forbidden\r
            Content-Type: text/html; charset=UTF-8\r
            \r
            <html>
            <body>
                <h1>Sorry, access is denied</h1>
            </body>
            </html>
        """
        return cls(
            status = STATUS_FORBIDDEN,
            content = [
                "<html>\n"
                "<body>\n"
                "    <h1>" + message + "</h1>\n"
                "</body>\n"
                "</html>"
            ]
        )

    @classmethod
    def bad_request(cls, request=None):
        """
        Returns an HTTP bad request response.

        Example usage::

            >>> from pesto.testing import TestApp
            >>> from pesto import to_wsgi
            >>> @to_wsgi
            ... def app(request):
            ...     return Response.bad_request()
            ...
            >>> print TestApp(app).get('/')
            400 Bad Request\r
            Content-Type: text/html; charset=UTF-8\r
            \r
            <html><body><h1>The server could not understand your request</h1></body></html>

        """
        return cls(
            status = STATUS_BAD_REQUEST,
            content = ["<html>"
                "<body>"
                    "<h1>The server could not understand your request</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def length_required(cls, request=None):
        """
        Returns an HTTP 411 Length Required request response.

        Example usage::

            >>> from pesto.testing import TestApp
            >>> from pesto import to_wsgi
            >>> @to_wsgi
            ... def app(request):
            ...     return Response.length_required()
            ...
            >>> print TestApp(app).get('/')
            411 Length Required\r
            Content-Type: text/html; charset=UTF-8\r
            \r
            <html><body><h1>The Content-Length header was missing from your request</h1></body></html>

        """
        return cls(
            status = STATUS_LENGTH_REQUIRED,
            content = ["<html>"
                "<body>"
                    "<h1>The Content-Length header was missing from your request</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def request_entity_too_large(cls, request=None):
        """
        Returns an HTTP 413 Request Entity Too Large response.

        Example usage::

            >>> from pesto.testing import TestApp
            >>> from pesto import to_wsgi
            >>> @to_wsgi
            ... def app(request):
            ...     return Response.request_entity_too_large()
            ...
            >>> print TestApp(app).get('/')
            413 Request Entity Too Large\r
            Content-Type: text/html; charset=UTF-8\r
            \r
            <html><body><h1>Request Entity Too Large</h1></body></html>

        """
        return cls(
            status = STATUS_REQUEST_ENTITY_TOO_LARGE,
            content = ["<html>"
                "<body>"
                    "<h1>Request Entity Too Large</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def method_not_allowed(cls, valid_methods):
        """
        Returns an HTTP method not allowed response (404)::

            >>> from pesto.testing import TestApp
            >>> from pesto import to_wsgi
            >>> @to_wsgi
            ... def app(request):
            ...     return Response.method_not_allowed(valid_methods=("GET", "HEAD"))
            ...
            >>> print TestApp(app).get('/')
            405 Method Not Allowed\r
            Allow: GET,HEAD\r
            Content-Type: text/html; charset=UTF-8\r
            \r
            <html><body><h1>Method not allowed</h1></body></html>

        ``valid_methods``
            A list of HTTP methods valid for the URI requested. If ``None``,
            the dispatcher_app mechanism will be used to autogenerate a list of
            methods. This expects a dispatcher_app object to be stored in the
            wsgi environ dictionary at ``pesto.dispatcher_app``.

        ``returns``
            A ``pesto.response.Response`` object
        """

        return cls(
            status = STATUS_METHOD_NOT_ALLOWED,
            allow = ",".join(valid_methods),
            content = ["<html>"
                "<body>"
                    "<h1>Method not allowed</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def internal_server_error(cls):
        """
        Return an HTTP internal server error response (500)::

            >>> from pesto.testing import TestApp
            >>> from pesto import to_wsgi
            >>> @to_wsgi
            ... def app(request):
            ...     return Response.internal_server_error()
            ...
            >>> print TestApp(app).get('/')
            500 Internal Server Error\r
            Content-Type: text/html; charset=UTF-8\r
            \r
            <html><body><h1>Internal Server Error</h1></body></html>

        ``returns``
            A ``pesto.response.Response`` object
        """

        return cls(
            status = STATUS_INTERNAL_SERVER_ERROR,
            content = ["<html>"
                "<body>"
                    "<h1>Internal Server Error</h1>"
                "</body>"
                "</html>"
            ]
        )

    @classmethod
    def redirect(cls, location, request=None, status=STATUS_FOUND):
        """
        Return an HTTP redirect reponse.

        ``location``
            The URI of the new location. If this is relative it will be converted
            to an absolute URL based on the current request.

        ``status``
            HTTP status code for the redirect, defaulting to ``STATUS_FOUND`` (a temporary redirect)

        Synopsis::

            >>> from pesto.testing import TestApp
            >>> from pesto import to_wsgi
            >>> @to_wsgi
            ... def app(request):
            ...   return Response.redirect("/new-location", request)
            ...
            >>> print TestApp(app).get('/')
            302 Found\r
            Content-Type: text/html; charset=UTF-8\r
            Location: http://localhost/new-location\r
            \r
            <html><head></head><body>
            <h1>Page has moved</h1>
            <p><a href='http://localhost/new-location'>http://localhost/new-location</a></p>
            </body></html>

        Note that we can also do the following::

            >>> from functools import partial
            >>> from pesto.testing import TestApp
            >>> from pesto.dispatch import dispatcher_app
            >>> d = dispatcher_app()
            >>> d.match('/animals', GET=partial(Response.redirect, '/new-location'))
            >>> print TestApp(d).get('/animals')
            302 Found\r
            Content-Type: text/html; charset=UTF-8\r
            Location: http://localhost/new-location\r
            \r
            <html><head></head><body>
            <h1>Page has moved</h1>
            <p><a href='http://localhost/new-location'>http://localhost/new-location</a></p>
            </body></html>
        """
        from pesto.wsgiutils import make_absolute_url
        if '://' not in location:
            if request is None:
                request = currentrequest()
            location = str(make_absolute_url(request.environ, location))
        return Response(
            status = status,
            location = location,
            content = [
                "<html><head></head><body>\n",
                "<h1>Page has moved</h1>\n",
                "<p><a href='%s'>%s</a></p>\n" % (location, location),
                "</body></html>",
            ]
        )

def make_header_name(name):
    """
    Return a formatted header name from a python idenfier.

    Example usage::

        >>> make_header_name('content_type')
        'Content-Type'
    """
    # Common exceptions
    if name.lower() == 'etag':
        return 'ETag'
    return name.replace('_', '-').title()

def _copy_close(src, dst, marker=object()):
    """
    Copy the ``close`` attribute from ``src`` to ``dst``, which are assumed to
    be iterators.

    If it is not possible to copy the attribute over (eg for
    ``itertools.chain``, which does not support the close attribute) an
    instance of ``ClosingIterator`` is returned which will proxy calls to ``close`` as necessary.
    """

    close = getattr(src, 'close', marker)
    if close is not marker:
        try:
            setattr(dst, 'close', close)
        except AttributeError:
            return ClosingIterator(dst, close)

    return dst

from pesto.wsgiutils import StartResponseWrapper
from pesto.wsgiutils import ClosingIterator#, IteratorWrapper
from pesto.core import PestoWSGIApplication
from pesto.request import Request, currentrequest
