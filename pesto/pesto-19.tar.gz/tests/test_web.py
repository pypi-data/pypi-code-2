# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import logging
from StringIO import StringIO
from urlparse import urlparse
from urllib import quote
import re
import time
from tempfile import NamedTemporaryFile

import pesto
from pesto.wsgiutils import make_query
from pesto.testing import TestApp, make_environ
from pesto.response import Response
from pesto.request import Request
from pesto.core import to_wsgi
from pesto.cookie import Cookie
from pesto.dispatch import dispatcher_app
from pesto.httputils import RequestParseError

from nose.tools import assert_equal, assert_true, assert_raises

def test_response_header():
    @to_wsgi
    def app(request):
        return Response(
            x_myheader=['Foo', 'Bar']
        )
    response = TestApp(app).get('/')
    assert_equal(response.get_header('X-Myheader'), 'Bar,Foo')

def test_add_response_header():
    @to_wsgi
    def app(request):
        res = Response(
            x_myheader='Foo'
        )
        return res.add_header('X-Myheader', 'Bar')
    response = TestApp(app).get('/')
    assert_equal(response.get_header('X-Myheader'), 'Bar,Foo')

def test_default_content_type_header():
    @to_wsgi
    def app(request):
        return Response()
    assert_equal(TestApp(app).get('/').get_header('Content-Type'), 'text/html; charset=UTF-8')

def test_set_content_type_header():
    @to_wsgi
    def app(request):
        return Response(content_type='text/rtf; charset=ISO-8859-1')
    assert_equal(TestApp(app).get('/').get_header('Content-Type'), 'text/rtf; charset=ISO-8859-1')

def test_redirect():
    @to_wsgi
    def app(request):
        return Response.redirect('/new_location', request)
    response = TestApp(app).get('/')
    assert 'http://localhost/new_location' in response.body
    assert_equal(response.get_header('Location'), 'http://localhost/new_location')
    assert_equal(response.status, '302 Found')

def test_not_found():
    @to_wsgi
    def app(request):
        return Response.not_found()
    assert 'not found' in TestApp(app).get('/').body.lower()

def test_method_not_allowed():
    @to_wsgi
    def app(request):
        return Response.method_not_allowed(valid_methods=('PUT', 'DELETE'))
    response = TestApp(app).get('/')
    assert 'not allowed' in response.body.lower()
    assert_equal(response.status, '405 Method Not Allowed')
    assert_equal(response.get_header('Allow'), 'PUT,DELETE')

def test_set_cookie():
    @to_wsgi
    def app(request):
        return Response(set_cookie=Cookie(name='fruit', value='banana'))
    assert_equal(
        TestApp(app).get().get_header('Set-Cookie'),
        'fruit=banana;Version=1'
    )

def test_method_not_allowed_dispatcher():
    import logging; logging.getLogger().setLevel(logging.DEBUG)
    dispatcher = dispatcher_app()

    @dispatcher.match('/blah', 'DELETE', 'PUT')
    def app(request):
        return Response.method_not_allowed(request)

    response = TestApp(dispatcher).get('/blah')
    assert 'not allowed' in response.body.lower()
    assert_equal(response.status, "405 Method Not Allowed")
    assert_equal(response.get_header('Allow'), 'PUT,DELETE')

def test_current_request():
    r1 = Request(make_environ())
    r2 = Request(make_environ())
    assert r1 is not pesto.currentrequest()
    assert r2 is pesto.currentrequest()

def test_current_request_threaded():

    import threading

    r1 = Request(make_environ())

    def thread_test():
        r2 = Request(make_environ())
        assert r2 is pesto.currentrequest()

    t = threading.Thread(target=thread_test)
    t.start()
    assert r1 is pesto.currentrequest()
    t.join()


def test_request_uri():

    request = Request(make_environ(SCRIPT_NAME='/foo', PATH_INFO='/bar', HTTP_HOST='localhost:80'))
    assert_equal(request.request_uri, "http://localhost/foo/bar")

    request = Request(make_environ(SCRIPT_NAME='/foo/bar', PATH_INFO='', HTTP_HOST='localhost:80'))
    assert_equal(request.request_uri, "http://localhost/foo/bar")

    request = Request(make_environ(SCRIPT_NAME='/', PATH_INFO='foo/bar', HTTP_HOST='localhost:80'))
    assert_equal(request.request_uri, "http://localhost/foo/bar")

