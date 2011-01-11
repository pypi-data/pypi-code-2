#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2009, 2010, 2011 Hans van Leeuwen.
# See LICENSE.txt for details.

from __future__ import unicode_literals

import sys
import threading
import unittest

from pycoreutils.test import BaseTestCase

if sys.version_info[0] == 2:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from SimpleHTTPServer import SimpleHTTPRequestHandler
else:
    from http.server import HTTPServer, BaseHTTPRequestHandler, \
                            SimpleHTTPRequestHandler


# LoopbackHttpServer, LoopbackHttpServerThread and GetRequestHandler are taken
# from Python 3.1.2's test_urllib2_localnet.py

class LoopbackHttpServer(HTTPServer):
    """HTTP server w/ a few modifications that make it useful for
    loopback testing purposes.
    """

    def __init__(self, server_address, RequestHandlerClass):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)

        # Set the timeout of our listening socket really low so
        # that we can stop the server easily.
        self.socket.settimeout(1.0)

    def get_request(self):
        """HTTPServer method, overridden."""

        request, client_address = self.socket.accept()

        # It's a loopback connection, so setting the timeout
        # really low shouldn't affect anything, but should make
        # deadlocks less likely to occur.
        request.settimeout(10.0)

        return (request, client_address)


class LoopbackHttpServerThread(threading.Thread):
    """Stoppable thread that runs a loopback http server."""

    def __init__(self, request_handler):
        threading.Thread.__init__(self)
        self._stop_server = False
        self.ready = threading.Event()
        request_handler.protocol_version = "HTTP/1.0"
        self.httpd = LoopbackHttpServer(("127.0.0.1", 0),
                                        SimpleHTTPRequestHandler)
        self.port = self.httpd.server_port

    def stop(self):
        """Stops the webserver if it's currently running."""

        # Set the stop flag.
        self._stop_server = True
        self.join()

    def run(self):
        self.ready.set()
        while not self._stop_server:
            self.httpd.handle_request()


def GetRequestHandler(responses):

    class FakeHTTPRequestHandler(BaseHTTPRequestHandler):

        server_version = "TestHTTP/"
        requests = []
        headers_received = []
        port = 80

        def do_GET(self):
            body = self.send_head()
            while body:
                done = self.wfile.write(body)
                body = body[done:]

        def do_POST(self):
            content_length = self.headers["Content-Length"]
            post_data = self.rfile.read(int(content_length))
            self.do_GET()
            self.requests.append(post_data)

        def send_head(self):
            FakeHTTPRequestHandler.headers_received = self.headers
            self.requests.append(self.path)
            response_code, headers, body = responses.pop(0)

            self.send_response(response_code)

            for (header, value) in headers:
                self.send_header(header, value % {'port':self.port})
            if body:
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                return body
            self.end_headers()

        def log_message(self, *args):
            pass

    return FakeHTTPRequestHandler


class TestCase(BaseTestCase):
    def start_server(self, responses=None):
        if responses is None:
            responses = [(200, [], b"we don't care")]
        handler = GetRequestHandler(responses)

        self.server = LoopbackHttpServerThread(handler)
        self.server.start()
        self.server.ready.wait()
        handler.port = self.server.port
        return handler

    def test_wget(self):
        self.createfile('foo')
        handler = self.start_server()
        self.assertTrue(self.runcommandline(
                'wget -O bar http://127.0.0.1:{0}/foo'.format(handler.port)))
        self.assertSamefile('foo', 'bar')
        self.server.stop()


if __name__ == '__main__':
    unittest.main()
