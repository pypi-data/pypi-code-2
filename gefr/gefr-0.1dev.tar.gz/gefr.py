#!/usr/bin/env python
#
#

__author__="Sun Ning <classicning@gmail.com>"
__date__ ="$Dec 28, 2010 10:06:01 PM$"
__version__ = '0.1dev'

import signal
import httplib
from StringIO import StringIO

from java.lang import String
from java.nio import ByteBuffer
from java.net import InetSocketAddress

from info.sunng.soldat import Soldat, HandleAdapter
from info.sunng.soldat.engines import MultithreadAcceptorEngine
from info.sunng.soldat.engines.SoldatEngine import TransportType
from info.sunng.soldat.examples.http import HttpMessage, HttpProtocol

class SoldatWSGIHandler(HandleAdapter):
    def __init__(self, app):
        self.wsgi_app = app

    def onMessageComplete(self, client):
        self.data = client.getBuffer()
        req_msg = HttpMessage(self.data)
        client.setAttachment(req_msg)
        
        environ = self.__get_environ(req_msg, client)
        
        start_response = StartResponse()
        body_data = self.wsgi_app(environ, start_response)

        resp_msg = self.__get_response(start_response, body_data, environ)

        resp_msg_java = String(resp_msg)
        resp_buffer = ByteBuffer.wrap(resp_msg_java.getBytes("utf8"))
        client.setBuffer(resp_buffer)

    def __get_default_environ(self):
        environ = {}
        environ['wsgi.version'] = (1,0)
        environ['wsgi.url_scheme'] = 'http'
        environ['wsgi.multithread'] = True
        environ['wsgi.multiprocess'] = False
        environ['wsgi.run_once'] = False
        return environ

    def __get_environ(self, msg, client):
        headers = dict(msg.getHeaders())
        request_uri = msg.getRequestURI()
        request_path = request_uri.split('?')[0]
        query_string = None
        if request_uri.find("?") > 0:
            query_string = request_uri.split('?')[1]

        environ = self.__get_default_environ()
        environ['REQUEST_METHOD'] = msg.getMethod()
        environ['SCRIPT_NAME'] = ''
        environ['PATH_INFO'] = request_path
        environ['QUERY_STRING'] = query_string or ''
        environ['CONTENT_TYPE'] = headers['Content-Type'] if 'Content-Type' in headers else None
        environ['CONTENT_LENGTH'] = int(headers['Content-Length']) if 'Content-Length' in headers else 0
        environ['SERVER_NAME'] = client.getServerHost()
        environ['SERVER_PORT'] = str(client.getServerPort())
        environ['REMOTE_ADDR'] = client.getClientHost()
        environ['SERVER_PROTOCOL'] = 'http'
        environ['wsgi.input'] = msg.getContent()
        environ['wsgi.errors'] = StringIO()

        for key,val in headers.items():
            environ['HTTP_'+key.replace('-','_')] = val

        

        return environ

    def __get_response(self, start_response, body, environ):
        status = start_response.status
        message = start_response.message

        output = ''.join(body) if int(status) < 500 else environ['wsgi.errors'].getvalue()
        
        first_line = " ".join(["HTTP/1.1", status, message])

        headers = start_response.headers
        headers['Server'] = "gefr/" + __version__
        if "Content-Length" not in headers:
            content_length = len(output)
            headers["Content-Length"] = str(content_length)
        header_lines = "\r\n".join([''.join([k,":",headers[k]]) for k in headers.keys()])
        return "\r\n".join([first_line, header_lines, '', output])
    
    def onWriteComplete(self, client):
        msg = client.getAttachment()
        headers = msg.getHeaders()
        if 'Connection' in headers:
            client.getTransport().close()
            return
        if headers['Connection'] != 'keep-alive':
            client.getTransport().close()
            return 

class StartResponse(object):
    def __init__(self):
        self.headers = {}

    def __call__(self, status, response_headers, exc_info=None):
        self.status, reason = status.split(' ', 1)
        self.message = httplib.responses[int(self.status)]
        for header in response_headers:
            self.headers[str(header[0])] = str(header[1])

class Gefr(object):
    def __init__(self, app, host='localhost', port=8080):
        self.app = app
        self.host = host
        self.port = port

        signal.signal(signal.SIGTERM, self.__sig_term)

    def start(self):
        addr = InetSocketAddress(self.host, self.port)
        engine = MultithreadAcceptorEngine(addr, TransportType.TCP)
        self.soldat = Soldat(engine)
        self.soldat.setHandler(SoldatWSGIHandler(self.app))
        self.soldat.setProtocol(HttpProtocol())
        self.soldat.start()

    def shutdown(self):
        self.soldat.shutdown()

    def __sig_term(self, sig, frame):
        self.shutdown()