def test_request_path():

    request = Request(make_environ(SCRIPT_NAME='/foo', PATH_INFO='/bar', HTTP_HOST='localhost:80'))
    assert_equal(request.request_path, "/foo/bar")

    request = Request(make_environ(SCRIPT_NAME='/foo/bar', PATH_INFO='', HTTP_HOST='localhost:80'))
    assert_equal(request.request_path, "/foo/bar")

    request = Request(make_environ(SCRIPT_NAME='/', PATH_INFO='foo/bar', HTTP_HOST='localhost:80'))
    assert_equal(request.request_path, "/foo/bar")

def test_form():

    request = Request(make_environ(QUERY_STRING='foo=bar'))
    assert_equal(request.get('foo'), u'bar')
    assert_equal(request['foo'], u'bar')
    assert_equal(request.get('fuz'), None)

    request = Request(make_environ(QUERY_STRING='foo=bar&foo=baz'))
    assert_equal(request.get('foo'), u'bar')
    assert_equal(request['foo'], u'bar')
    assert_equal(request.getlist('foo'), [u'bar', u'baz'])

def test_remote_addr():
    request = Request(make_environ(REMOTE_ADDR="1.2.3.4", HTTP_X_FORWARDED_FOR="4.3.2.1"))
    assert request.remote_addr == "1.2.3.4"

def test_mock_post():
    @to_wsgi
    def app(request):
        return Response(content=[request.request_method, request.get('foo')])
    assert TestApp(app).post('/', data={'foo': 'bar'}).content == ['POST', 'bar']

def test_mock_get():
    @to_wsgi
    def app(request):
        return Response(content=[request.request_method, request.get('foo')])
    assert TestApp(app).get('/', data={'foo': 'baz'}).content == ['GET', 'baz']

def test_encoding():

    # Test UTF-8 decoding works (this should be the default)
    request = Request(make_environ(QUERY_STRING=make_query(foo=u'\xa0'.encode('utf8'))))
    assert_equal(request.get('foo'), u'\xa0')

    # Force a different encoding
    request = Request(make_environ(QUERY_STRING=make_query(foo=u'\xa0'.encode('utf7'))))
    request.charset = 'utf-7'
    assert_equal(request.get('foo'), u'\xa0')

    # Force an incorrect encoding
    request = Request(make_environ(QUERY_STRING=make_query(foo=u'\xa0'.encode('utf8'))))
    request.charset = 'utf-7'
    assert_raises(RequestParseError, request.get, 'foo')

def test_form_getters():

    alpha = u'\u03b1' # Greek alpha
    beta = u'\u03b2' # Greek beta
    gamma = u'\u03b3' # Greek gamma

    request = Request(make_environ(
        QUERY_STRING='foo=%s;foo=%s;bar=%s' % (
            quote(alpha.encode('utf-8')),
            quote(beta.encode('utf-8')),
            quote(gamma.encode('utf-8'))
        )
    ))
    assert request.get('foo') == request.form.get('foo') == alpha
    assert request.getlist('foo') == request.form.getlist('foo') == [alpha, beta]

    assert request.get('cheese') == request.form.get('cheese') == None
    assert request.getlist('cheese') == request.form.getlist('cheese') == []

    assert request.get('bar') == request.form.get('bar') == gamma
    assert request.getlist('bar') == request.form.getlist('bar') == [gamma]


def test_file_test():

    filename = 'test.txt'
    filedata = 'whoa nelly!\n'
    content_type = 'text/plain'
    boundary = '---------------------------1234'

    post_data = (
          '--%s\r\n' % boundary
        + 'Content-Disposition: form-data; name="uploaded_file"; filename="%s"\r\n' % filename
        + 'Content-Type: %s\r\n' % content_type
        + '\r\n'
        + filedata + '\r\n--' + boundary + '--\r\n'
    )
    request = Request(make_environ(
        wsgi_input=StringIO(post_data),
        REQUEST_METHOD='POST',
        CONTENT_TYPE='multipart/form-data; boundary=%s' % boundary,
        CONTENT_LENGTH=str(len(post_data)),
    ))
    assert_equal(request.files['uploaded_file'].filename, filename)
    assert_equal(request.files['uploaded_file'].headers['Content-Type'], content_type)

    ntf = NamedTemporaryFile()
    request.files['uploaded_file'].save(ntf)
    ntf.flush()

    f = open(ntf.name, 'r')
    testdata = f.read()
    f.close()
    ntf.close()
    assert_equal(testdata, filedata)

    ntf = NamedTemporaryFile()
    request.files['uploaded_file'].save(ntf.name)

    f = open(ntf.name, 'r')
    testdata = f.read()
    f.close()
    ntf.close()
    assert_equal(testdata, filedata)


