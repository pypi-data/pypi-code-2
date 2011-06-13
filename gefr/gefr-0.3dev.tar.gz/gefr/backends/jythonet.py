

from gefr.core import GefrBackend, StartResponse, version
from gefr.wsgi import get_environ_from_servlet_request

class JythonetBackend(GefrBackend):
    def __init__(self, app, host, port):
        GefrBackend.__init__(self, app, host, port)

    def start(self):
        """When integrated with jythonet/Servlet, Gefr should be
        started in ``servlet#init``, hold Gefr instance as a servlet instance member
        """
        self.handler = ServletWSGIAdapter(self.app)

    def handle(self, servlet, request, response):
        """Override Servlet's default ``service`` by:
        `` gefr.backend.handle(servlet, request, response)`` """
        self.handler.service(servlet, request, response)

class ServletWSGIAdapter(object):
    def __init__(self, app):
        self.wsgi_app = app

    def service(self, servlet, request, response):
        environ = self.__get_environ(request)

        start_response = StartResponse()
        body_data = self.wsgi_app(environ, start_response)

        self.__write_response(response, start_response, environ, body_data)

    def __write_response(self, response, start_response, environ, body_data):
        status = start_response.status

        response.setStatus(status)
        if status >= 500:
            error_msg = environ['wsgi.errors'].getvalue()
            response.sendError(status, error_msg)
            return

        for key,value in start_response.headers.items():
            response.setHeader(key, value)
        response.setHeader('Server', "gefr/" + version)

        writer = response.getWriter()
        for line in body_data:
            writer.write(line)
            
        writer.flush()
        writer.close()
        

    def __get_environ(self, request):
        environ = get_environ_from_servlet_request(request)
        environ['gefr.backend'] = 'jythonet'
        return environ

