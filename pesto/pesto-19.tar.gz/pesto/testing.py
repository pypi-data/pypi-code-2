# Copyright (c) 2007-2010 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
pesto.testing
-------------

Test utilities for WSGI applications.
"""


from itertools import chain
from wsgiref.validate import validator as wsgi_validator
from StringIO import StringIO
from shutil import copyfileobj
from urlparse import urlparse

from pesto.response import Response
from pesto.request import Request
from pesto.wsgiutils import make_query

CRLF = '\r\n'

class MockResponse(Response):
    """
    Response class with some extra methods to facilitate testing output of
    applications
    """

    def __init__(self, content=None, status="200 OK", headers=None, onclose=None, add_default_content_type=True, **kwargs):
        super(MockResponse, self).__init__(
            content,
            status,
            headers,
            onclose,
            add_default_content_type,
            **kwargs
        )
        # Buffer the content iterator to make sure that it is not exhausted
        # when inspecting it through the various debug methods
        self._content = list(content)
        if getattr(content, 'close', None):
            content.close()

    def __str__(self):
        """
        Return a string representation of the entire response
        """
        return ''.join(
            chain(
                ['%s\r\n' % (self.status,)],
                ('%s: %s\r\n' % (k, v) for k, v in self.headers),
                ['\r\n'],
                self.content
            )
        )

    def text(self):
        """
        Return a string representation of the entire response, using newlines
        to separate headers, rather than the CRLF required by the HTTP spec.
        """
        return ''.join(
            chain(
                ['%s\n' % (self.status,)],
                ('%s: %s\n' % (k, v) for k, v in self.headers),
                ['\n'],
                self.content
            )
        )


    @property
    def body(self):
        """
        Content part as a single string
        """
        return ''.join(self.content)

class TestApp(object):

    response_class = MockResponse

    environ_defaults = {
        'SCRIPT_NAME': "",
        'PATH_INFO': "",
        'QUERY_STRING': "",
        'SERVER_NAME': "localhost",
        'SERVER_PORT': "80",
        'SERVER_PROTOCOL': "HTTP/1.0",
        'REMOTE_ADDR': '127.0.0.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    def __init__(self, app, charset='utf-8', **environ_defaults):

        self.app = app
        self.charset = charset
        self.environ_defaults = self.environ_defaults.copy()
        self.environ_defaults.update(**environ_defaults)

    @classmethod
    def make_environ(cls, REQUEST_METHOD='GET', PATH_INFO='', wsgi_input='', **kwargs):
        """
        Generate a WSGI environ suitable for testing applications

        Example usage::

            >>> from pprint import pprint
            >>> pprint(make_environ(PATH_INFO='/xyz')) # doctest: +ELLIPSIS
            {'PATH_INFO': '/xyz',
             'QUERY_STRING': '',
             'REMOTE_ADDR': '127.0.0.1',
             'REQUEST_METHOD': 'GET',
             'SCRIPT_NAME': '',
             'SERVER_NAME': 'localhost',
             'SERVER_PORT': '80',
             'SERVER_PROTOCOL': 'HTTP/1.0',
             'wsgi.errors': <StringIO.StringIO instance at 0x...>,
             'wsgi.input': <StringIO.StringIO instance at 0x...>,
             'wsgi.multiprocess': False,
             'wsgi.multithread': False,
             'wsgi.run_once': False,
             'wsgi.url_scheme': 'http',
             'wsgi.version': (1, 0)}

        """

        SCRIPT_NAME = kwargs.pop('SCRIPT_NAME', cls.environ_defaults["SCRIPT_NAME"])

        if SCRIPT_NAME and SCRIPT_NAME[-1] == "/":
            SCRIPT_NAME = SCRIPT_NAME[:-1]
            PATH_INFO = "/" + PATH_INFO

        environ = cls.environ_defaults.copy()
        environ.update(kwargs)
        for key, value in kwargs.items():
            environ[key.replace('wsgi_', 'wsgi.')] = value

        if isinstance(wsgi_input, basestring):
            wsgi_input = StringIO(wsgi_input)

        environ.update({
            'REQUEST_METHOD': REQUEST_METHOD,
            'SCRIPT_NAME': SCRIPT_NAME,
            'PATH_INFO': PATH_INFO,
            'wsgi.input': wsgi_input,
            'wsgi.errors': StringIO(),
        })

        if environ['SCRIPT_NAME'] == '/':
            environ['SCRIPT_NAME'] = ''
            environ['PATH_INFO'] = '/' + environ['PATH_INFO']

        while PATH_INFO.startswith('//'):
            PATH_INFO = PATH_INFO[1:]

        return environ

    def _request(self, REQUEST_METHOD, PATH_INFO="", **kwargs):
        """
        Generate a WSGI request of HTTP method ``REQUEST_METHOD`` and pass it
        to the application being tested.
        """
        environ = self.make_environ(REQUEST_METHOD, PATH_INFO, **kwargs)

        if '?' in environ['PATH_INFO']:
            environ['PATH_INFO'], querystring = environ['PATH_INFO'].split('?', 1)
            if environ.get('QUERY_STRING'):
                environ['QUERY_STRING'] += querystring
            else:
                environ['QUERY_STRING'] = querystring

        app = wsgi_validator(self.app)
        return self.response_class.from_wsgi(app, environ, self.start_response)

    def get(self, PATH_INFO='/', data=None, charset='UTF-8', **kwargs):
        """
        Make a GET request to the application and return the response.
        """
        if data is not None:
            kwargs.setdefault('QUERY_STRING', make_query(data, charset=charset))

        return self._request(
            'GET',
            PATH_INFO=PATH_INFO,
            **kwargs
        )

    def start_response(self, status, headers, exc_info=None):
        """
        WSGI start_response method
        """

    def post(self, PATH_INFO='/', data=None, charset='UTF-8', **kwargs):
        """
        Make a POST request to the application and return the response.
        """
        if data is None:
            data = {}

        data = make_query(data, charset=charset)
        wsgi_input = StringIO(data)
        wsgi_input.seek(0)

        return self._request(
            'POST',
            PATH_INFO=PATH_INFO,
            CONTENT_TYPE="application/x-www-form-urlencoded",
            CONTENT_LENGTH=str(len(data)),
            wsgi_input=wsgi_input,
        )

    def post_multipart(self, PATH_INFO='/', data=None, files=None, charset='UTF-8', **kwargs):
        """
        Create a MockWSGI configured to post multipart/form-data to the given URI.

        This is usually used for mocking file uploads

        data
            dictionary of post data
        files
            list of ``(name, filename, content_type, data)`` tuples. ``data``
            may be either a byte string, iterator or file-like object.
        """

        boundary = '----------------------------------------BoUnDaRyVaLuE'
        if data is None:
            data = {}
        if files is None:
            files = []

        items = chain(
            (
                (
                    [
                        ('Content-Disposition',
                         'form-data; name="%s"' % (name,))
                    ],
                    data.encode(charset)
                ) for name, data in data.items()
            ), (
                (
                    [
                        ('Content-Disposition',
                         'form-data; name="%s"; filename="%s"' % (name, fname)),
                        ('Content-Type', content_type)
                    ], data
                ) for name, fname, content_type, data in files
            )
        )
        post_data = StringIO()
        post_data.write('--' + boundary)
        for headers, data in items:
            post_data.write(CRLF)
            for name, value in headers:
                post_data.write('%s: %s%s' % (name, value, CRLF))
            post_data.write(CRLF)
            if hasattr(data, 'read'):
                copyfileobj(data, post_data)
            elif isinstance(data, str):
                post_data.write(data)
            else:
                for chunk in data:
                    post_data.write(chunk)
            post_data.write(CRLF)
            post_data.write('--' + boundary)
        post_data.write('--' + CRLF)
        length = post_data.tell()
        post_data.seek(0)
        kwargs.setdefault('CONTENT_LENGTH', str(length))
        return self._request(
            'POST',
            PATH_INFO,
            CONTENT_TYPE='multipart/form-data; boundary=%s' % boundary,
            wsgi_input=post_data,
            **kwargs
        )

make_environ = TestApp.make_environ

class MockRequest(object):
    """
    A mock object for testing WSGI applications

    Synopsis::

        >>> from pesto.core import to_wsgi
        >>> from pesto.response import Response
        >>> mock = MockWSGI('http://www.example.com/nelly')
        >>> mock.request.request_uri
        'http://www.example.com/nelly'
        >>> def app(request):
        ...     return Response(
        ...         content_type = 'text/html; charset=UTF-8',
        ...         x_whoa = 'Nelly',
        ...         content = ['Yop!']
        ...     )
        >>> result = mock.run(to_wsgi(app)) #doctest: +ELLIPSIS
        <pesto.wsgiutils.MockWSGI object at 0x...>
        >>> mock.headers
        [('Content-Type', 'text/html; charset=UTF-8'), ('X-Whoa', 'Nelly')]
        >>> mock.output
        ['Yop!']
        >>> print str(mock)
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        X-Whoa: Nelly\r
        \r
        Yop!
        >>>
    """

    def __init__(self, url=None, wsgi_input=None, SCRIPT_NAME='/', charset=None, **environ):

        from pesto.core import to_wsgi

        self.status = None
        self.headers = None
        self.output = None
        self.exc_info = None
        if wsgi_input is not None:
            self.wsgi_input = wsgi_input
        else:
            self.wsgi_input = StringIO()
        self.wsgi_errors = StringIO()

        self.environ = {
            'REQUEST_METHOD'    : "GET",
            'SCRIPT_NAME'       : "/",
            'PATH_INFO'         : "",
            'QUERY_STRING'      : "",
            'CONTENT_TYPE'      : "",
            'CONTENT_LENGTH'    : "",
            'SERVER_NAME'       : "localhost",
            'SERVER_PORT'       : "80",
            'SERVER_PROTOCOL'   : "HTTP/1.0",
            'REMOTE_ADDR'       : "127.0.0.1",
            'wsgi.version'      : (1, 0),
            'wsgi.url_scheme'   : "http",
            'wsgi.input'        : self.wsgi_input,
            'wsgi.errors'       : self.wsgi_errors,
            'wsgi.multithread'  : False,
            'wsgi.multiprocess' : False,
            'wsgi.run_once'     : False,
        }
        self.mockapp = to_wsgi(lambda request: Response(['ok']))

        if url is not None:
            scheme, netloc, path, params, query, fragment = urlparse(url)
            if scheme == '':
                scheme = 'http'
            if netloc == '':
                netloc = 'example.org'
            if ':' in netloc:
                server, port = netloc.split(':')
            else:
                if scheme == 'https':
                    port = '443'
                else:
                    port = '80'
                server = netloc

            assert path.startswith(SCRIPT_NAME)
            PATH_INFO = path[len(SCRIPT_NAME):]
            if SCRIPT_NAME and SCRIPT_NAME[-1] == "/":
                SCRIPT_NAME = SCRIPT_NAME[:-1]
                PATH_INFO = "/" + PATH_INFO

            self.environ.update({
                'wsgi.url_scheme' : scheme,
                'SERVER_NAME'     : server,
                'SERVER_PORT'     : port,
                'SCRIPT_NAME'     : SCRIPT_NAME,
                'QUERY_STRING'    : query,
                'PATH_INFO'       : PATH_INFO,
            })

        self.environ.update(environ)

        if self.environ['SCRIPT_NAME'] == '/':
            self.environ['SCRIPT_NAME'] = ''
            self.environ['PATH_INFO'] = '/' + self.environ['PATH_INFO']

        self.request  = Request(self.environ)
        if charset is not None:
            self.request.charset = charset

        self.buf = StringIO()


