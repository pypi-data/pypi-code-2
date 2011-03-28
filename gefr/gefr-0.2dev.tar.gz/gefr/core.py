#!/usr/bin/env python
#
#

__author__="Sun Ning <classicning@gmail.com>"
__date__ ="$Dec 28, 2010 10:06:01 PM$"
__version__ = '0.2dev'

version = __version__

import signal
import httplib

class StartResponse(object):
    def __init__(self):
        self.headers = {}

    def __call__(self, status, response_headers, exc_info=None):
        self.status, _ = status.split(' ', 1)
        self.message = httplib.responses[int(self.status)]
        for header in response_headers:
            self.headers[str(header[0])] = str(header[1])

class GefrBackend(object):
    def __init__(self, app, host, port):
        self.app = app
        self.host = host
        self.port = port

    def start(self):
        pass

    def shutdown(self):
        pass

class Gefr(object):
    def __init__(self, app, backend, host='localhost', port=8080):
        self.backend = backend(app, host, port)

        signal.signal(signal.SIGTERM, self.__sig_term)

    def start(self):
        self.backend.start()

    def shutdown(self):
        self.backend.shutdown()

    def __sig_term(self, sig, frame):
        self.shutdown()

