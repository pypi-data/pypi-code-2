# vim: set fileencoding=utf-8 :
# Copyright (c) 2007-2010 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

from nose.tools import assert_equal
from tempfile import mkstemp
from email.utils import parsedate
from os import unlink
from time import time, strftime, mktime, gmtime
from calendar import timegm
from math import floor
import os

import pesto
from pesto.request import Request
from pesto.response import Response
from pesto.wsgiutils import mount_app, use_x_forwarded, make_uri_component
from pesto.wsgiutils import make_query, overlay, with_request_args
from pesto.wsgiutils import ClosingIterator, StartResponseWrapper
from pesto.wsgiutils import normpath, serve_static_file
from pesto.testing import TestApp, make_environ
from pesto.core import PestoWSGIApplication, to_wsgi

def test_mountapp_match_order():
    """
    Regression test for bug where paths were matched in an arbitrary order,
    rather than testing the most specific paths first
    """
    def app1(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return ["app1"]

    def app2(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return ["app2"]

    m = mount_app({
        '/' : app1,
        '/a' : app2,
    })

    assert_equal(
        TestApp(m).get(SCRIPT_NAME='', PATH_INFO='/').body, "app1"
    )
    assert_equal(
        TestApp(m).get(SCRIPT_NAME='', PATH_INFO='/a').body, "app2"
    )

    m = mount_app({
        '/' : app2,
        '/a' : app1,
    })
    assert_equal(
        TestApp(m).get(SCRIPT_NAME='/', PATH_INFO='').body, "app2"
    )
    assert_equal(
        TestApp(m).get(SCRIPT_NAME='/', PATH_INFO='a').body, "app1"
    )

def test_mountapp_script_name_path_info():
    """
    Check that mount_app correctly sets the SCRIPT_NAME and PATH_INFO variables
    """
    def app1(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return ["1", e["SCRIPT_NAME"], e["PATH_INFO"]]
    def app2(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return ["2", e["SCRIPT_NAME"], e["PATH_INFO"]]
    m = mount_app({
        '/app1' : app1,
        '/app2' : app2,
    })

    assert_equal(
        TestApp(m).get(SCRIPT_NAME='/a', PATH_INFO='/app1').content,
        ["1", "/a/app1", ""]
    )

    assert_equal(
        TestApp(m).get(SCRIPT_NAME='/a', PATH_INFO='/app2').content,
        ["2", "/a/app2", ""]
    )

def test_use_x_forwarded_no_forwarding():

    def app(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return [ Request(e).request_uri, Request(e).remote_addr ]

    app = use_x_forwarded(trusted=['127.0.0.1'])(app)

    # Without the HTTP_X_FORWARDED headers, we should get back the original URI + remote address
    assert_equal(
        TestApp(app).get(HTTP_HOST='127.0.0.1:1234', REMOTE_ADDR='4.3.2.1').content,
        ['http://127.0.0.1:1234/', '4.3.2.1']
    )

def test_use_x_forwarded_forward_host():

    def app(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return [ Request(e).request_uri, Request(e).remote_addr ]

    app = use_x_forwarded(trusted=['127.0.0.1'])(app)

    # With HTTP_X_FORWARDED_HOST from a trusted IP, should override SERVER_NAME and SERVER_PORT
    assert_equal(
        TestApp(app).get(HTTP_HOST='127.0.0.1:1234', REMOTE_ADDR='127.0.0.1', HTTP_X_FORWARDED_HOST='example.org:80').content,
        ['http://example.org/', '127.0.0.1']
    )

def test_use_x_forwarded_forward_host_ssl():

    def app(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return [ Request(e).request_uri, Request(e).remote_addr ]

    app = use_x_forwarded(trusted=['127.0.0.1'])(app)

    # With HTTP_X_FORWARDED_HOST from a trusted IP, should override SERVER_NAME and SERVER_PORT
    assert_equal(
        TestApp(app).get(
            HTTP_HOST='127.0.0.1:1234',
            REMOTE_ADDR='127.0.0.1',
            HTTP_X_FORWARDED_HOST='example.org',
            HTTP_X_FORWARDED_SSL='on',
        ).content,
        ['https://example.org/', '127.0.0.1']
    )

def test_use_x_forwarded_forward_host_nonstandard_port():

    def app(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return [ Request(e).request_uri, Request(e).remote_addr ]

    app = use_x_forwarded(trusted=['127.0.0.1'])(app)

    assert_equal(
        TestApp(app).get(
            HTTP_HOST='127.0.0.1:1234',
            REMOTE_ADDR='127.0.0.1',
            HTTP_X_FORWARDED_HOST='example.org:8080',
        ).content,
        ['http://example.org:8080/', '127.0.0.1']
    )

def test_use_x_forwarded_forward_host_ssl_nonstandard_port():

    def app(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return [ Request(e).request_uri, Request(e).remote_addr ]

    app = use_x_forwarded(trusted=['127.0.0.1'])(app)

    # With HTTP_X_FORWARDED_HOST from a trusted IP, should override SERVER_NAME and SERVER_PORT
    assert_equal(
        TestApp(app).get(
            '/',
            SERVER_NAME='127.0.0.1',
            SERVER_PORT='1234',
            REMOTE_ADDR='127.0.0.1',
            HTTP_X_FORWARDED_HOST='example.org:8080',
            HTTP_X_FORWARDED_SSL='on'
        ).content,
        ['https://example.org:8080/', '127.0.0.1']
    )


def test_use_x_forwarded_forward_remote_addr():

    def app(e, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        return [ Request(e).request_uri, Request(e).remote_addr ]

    app = use_x_forwarded(trusted=['127.0.0.1'])(app)

    # With HTTP_X_FORWARDED_HOST from a trusted IP, should override SERVER_NAME and SERVER_PORT
    assert_equal(
        TestApp(app).get(
            SERVER_NAME='127.0.0.1',
            SERVER_PORT='1234',
            REMOTE_ADDR='127.0.0.1',
            HTTP_X_FORWARDED_HOST='example.org',
            HTTP_X_FORWARDED_FOR='4.3.2.1'
        ).content,
        ['http://example.org/', '4.3.2.1']
    )

def test_unicode():
    assert make_uri_component(u"Arvo Pärt") == "arvo-part"

def test_make_query():
    assert make_query(a='1', b=2) == 'a=1;b=2'
    assert make_query(a='one two three') == 'a=one+two+three'
    assert make_query(a=['one', 'two', 'three']) == 'a=one;a=two;a=three'

alpha = u'\u03b1' # Greek alpha
beta = u'\u03b2' # Greek beta
gamma = u'\u03b3' # Greek gamma

def test_make_query_unicode():
    assert make_query(a=[alpha, beta, gamma], charset='utf8') == 'a=%CE%B1;a=%CE%B2;a=%CE%B3'

def test_make_query_unicode_default_encoding():
    assert make_query(a=[alpha, beta, gamma], charset='utf8') == make_query(a=[alpha, beta, gamma])

def test_overlay_app():

    def app1(environ, start_response):
        request = Request(environ)
        if request.path_info == '/app1':
            return Response(['app1 response'])(environ, start_response)
        return Response(['not found'], status=404)(environ, start_response)

    def app2(environ, start_response):
        request = Request(environ)
        if request.path_info == '/app2':
            return Response(['app2 response'])(environ, start_response)
        return Response(['not found'], status=404)(environ, start_response)

    app = TestApp(overlay(app1, app2))
    assert_equal(app.get('/app1').content, ['app1 response'])
    assert_equal(app.get('/app2').content, ['app2 response'])
    assert_equal(app.get('/app3').status, '404 Not Found')

def test_withargs_dispatch_args():

        dispatcher = pesto.dispatcher_app()

        @dispatcher.match(r'/<arg1:unicode>/<arg2:unicode>', 'GET')
        @with_request_args(arg1=unicode, arg2=int)
        def app(request, arg1, arg2):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__, arg2, type(arg2).__name__)
            ])


        assert_equal(
            TestApp(dispatcher).get('/foo/29').body,
            "Received u'foo':unicode, 29:int"
        )

def test_withargs_query_args():

        @to_wsgi
        @with_request_args(arg1=unicode, arg2=int)
        def app(request, arg1, arg2):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__, arg2, type(arg2).__name__)
            ])

        assert_equal(
            TestApp(app).get(QUERY_STRING='arg1=foo;arg2=29').body,
            "Received u'foo':unicode, 29:int"
        )

def test_withargs_missing_args():

        @to_wsgi
        @with_request_args(arg1=unicode, arg2=int)
        def app(request, arg1, arg2):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__, arg2, type(arg2).__name__)
            ])

        try:
            TestApp(app).get(QUERY_STRING='arg1=foo').status,
        except KeyError, e:
            assert_equal(e.args, ('arg2',))
        else:
            raise AssertionError("KeyError expected but not raised")

        @to_wsgi
        @with_request_args(arg1=unicode, arg2=int)
        def app(request, arg1, arg2=None):
            return Response([
                'Received %r:%s, %r:%s' % (arg1, type(arg1).__name__, arg2, type(arg2).__name__)
            ])

        response = TestApp(app).get(QUERY_STRING='arg1=foo')
        assert_equal(response.status, '200 OK')
        assert_equal(response.body, "Received u'foo':unicode, None:NoneType")

def test_closingiterator():

    class TestException(Exception):
        """
        An exception to test with
        """
    mock_environ = make_environ()
    def mock_start_response(status, headers):
        pass

    def app(environ, start_response):
        start_response('200 OK', [('Content-Type: text/plain')])
        yield "Foo"
        yield "Bar"

    def app_with_exception(environ, start_response):
        start_response('200 OK', [('Content-Type: text/plain')])
        yield "Foo"
        raise TestException()

    def test_close(app):
        l = []
        def close():
            l.append(1)
        app = app(mock_environ, mock_start_response)
        app = ClosingIterator(app, close)
        try:
            try:
                for i in app:
                    pass
            finally:
                app.close()
        except TestException:
            pass
        assert_equal(l, [1])

    def test_close2(app):
        l = []
        m = MockWSGI()
        def close():
            l.append(1)
        def close2():
            l.append(2)
        app = app(mock_environ, mock_start_response)
        app = ClosingIterator(app, close, close2)
        try:
            try:
                for i in app:
                    pass
            finally:
                app.close()
        except TestException:
            pass
        assert_equal(l, [1, 2])

    test_close(app)
    test_close(app_with_exception)

def test_StartResponseWrapper_write():

    def wsgiapp(environ, start_response):
        start_response = StartResponseWrapper(start_response)
        write = start_response('200 OK', [('X-We-All-Adora', 'Kia-Ora'), ('Content-Type', 'text/plain')])

        write('cat')
        write('sat')
        write2 = start_response.call_start_response()
        write2('mat')
        return []

    assert_equal(TestApp(wsgiapp).get('/').content, ['catsatmat'])




def test_ClosingIterator_with_exception():

    class TestException(Exception):
        pass

    @PestoWSGIApplication
    def app(request):
        raise TestException()
        return Response(['foobar'])

    l = []
    def close():
        l.append(1)

    def middleware(app):
        def middleware(environ, start_response):
            return ClosingIterator(app(environ, start_response), close)
        return middleware
    app = middleware(app)
    try:
        TestApp(app).get('/')
    except TestException:
        pass

    assert_equal(l, [1])

def test_pesto_app_runs_on_first_iteration():

    l = []
    @PestoWSGIApplication
    def app(request):
        l.append(1)
        return Response(['foobar'])

    mock_environ = make_environ()
    def mock_start_response(status, headers):
        pass

    response_iterator = app(mock_environ, mock_start_response)
    assert_equal(l, [])

    response_iterator.next()
    assert_equal(l, [1])

    response_iterator.close()

def test_pesto_dispatcher_app_runs_on_first_iteration():

    l = []
    dispatcher = pesto.dispatcher_app()

    mock_environ = make_environ()
    def mock_start_response(status, headers):
        pass

    @dispatcher.match('/', 'GET')
    def app(request):
        l.append(1)
        return Response(['foobar'])

    response_iterator = dispatcher(mock_environ, mock_start_response)
    assert_equal(l, [])

    response_iterator.next()
    assert_equal(l, [1])

    response_iterator.close()

def test_script_name_returned_from_requests_via_a_mount_app():

    def app(request):
        return Response([request.script_name], content_type='text/plain')

    m = mount_app({
        '/a' : to_wsgi(app),
        '/b' : to_wsgi(app),
    })

    assert_equal(
        TestApp(m).get(SCRIPT_NAME='', PATH_INFO='/a').body, "/a"
    )
    assert_equal(
        TestApp(m).get(SCRIPT_NAME='', PATH_INFO='/b').body, "/b"
    )

def test_normpath():

    assert normpath('') == ''
    assert normpath('/') == '/'
    assert normpath('//') == '/'
    assert normpath('///') == '/'

    assert normpath('/./') == '/'
    assert normpath('/../') == '/'
    assert normpath('/.../') == '/.../'
    assert normpath('/..//../') == '/'

    assert normpath("/hello/.//dolly//") == "/hello/dolly/"
    assert normpath("///hello/.//dolly//.//..//.//sailor") == "/hello/sailor"

    assert normpath("/sliced/bread/") == "/sliced/bread/"

def test_static_server_sets_last_modified_header():
    start_time = time()
    fh, tmpname = mkstemp()

    def app(environ, start_response):
        return serve_static_file(Request(environ), tmpname)(environ, start_response)

    try:
        os.close(fh)
        response = TestApp(app).get('/')
        assert response.status_code == 200
        assert timegm(parsedate(response.get_header('Last-Modified'))) >= floor(start_time)
    finally:
        unlink(tmpname)

def test_static_server_returns_not_modified_status():

    def app(environ, start_response):
        return serve_static_file(Request(environ), tmpname)(environ, start_response)

    def rfc2822_date(time, tzoffset):
        """
        Return an rfc2822 formatted tuple for the given time (seconds since epoch, UTC) for
        the given timezone offset. The dst flag is always set to zero.
        """
        s = strftime('%w, %d %b %Y %H:%M:%S', gmtime(time + tzoffset * 3600))
        if not tzoffset:
            return s + ' -0000'
        else:
            return s + ' %+05d' % (tzoffset * 100,)

    start_time = time()
    app = TestApp(app)

    fh, tmpname = mkstemp()
    try:
        os.close(fh)
        now = time()
        r = app.get('/', HTTP_IF_MODIFIED_SINCE=rfc2822_date(0, 0))
        assert r.status_code == 200
        mtime = timegm(parsedate(r.get_header('Last-Modified')))

        r = app.get('/', HTTP_IF_MODIFIED_SINCE=rfc2822_date(mtime, 0))
        assert r.status_code == 304

        # Check we get the correct response even when specifying different timezones
        r = app.get('/', HTTP_IF_MODIFIED_SINCE=rfc2822_date(mtime, +1))
        assert r.status_code == 304

        r = app.get('/', HTTP_IF_MODIFIED_SINCE=rfc2822_date(mtime, -1))
        assert r.status_code == 304

        r = app.get('/', HTTP_IF_MODIFIED_SINCE=rfc2822_date(mtime - 60, 0))
        assert r.status_code == 200

        r = app.get('/', HTTP_IF_MODIFIED_SINCE=rfc2822_date(mtime - 60, +1))
        assert r.status_code == 200

        r = app.get('/', HTTP_IF_MODIFIED_SINCE=rfc2822_date(mtime - 60, -1))
        assert r.status_code == 200

    finally:
        unlink(tmpname)


