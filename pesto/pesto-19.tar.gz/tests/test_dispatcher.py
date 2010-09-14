# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

from functools import wraps
import pesto
from pesto.response import Response
from pesto.request import Request
from pesto.testing import TestApp

from nose.tools import assert_equal

def test_spaces():

    def h1(request, value):
        return Response([value])

    d = pesto.dispatcher_app()
    d.match('/<value:unicode>', GET=h1)

    response = TestApp(d).get('/value%20with%20spaces')
    assert_equal(response.body, 'value with spaces')

def test_unbound_method():

    d = pesto.dispatcher_app()

    class Controller(object):
        @d.match('/h1', 'GET')
        def h1(request):
            return Response(["h1"])

        @d.match('/h2', 'GET')
        def h2(request):
            return Response(["h2"])

    d = TestApp(d)
    assert d.get('/h1').body == 'h1'
    assert d.get('/h2').body == 'h2'

def test_bound_method():

    d = pesto.dispatcher_app()

    class Greeter(object):

        def __init__(self, greeting):
            self.greeting = greeting

        def greet(self, request):
            return Response(self.greeting)

    g = Greeter('hello world!')
    d.match('/greeting', 'GET')(g.greet)

    d = TestApp(d)
    assert_equal(d.get('/greeting').body, 'hello world!')



def test_dispatcher_simple_match():

    # Ordinarily these would be pesto handler functions, but strings are easier for writing test cases
    handler1 = 'h1'
    handler2 = 'h2'

    dispatcher = pesto.dispatcher_app()
    dispatcher.match('/foo', GET=handler1)
    dispatcher.match('/bar', GET=handler2)

    request = Request(TestApp.make_environ(PATH_INFO='/foo'))
    assert_equal(
        list(dispatcher.gettarget('/foo', 'GET', request)),
        [(handler1, None, (), {})]
    )

    request = Request(TestApp.make_environ(PATH_INFO='/foo'))
    assert_equal(
        list(dispatcher.gettarget('/bar', 'GET', request)),
        [(handler2, None, (), {})]
    )

    request = Request(TestApp.make_environ(PATH_INFO='/baz'))
    assert_equal(
        list(dispatcher.gettarget('/baz', 'GET', request)),
        []
    )


def test_dispatcher_trailing_slashes():

    # Ordinarily these would be pesto handler functions, but strings are easier for writing test cases
    handler1 = 'h1'
    handler2 = 'h2'

    dispatcher = pesto.dispatcher_app()
    dispatcher.match('/foo', GET=handler1)
    dispatcher.match('/foo/', GET=handler2)

    request = Request(TestApp.make_environ(PATH_INFO='/foo'))
    assert_equal(
        list(dispatcher.gettarget('/foo', 'GET', request)),
        [(handler1, None, (), {})]
    )
    request = Request(TestApp.make_environ(PATH_INFO='/foo/'))
    assert_equal(
        list(dispatcher.gettarget('/foo/', 'GET', request)),
        [(handler2, None, (), {})]
    )
    request = Request(TestApp.make_environ(PATH_INFO='/foo////'))
    assert_equal(
        list(dispatcher.gettarget('/foo////', 'GET', request)),
        [(handler2, None, (), {})]
    )

def test_dispatcher_match_with_vars():

    handler1 = 'h1'
    handler2 = 'h2'

    dispatcher = pesto.dispatcher_app()
    dispatcher.match(r'/entries/new',        GET=handler2)
    dispatcher.match(r'/entries/<id:unicode>', GET=handler1)

    request = Request(TestApp.make_environ(PATH_INFO='/entries/new'))
    assert_equal(
        list(dispatcher.gettarget(request.path_info, request.request_method, request)),
        [(handler2, None, (), {}), (handler1, None, (), {'id' : 'new'})]
    )

    request = Request(TestApp.make_environ(PATH_INFO='/entries/blah'))
    assert_equal(
        list(dispatcher.gettarget(request.path_info, request.request_method, request)),
        [(handler1, None, (), {'id': 'blah'})]
    )

def test_combined_dispatcher():

        d1 = pesto.dispatcher_app()
        d1.match('/foo', GET=lambda request: Response(['d1:foo']))
        d2 = pesto.dispatcher_app()
        d2.match('/bar', GET=lambda request: Response(['d2:bar']))
        combined = pesto.dispatcher_app(debug=True).combine(d1, d2)

        d1 = TestApp(d1)
        d2 = TestApp(d2)
        combined = TestApp(combined)
        assert_equal(d1.get('/foo').body, 'd1:foo')
        assert_equal(combined.get('/foo').body, 'd1:foo')

        assert_equal(d2.get('/bar').body, 'd2:bar')
        assert_equal(combined.get('/bar').body, 'd2:bar')


def test_unicode():
    d = pesto.dispatcher_app()
    request = Request(TestApp.make_environ())
    d.match('/<:unicode>', GET='x'),
    assert_equal(list(d.gettarget('/xyzy', 'GET', request)), [('x', None, ('xyzy',), {})])
    assert_equal(list(d.gettarget('/xyzy/index.html', 'GET', request)), [])

