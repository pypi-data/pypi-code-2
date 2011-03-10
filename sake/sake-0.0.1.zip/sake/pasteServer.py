"""
pasteServer module
A service for running paste http server
"""

import SocketServer

from .app import app
from .process import Process


class StacklessMixIn:
    """Mix-in class to handle each request in a new tasklet."""

    requestCount = 0

    def process_request_tasklet(self, request, client_address):
        """Same as in BaseServer but as a thread.

        In addition, exception handling is done here.
        """
        StacklessMixIn.requestCount += 1

        try:
            self.finish_request(request, client_address)
            self.close_request(request)
        except Exception:
            self.handle_error(request, client_address)
            self.close_request(request)

    def process_request(self, request, client_address):
        """Start a new tasklet to process the request."""
        if app.running:
            pasteServer = app.GetService("pasteServer")
            pasteServer.New(self.process_request_tasklet, request, client_address)


# monkey patch - must be set before httpserver module is initialized
SocketServer.ThreadingMixIn = StacklessMixIn
from paste import httpserver



class PasteServer(Process):
    serviceName     = "pasteServer"
    serviceIncludes = []

    def StartProcess(self):
        self.servers = []


    def StopProcess(self):
        for server in self.servers:
            server.server_close()


    def RunWebServer(self, middleware, host, port):
        server = httpserver.serve(
            middleware,
            host=host, port=port,
            use_threadpool=False,
            protocol_version = "HTTP/1.1",
            start_loop = False,
            )

        self.servers.append(server)
        self.log.info("http server running on %s:%s", host, port)
        self.New(self._Serve, server)


    def _Serve(self, server):
        while self.running:
            server.handle_request()
