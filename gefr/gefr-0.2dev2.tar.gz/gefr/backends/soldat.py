
from gefr.core import GefrBackend, StartResponse
from gefr.wsgi import *

from java.lang import String
from java.nio import ByteBuffer
from java.net import InetSocketAddress

from info.sunng.soldat import Soldat, HandleAdapter
from info.sunng.soldat.engines import MultithreadAcceptorEngine
from info.sunng.soldat.engines.SoldatEngine import TransportType
from info.sunng.soldat.examples.http import HttpMessage, HttpProtocol

__author__="Sun Ning <classicning@gmail.com>"
__date__ ="$Mar 28, 2011 1:14:19 PM$"

class SoldatBackend(GefrBackend):
    def __init__(self, app, host, port):
        GefrBackend.__init__(self, app, host, port)
        
    def start(self):
        addr = InetSocketAddress(self.host, self.port)
        engine = MultithreadAcceptorEngine(addr, TransportType.TCP)
        self.soldat = Soldat(engine)
        self.soldat.setHandler(SoldatWSGIHandler(self.app))
        self.soldat.setProtocol(HttpProtocol())
        self.soldat.start()

    def shutdown(self):
        self.soldat.shutdown()

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

        resp_msg = get_response(start_response, body_data, environ)

#        resp_msg_java = String(resp_msg)
#        resp_buffer = ByteBuffer.wrap(resp_msg_java.getBytes("utf8"))
        resp_buffer = ByteBuffer.wrap(resp_msg)
        client.setBuffer(resp_buffer)

    def __get_environ(self, msg, client):
        headers = dict(msg.getHeaders())
        request_uri = msg.getRequestURI()
        request_path = request_uri.split('?')[0]
        query_string = None
        if request_uri.find("?") > 0:
            query_string = request_uri.split('?')[1]

        environ = get_default_environ()
        environ['REQUEST_METHOD'] = msg.getMethod()
        environ['SCRIPT_NAME'] = ''
        environ['PATH_INFO'] = request_path
        environ['QUERY_STRING'] = query_string or ''
        environ['CONTENT_TYPE'] = headers.get('Content-Type', None)
        environ['CONTENT_LENGTH'] = int(headers.get('Content-Length', 0))
        environ['SERVER_NAME'] = client.getServerHost()
        environ['SERVER_PORT'] = str(client.getServerPort())
        environ['REMOTE_ADDR'] = client.getClientHost()
        environ['SERVER_PROTOCOL'] = 'http'
        environ['wsgi.input'] = StringIO(msg.getContent())

        environ['gefr.backend'] = 'soldat'
        header_dict_to_environ(headers, environ)

        return environ

    def onWriteComplete(self, client):
        msg = client.getAttachment()
        headers = msg.getHeaders()
        if 'Connection' in headers:
            client.getTransport().close()
            return
        if headers['Connection'].upper() != 'KEEP-ALIVE':
            client.getTransport().close()
            return
        