def test_path():
    d = pesto.dispatcher_app()
    request = Request(TestApp.make_environ())
    d.match('/<:path>', GET='x'),
    assert_equal(list(d.gettarget('/xyzy', 'GET', request)), [('x', None, ('xyzy',), {})])
    assert_equal(list(d.gettarget('/xyzy/index.html', 'GET', request)), [('x', None, ('xyzy/index.html',), {})])

def test_any():
    d = pesto.dispatcher_app()
    request = Request(TestApp.make_environ())
    d.match('/<:any("about", "contact")>.html', GET='x'),
    assert_equal(list(d.gettarget('/xyzy', 'GET', request)), [])
    assert_equal(list(d.gettarget('/about.html', 'GET', request)), [('x', None, ('about',), {})])
    assert_equal(list(d.gettarget('/about.htm', 'GET', request)), [])
    assert_equal(list(d.gettarget('/contact.html', 'GET', request)), [('x', None, ('contact',), {})])
    assert_equal(list(d.gettarget('/xyzzy.html', 'GET', request)), [])


def test_predicate():

    def from_ip(addr):
        def from_ip(req):
            return req.remote_addr.startswith(addr)
        return from_ip

    d = pesto.dispatcher_app()

    @d.match('/', 'GET', predicate=from_ip('192.168.1.'))
    def internal(req):
        return Response(['internal'])

    @d.match('/', 'GET', predicate=from_ip('127.0.0.1'))
    def localhost(req):
        return Response(['localhost'])

    @d.match('/', 'GET')
    def external(req):
        return Response(['external'])

    d = TestApp(d)
    assert_equal(d.get('/', REMOTE_ADDR='127.0.0.1').body, 'localhost')
    assert_equal(d.get('/', REMOTE_ADDR='192.168.1.20').body, 'internal')
    assert_equal(d.get('/', REMOTE_ADDR='1.2.3.4').body, 'external')


def test_decorators():

    def decorator1(func):

        @wraps(func)
        def decorator1(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            if isinstance(result, Response):
                return result
            return Response(
                content=['X'.join(result)],
                content_type='text/plain'
            )
        return decorator1

    def decorator2(func):
        @wraps(func)
        def decorator2(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            if isinstance(result, Response):
                return result
            return Response(
                content=['Y'.join(result)],
                content_type='text/plain'
            )
        return decorator2

    d = pesto.dispatcher_app()

    @d.match('/data.1', "GET", decorators=[decorator1])
    @d.match('/data.2', "GET", decorators=[decorator2])
    def getdata(request):
        return ['yo', 'ho', 'ho']

    request = Request(TestApp.make_environ())
    assert_equal(getdata(request), ['yo', 'ho', 'ho'])
    assert_equal(TestApp(d).get('/data.1').body, 'yoXhoXho')
    assert_equal(TestApp(d).get('/data.2').body, 'yoYhoYho')

def test_precedence():
    """
    Check that the first matching function is used
    """
    d = pesto.dispatcher_app()

    @d.match('/whuffle', 'GET')
    def whuffle(request):
        return Response(['whuffle-1'])

    @d.match('/whuffle', 'GET')
    def whuffle(request):
        return Response(['whuffle-2'])

    d = TestApp(d)
    assert_equal(d.get('/whuffle').body, 'whuffle-1')

def test_cache_with_predicate():

    predicate = lambda request: 'flobble' in request.form
    d = pesto.dispatcher_app(cache_size=10)

    @d.match('/whuffle', 'GET', predicate=predicate)
    def whuffle_with_flobble(request):
        return Response(['whuffle-flobble'])

    @d.match('/whuffle', 'GET')
    def whuffle_no_flobble(request):
        return Response(['whuffle'])

    d = TestApp(d)
    assert_equal(d.get('/whuffle').body, 'whuffle')
    assert_equal(d.get('/whuffle', data={'flobble': '1'}).body, 'whuffle-flobble')

    # Second pass to check that the cache does not store the wrong result
    assert_equal(d.get('/whuffle').body, 'whuffle')
    assert_equal(d.get('/whuffle', data={'flobble': '1'}).body, 'whuffle-flobble')

def test_url_generation():

    d = pesto.dispatcher_app()

    @d.match('/page/one', 'GET')
    def page_one(request):
        return Response([page_two.url()])

    @d.match('/page/two', 'GET')
    def page_two(request):
        return Response([page_one.url()])

    d = TestApp(d)
    assert_equal(d.get('/page/one').body, 'http://localhost/page/two')
    assert_equal(d.get('/page/two').body, 'http://localhost/page/one')

def test_url_generation_overriding_script_name():

    d = pesto.dispatcher_app()

    @d.match('/page/one', 'GET')
    def page_one(request):
        return Response([page_one.url(script_name='/buffalo')])

    d = TestApp(d)
    assert_equal(d.get('/page/one').body, 'http://localhost/buffalo/page/one')


def test_url_generation_overriding_netloc():

    d = pesto.dispatcher_app()

    @d.match('/page/one', 'GET')
    def page_one(request):
        return Response([page_one.url(netloc='example.org:8080')])

    d = TestApp(d)
    assert_equal(d.get('/page/one').body, 'http://example.org:8080/page/one')


