# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import pesto
from pesto.response import Response
from pesto.testing import TestApp
from pesto.caching import with_etag, etag_middleware

from nose.tools import assert_equal

def gen_etag(request):
    return "one"

def test_set_etag():

    @pesto.to_wsgi
    @with_etag(gen_etag)
    def app(request):
        return Response(['whoa nelly'])
    assert_equal(TestApp(app).get().get_header('ETag'), '"one"')

def test_set_etag_weak():

    @pesto.to_wsgi
    @with_etag(gen_etag, weak=True)
    def app(request):
        return Response(['whoa nelly'])

    assert_equal(TestApp(app).get().get_header('ETag'), 'W/"one"')

def test_if_none_match_hit():

    calls = []

    @pesto.to_wsgi
    @with_etag(gen_etag)
    def app(request):
        def gen_content():
            yield "whoa"
            yield " nelly"
            calls.append(1)
        return Response(gen_content())

    app = etag_middleware(app)

    result = TestApp(app).get(HTTP_IF_NONE_MATCH='"one"')
    assert_equal(result.get_header('ETag'), '"one"')
    assert_equal(result.status, "304 Not Modified")
    assert_equal(result.body, '')
    assert_equal(len(calls), 0)

def test_if_none_match_miss():

    calls = []

    @pesto.to_wsgi
    @with_etag(gen_etag)
    def app(request):
        def gen_content():
            yield "whoa"
            yield " nelly"
            calls.append(1)
        return Response(gen_content())

    app = etag_middleware(app)

    result = TestApp(app).get(HTTP_IF_NONE_MATCH='"two"')
    assert_equal(result.get_header('ETag'), '"one"')
    assert_equal(result.status, "200 OK")
    assert_equal(result.body, 'whoa nelly')
    assert_equal(len(calls), 1)

