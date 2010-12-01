"""
Statement coverage tests for mongrel2_wsgi.server.
"""

from mongrel2_wsgi import server

import urllib2

from wsgiref.simple_server import demo_app
from wsgiref.validate import validator

import logging
log = logging.getLogger(__name__)

sender_id = 'ee3f2ae1-37e1-4866-a9bc-90cf5db31b9d'
sub_addr = 'tcp://127.0.0.1:52999'
pub_addr = 'tcp://127.0.0.1:52998'

def create_test_server():
    """Return testing Mongrel2WSGIServer."""
    app = validator(demo_app)
    s = server.Mongrel2WSGIServer(
            app, 
            sender_id=sender_id, 
            sub_addr=sub_addr,
            pub_addr=pub_addr
            )
    s.requests = RedPool()
    s.bind()
    s.ready = True
    return s

class RedPool(object):
    """Synchronous GreenPool implementation."""
    def spawn_n(self, fn, *args, **kwargs):
        fn(*args, **kwargs)

class MockRecv(object):
    def __init__(self, request_data):
        self.request_data=request_data

    def recv(self):
        self.recv = None
        return self.request_data

class MockSend(list):
    def send(self, data):
        self.append(data)

def test_server():
    request_data = """ee3f2ae1-37e1-4866-a9bc-90cf5db31b9d 45965 / 203:{"PATH":"/","user-agent":"Python-urllib/2.6","host":"localhost:6767","x-forwarded-for":"::1","connection":"close","accept-encoding":"identity","METHOD":"GET","VERSION":"HTTP/1.1","URI":"/","PATTERN":"/"},0:,"""

    s = create_test_server()

    assert 'Mongrel2' in str(s), str(s)

    s.reqs = MockRecv(request_data)
    s.resp = MockSend()
    s.tick()
    assert '200 OK\r\n' in s.resp[0], s.resp

    invalid_request_data = """ee3f2ae1-37e1-4866-a9bc-90cf5db31b9d 45965 / 203:{"PATH":"/","user-agent":"Python-urllib/2.6","host":"localhost:6767","x-forwarded-for":"::1","connection":"close","accept-encoding":"identity","METHOD":"GET","VERSION":"HTTP/4.9","URI":"/","PATTERN":"/"},0:,"""

    s.reqs = MockRecv(invalid_request_data)
    s.resp = MockSend()
    s.tick()
    assert '505 HTTP' in s.resp[0], s.resp

def test_start_stop():
    s = create_test_server()
    def tick():
        s.ready = False
    s.tick = tick
    s.start()
    s.stop()

def dont_test_bad_netstring():
    s = create_test_server()
    # netstring has incorrect length, will raise IndexError if length
    # is too long, ValueError if length does not go past the end of the
    # request_data string, AttributeError if an int was thrown into
    # the JSON.
    request_data = """ee3f2ae1-37e1-4866-a9bc-90cf5db31b9d 45965 / 2103:{"PATH":"/","user-agent":"Python-urllib/2.6","host":"localhost:6767","x-forwarded-for":"::1","connectionclose","accept-encoding":"identity","METHOD":"GET","VERSION":"HTTP/1.1","URI":"/","PATTERN":"/"},0:,"""
    s.reqs = MockRecv(request_data)
    s.tick()

def test_mrbs():
    s = create_test_server()
    s.max_request_body_size = 1023
    request_data = """ee3f2ae1-37e1-4866-a9bc-90cf5db31b9d 45965 / 206:{"PATH":"/","user-agent":"Python-urllib/2.6","host":"localhost:6767","x-forwarded-for":"::1","content-length":"1024","accept-encoding":"identity","METHOD":"GET","VERSION":"HTTP/1.1","URI":"/","PATTERN":"/"},0:,"""
    s.reqs = MockRecv(request_data)
    s.resp = MockSend()
    s.tick()
    assert '413 Request Entity Too Large' in s.resp[0], s.resp

def test_transfer_encoding():
    s = create_test_server()
    request_data = """ee3f2ae1-37e1-4866-a9bc-90cf5db31b9d 45965 / 216:{"PATH":"/","user-agent":"Python-urllib/2.6","host":"localhost:6767","transfer-encoding":"chunked,foo","content-length":"1024","accept-encoding":"identity","METHOD":"GET","VERSION":"HTTP/1.1","URI":"/","PATTERN":"/"},0:,"""
    s.reqs = MockRecv(request_data)
    s.resp = MockSend()
    s.tick()
    # server does not support the 'foo' transfer encoding:
    assert '501 Unimplemented' in s.resp[0], s.resp

def test_100_continue():
    s = create_test_server()
    request_data = """ee3f2ae1-37e1-4866-a9bc-90cf5db31b9d 45965 / 182:{"PATH":"/","user-agent":"Python-urllib/2.6","host":"localhost:6767","expect":"100-continue","accept-encoding":"identity","METHOD":"GET","VERSION":"HTTP/1.1","URI":"/","PATTERN":"/"},0:,"""
    s.reqs = MockRecv(request_data)
    s.resp = MockSend()
    s.tick()
    assert '100 Continue\r\n' in s.resp[0], s.resp

def test_mongrel2file():
    class request:
        conn_id='foo'
        sender='bar'
    assert server.Mongrel2File(None, request).flush() is None

def test_read_headers():
    mongrel2_headers = {
            'accept':['foo','bar'],
            'content-language':'esperanto',
            'x-men':['superman','wolverine'],
            'PATH':'/usr/local/bin'}
    headers = server.read_headers(mongrel2_headers)
    assert 'foo' in headers['Accept'], headers['Accept']
    assert 'bar' in headers['Accept'], headers['Accept']
    assert 'superman' not in headers['X-Men'], headers['X-Men']
    assert 'wolverine' in headers['X-Men'], headers['X-Men']
    assert 'PATH' not in headers

