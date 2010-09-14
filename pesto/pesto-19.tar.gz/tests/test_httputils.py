# Copyright (c) 2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

from cStringIO import StringIO

from nose.tools import assert_equal, assert_true, assert_raises

from pesto.httputils import parse_querystring, parse_post
from pesto.httputils import TooBig, RequestParseError
from pesto.testing import TestApp, make_environ
from pesto import to_wsgi
from pesto.response import Response

from form_data import FILE_UPLOAD_DATA

def test_querystring():

    cases = [
        ('', []),
        ('a=b', [('a', 'b')]),
        ('a=b+c', [('a', 'b c')]),
        ('a==c', [('a', '=c')]),
        ('%20==c%3D', [(' ', '=c=')]),
        ('%20==c%3D', [(' ', '=c=')]),
    ]

    for input_value, expected_result in cases:
        assert_equal(
            list(parse_querystring(input_value)),
            expected_result
        )

def test_multipart():
    import form_data
    for data in form_data.multipart_samples:
        io = StringIO(data['data'])
        io.seek(0)
        environ = {
            'CONTENT_LENGTH': data['content_length'],
            'CONTENT_TYPE': data['content_type'],
        }
        parsed = sorted(list(parse_post(environ, io, 'UTF-8')))

        assert_equal(
            [name for name, value in parsed],
            ["empty-text-input", "file-upload", "text-input-ascii", "text-input-unicode"]
        )

        assert_equal(parsed[0], ("empty-text-input", ""))
        assert_equal(parsed[2], ("text-input-ascii", "abcdef"))
        assert_equal(parsed[3], ("text-input-unicode", "\xce\xb1\xce\xb2\xce\xb3\xce\xb4".decode("utf8")))

        fieldname, fileupload = parsed[1]
        assert_equal(fieldname, "file-upload")
        assert_equal(fileupload.filename, "test.data")
        assert_true(fileupload.headers['content-type'], "application/octet-stream")
        assert_equal(fileupload.file.read(), FILE_UPLOAD_DATA)

def test_fileupload_too_big():
    """
    Verify that multipart/form-data encoded POST data raises an exception if
    the total data size exceeds request.MAX_SIZE bytes
    """

    @to_wsgi
    def app(request):
        request.MAX_MULTIPART_SIZE = 500
        request.get('f1')
        return Response(['ok'])

    response = TestApp(app).post_multipart(
        files=[('f1', 'filename.txt', 'text/plain', 'x' * 1000)]
    )
    assert_equal(response.status, "413 Request Entity Too Large")

    response = TestApp(app).post_multipart(
        files=[('f1', 'filename.txt', 'text/plain', 'x' * 400)],
        data={'f2': 'x' * 101}
    )
    assert_equal(response.status, "413 Request Entity Too Large")

    @to_wsgi
    def app(request):
        request.MAX_MULTIPART_SIZE = 500
        x = request.get('f1')
        return Response(['ok'])

    # Same again but with a fake content length header
    response = TestApp(app).post_multipart(
        files=[('f1', 'filename.txt', 'text/plain', 'x' * 1000)],
        CONTENT_LENGTH="499",
    )
    assert_equal(response.status, "400 Bad Request")
    assert_equal(response.get_header('X-Pesto-Exception'), "RequestParseError('Incomplete data (expected boundary)',)")

def test_multipart_field_too_big():
    """
    Verify that multipart/form-data encoded POST data raises an exception if it
    contains a single field exceeding request.MAX_SIZE bytes
    """
    @to_wsgi
    def app(request):
        request.MAX_MULTIPART_SIZE = 500
        request.MAX_SIZE = 100
        x = request.get('f1')
        return Response(['ok'])

    response = TestApp(app).post_multipart(data={'f1': 'x' * 200})
    assert_equal(response.status, "413 Request Entity Too Large")

def test_formencoded_data_too_big():
    """
    Verify that application/x-www-form-urlencoded POST data raises an exception
    if it exceeds request.MAX_SIZE bytes
    """
    @to_wsgi
    def app(request):
        request.MAX_SIZE = 100
        x = request.get('f1')
        return Response(['ok'])

    response = TestApp(app).post(data={'f1': 'x' * 200})
    assert_equal(response.status, "413 Request Entity Too Large")


def test_non_utf8_data():
    @to_wsgi
    def app(request):
        request.charset = 'latin1'
        x = request.form['char']
        return Response([x.encode('utf8')])

    response = TestApp(app).post(data={'char': u'\u00a3'.encode('latin1')})
    assert_equal(response.body.decode('utf8'), u"\u00a3")

    response = TestApp(app).get(data={'char': u'\u00a3'.encode('latin1')})
    assert_equal(response.body.decode('utf8'), u"\u00a3")


