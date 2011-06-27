#
# Jetty backend for gefr
# Author: Sun Ning<classicning@gmail.com>
#

from java.net import InetSocketAddress

from org.eclipse.jetty.server import Server
from org.eclipse.jetty.server.handler import AbstractHandler

from gefr import gefr_version
from gefr.core import GefrBackend, StartResponse
from gefr.wsgi import get_environ_from_servlet_request

class JettyBackend(GefrBackend):
    def __init__(self, app, host, port):
        GefrBackend.__init__(self, app, host, port)
        
    def start(self):
        self.handler = JettyWsgiHandler(self.app)
        self.server = Server(InetSocketAddress(self.host, self.port))
        self.server.setHandler(self.handler)
        self.server.start()
        self.server.join()
        
    def shutdown(self):
        self.server.stop()

BACKEND = JettyBackend        
        
class JettyWsgiHandler(AbstractHandler):
    
    def __init__(self, app):
        self.app = app
        
    def handle(self, target, baseRequest, request, response):
        environ = self._get_environ(request)

        start_response = StartResponse()
        data_generator = self.app(environ, start_response)
        status = int(start_response.status)
        response.setStatus(status)
        for key,value in start_response.headers.items():
            response.setHeader(key, value)
        response.setHeader('Server',  "gefr-%s/%s" % (environ['gefr.backend'], gefr_version))
        ## generator style
        writer = response.getWriter()
        for data in data_generator:
            writer.println(data)
                
        baseRequest.setHandled(True)
                
    def _get_environ(self, request):
        environ = get_environ_from_servlet_request(request)
        environ['gefr.backend'] = 'jetty'
        return environ
        
                