def test_response_get_headers():

    response = Response(['whoa nelly!'], content_type='text/plain', x_test_header=["1", "2"])
    assert_equal(response.get_headers('content-type'), ['text/plain'])
    assert_equal(response.get_headers('x-test-header'), ['1', '2'])
    assert_equal(response.get_headers('X-Test-Header'), ['1', '2'])
    assert_equal(response.get_headers('x-does-not-exist'), [])

def test_response_get_headers():

    response = Response(['whoa nelly!'], content_type='text/plain', x_test_header=["1", "2"])
    assert_equal(response.get_header('content-type'), 'text/plain')
    assert_equal(response.get_header('x-test-header'), '1,2')
    assert_equal(response.get_header('X-Test-Header'), '1,2')
    assert_equal(response.get_header('x-does-not-exist', 'boo!'), 'boo!')

def test_from_wsgi():

    from pesto import to_wsgi
    def pesto_app(request):

        def content():
            yield "<html>"
            yield "Yop!"
            yield "</html>"

        return Response(content(), content_type='text/html', x_counter="1")

    wsgi_app = to_wsgi(pesto_app)
    def middleware(app):
        def middleware(environ, start_response):
            response = Response.from_wsgi(app, environ, start_response)
            return response.replace(x_counter='2')(environ, start_response)
        return middleware

    wsgi_app = middleware(wsgi_app)
    response = TestApp(wsgi_app).get('/')
    assert_equal(
        str(response),
        '200 OK\r\n'
        'Content-Type: text/html\r\n'
        'X-Counter: 2\r\n'
        '\r\n'
        '<html>Yop!</html>'
    )

def test_make_uri_quoting():
    request = Request(make_environ(HTTP_HOST='example.com', SCRIPT_NAME='/path with spaces/page one'))
    assert_equal(request.make_uri(), 'http://example.com/path%20with%20spaces/page%20one')
    assert_equal(request.make_uri(path='./page two'), 'http://example.com/path%20with%20spaces/page%20two')
    assert_equal(request.make_uri(path='/page three'), 'http://example.com/page%20three')


def test_onclose():

    closed = []
    @to_wsgi
    def app(request):
        def closeme():
            closed.append(1)
        def closeme2():
            closed.append(2)

        def content():
            yield "<html>"
            yield "Yop!"
            yield "</html>"

        return Response(content(), onclose=closeme).add_onclose(closeme2)

    def middleware(app):
        def middleware(environ, start_response):
            response = Response.from_wsgi(app, environ, start_response)
            return response.replace(x_counter='2')(environ, start_response)
        return middleware
    TestApp(app).get()
    assert_equal(closed, [1, 2])

def test_onclose_from_wsgi():
    """
    Check close events are propagated from an upstream WSGI app
    """
    closed = []

    class MyApp(object):

        def __init__(self):
            pass

        def __iter__(self):
            yield "blah"
            yield "blah"
            yield "blah"

        def __call__(self, environ, start_response):
            start_response('200 OK', [])
            return self

        def close(self):
            closed.append(1)

    def middleware(app):
        def middleware(environ, start_response):
            r = Response.from_wsgi(app, environ, start_response)
            return r.replace(content='blah')(environ, start_response)
        return middleware

    TestApp(middleware(MyApp())).get()
    assert_equal(closed, [1])


def test_delayed_start_response():

    # Most WSGI applications call start_response before returning the iterable.
    # However, an application may also call start_response in the first iteration.

    closed = []

    class wsgiapp(object):

        def __init__(self):
            self.iter_count = 0
            self._next = iter(['cat', 'sat', 'mat']).next

        def __call__(self, environ, start_response):
            self.environ = environ
            self.start_response = start_response
            return self

        def __iter__(self):
            return self

        def next(self):
            if self.iter_count == 0:
                self.start_response('200 hoopy', [])
            self.iter_count += 1
            return self._next()

        def close(self):
            closed.append(1)

    def middleware(app):
        def middleware(environ, start_response):
            r = Response.from_wsgi(app, environ, start_response)
            return r(environ, start_response)
        return middleware

    response = TestApp(middleware(wsgiapp())).get()
    assert_equal(response.status, '200 hoopy')
    assert_equal(closed, [1])

def test_to_wsgi_as_method_decorator():

    class A(object):

        def __init__(self, data):
            self.data = data

        @to_wsgi
        def handler(self, request):
            return Response([self.data], content_type='text/plain')

    response = TestApp(A('abcdef').handler).get()
    assert_equal(list(response.content), ['abcdef'])

