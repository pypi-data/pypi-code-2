"""
Adapt Mongrel2 events to WSGI by subclassing the CherryPy WSGI server.

Daniel Holth <dholth@fastmail.fm>
"""

__version__ = "0.2"

from eventlet.hubs import use_hub
use_hub('zeromq')

import eventlet
from eventlet.green import zmq

try:
    from cStringIO import StringIO
except ImportError: # PRAGMA nocover
    from StringIO import StringIO

from mongrel2_wsgi.request import Request
from mongrel2_wsgi import wsgiserver
from mongrel2_wsgi.wsgiserver import quoted_slash
from urllib import unquote

ctx = zmq.Context()

import logging
log = logging.getLogger(__name__)

# Mongrel2 HTTP headers are all lowercase:
comma_separated_headers = set(x.lower() for x in ['Accept', 'Accept-Charset', 'Accept-Encoding',
    'Accept-Language', 'Accept-Ranges', 'Allow', 'Cache-Control',
    'Connection', 'Content-Encoding', 'Content-Language', 'Expect',
    'If-Match', 'If-None-Match', 'Pragma', 'Proxy-Authenticate', 'TE',
    'Trailer', 'Transfer-Encoding', 'Upgrade', 'Vary', 'Via', 'Warning',
    'WWW-Authenticate'])

class Mongrel2File(object):
    """Make Mongrel2 response connection look somewhat like a socket."""

    def __init__(self, connection, request):
        self.connection = connection
        self.request = request
        self.header = "%s %d:%s," % \
                (request.sender, len(str(request.conn_id)), str(request.conn_id))

    def send(self, data):
        if data:
            self.connection.send(' '.join((self.header, data)))
            
    sendall = send

    def flush(self):
        pass

    def close(self):
        self.connection.send(self.header + ' ')

def read_headers(mongrel2_headers, hdict={}):
    """Merge mongrel2's headers into hdict."""
     
    for k, v in mongrel2_headers.items():
        # Mongrel2 HTTP headers are all lowercase. 
        # Uppercase values are Mongrel2 variables.
        if not (k[0].islower() and '.' not in k): continue
        if isinstance(v, list):
            if k in comma_separated_headers:
                v = ', '.join(v)
            else:
                v = v[-1]

        k = str(k.strip().title())
        v = str(v.strip())
         
        hdict[k] = v
    
    return hdict

class Mongrel2Request(wsgiserver.HTTPRequest):
    """Adapt Mongrel2 events to WSGI by subclassing the CherryPy WSGI server.

    Basically, we comment out the HTTP request parsing and error checking
    already performed by Mongrel2."""

    def __init__(self, server, conn):
        wsgiserver.HTTPRequest.__init__(self, server, None)
        self.server = server
        self.conn = conn

    def parse_request(self):
        """Parse the next HTTP request start-line and message-headers."""
        self.read_request_line()
        if self.read_request_headers():
            self.ready = True

    def read_request_line(self):
        self.started_request = True
        mongrel2_headers = self.conn.mongrel2_request.headers
        # These may or may not be the correct Mongrel2 parameters:
        method = str(mongrel2_headers['METHOD'])
        uri = str(mongrel2_headers['PATH'])
        req_protocol = str(mongrel2_headers['VERSION'])
        
        self.uri = uri
        self.method = method

        scheme, authority, path = None, None, self.uri

        if scheme: self.scheme = scheme

        qs = str(mongrel2_headers.get('QUERY', ''))
        self.qs = qs

        # Unquote the path+params (e.g. "/this%20path" -> "/this path").
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html#sec5.1.2
        #
        # But note that "...a URI must be separated into its components
        # before the escaped characters within those components can be
        # safely decoded." http://www.ietf.org/rfc/rfc2396.txt, sec 2.4.2
        # Therefore, "/this%2Fpath" becomes "/this%2Fpath", not "/this/path".
        try:
            atoms = [unquote(x) for x in quoted_slash.split(path)]
        except ValueError, ex:
            self.simple_response("400 Bad Request", ex.args[0])
            return
        path = "%2F".join(atoms)
        self.path = path

        # Compare request and server HTTP protocol versions, in case our
        # server does not support the requested protocol. Limit our output
        # to min(req, server). We want the following output:
        #     request    server     actual written   supported response
        #     protocol   protocol  response protocol    feature set
        # a     1.0        1.0           1.0                1.0
        # b     1.0        1.1           1.1                1.0
        # c     1.1        1.0           1.0                1.0
        # d     1.1        1.1           1.1                1.1
        # Notice that, in (b), the response will be "HTTP/1.1" even though
        # the client only understands 1.0. RFC 2616 10.5.6 says we should
        # only return 505 if the _major_ version is different.
        rp = int(req_protocol[5]), int(req_protocol[7])
        sp = int(self.server.protocol[5]), int(self.server.protocol[7])
        
        if sp[0] != rp[0]:
            self.request_protocol = "HTTP/1.0" # prevent AttributeError
            self.simple_response("505 HTTP Version Not Supported")
            return
        self.request_protocol = req_protocol
        self.response_protocol = "HTTP/%s.%s" % min(rp, sp)

    def read_request_headers(self):
        """Read self.rfile into self.inheaders. Return success."""
        
        # then all the http headers
        try:
            read_headers(self.conn.mongrel2_request.headers, self.inheaders)
        except ValueError, ex: # can read_headers raise this exception?
            self.simple_response("400 Bad Request", ex.args[0])
            return False
        
        mrbs = self.server.max_request_body_size
        if mrbs and int(self.inheaders.get("Content-Length", 0)) > mrbs:
            self.simple_response("413 Request Entity Too Large",
                "The entity sent with the request exceeds the maximum "
                "allowed bytes.")
            return False
        
        # Persistent connection support
        if self.response_protocol == "HTTP/1.1":
            # Both server and client are HTTP/1.1
            if self.inheaders.get("Connection", "") == "close":
                self.close_connection = True
        else:
            # Either the server or client (or both) are HTTP/1.0
            if self.inheaders.get("Connection", "") != "Keep-Alive":
                self.close_connection = True
        
        # Transfer-Encoding support
        te = None
        if self.response_protocol == "HTTP/1.1":
            te = self.inheaders.get("Transfer-Encoding")
            if te:
                te = [x.strip().lower() for x in te.split(",") if x.strip()]
        
        if te:
            for enc in te:
                if enc == "chunked":
                    self.chunked_read = True
                else:
                    # Note that, even if we see "chunked", we must reject
                    # if there is an extension we don't recognize.
                    self.simple_response("501 Unimplemented")
                    self.close_connection = True
                    return False
        
        # From PEP 333:
        # "Servers and gateways that implement HTTP 1.1 must provide
        # transparent support for HTTP 1.1's "expect/continue" mechanism.
        # This may be done in any of several ways:
        #   1. Respond to requests containing an Expect: 100-continue request
        #      with an immediate "100 Continue" response, and proceed normally.
        #   2. Proceed with the request normally, but provide the application
        #      with a wsgi.input stream that will send the "100 Continue"
        #      response if/when the application first attempts to read from
        #      the input stream. The read request must then remain blocked
        #      until the client responds.
        #   3. Wait until the client decides that the server does not support
        #      expect/continue, and sends the request body on its own.
        #      (This is suboptimal, and is not recommended.)
        #
        # We used to do 3, but are now doing 1. Maybe we'll do 2 someday,
        # but it seems like it would be a big slowdown for such a rare case.
        if self.inheaders.get("Expect", "") == "100-continue":
            # Don't use simple_response here, because it emits headers
            # we don't want. See http://www.cherrypy.org/ticket/951
            msg = self.server.protocol + " 100 Continue\r\n\r\n"
            # try:
            self.conn.wfile.sendall(msg)
            # except socket.error, x: # XXX which errors will ZeroMQ raise? import socket...
            #    if x.args[0] not in socket_errors_to_ignore:
            #        raise
        return True

class Mongrel2Connection(wsgiserver.HTTPConnection):
    """An active request."""

    RequestHandlerClass = Mongrel2Request

    def __init__(self, server, response, mongrel2_request):
        self.server = server
        self.response = response
        self.mongrel2_request = mongrel2_request
        self.rfile = StringIO(mongrel2_request.body)
        self.wfile = Mongrel2File(response, mongrel2_request)

    def communicate(self):
        req = self.RequestHandlerClass(self.server, self)
        req.parse_request()
        if not req.ready:
            return
        req.respond()
        if req.close_connection:
            self.close()

    def close(self):
        self.wfile.close()

class Mongrel2WSGIServer(wsgiserver.CherryPyWSGIServer):
    """A Mongrel2 handler."""

    ConnectionClass = Mongrel2Connection

    def __init__(self, wsgi_app, sub_addr, pub_addr, sender_id=''):
        self.requests = eventlet.GreenPool()
        self.wsgi_app = wsgi_app
        self.gateway = wsgi_gateways[self.wsgi_version]
        self.sub_addr = sub_addr
        self.pub_addr = pub_addr
        self.sender_id = sender_id
        self.software = "%s Server" % self.version
        self.server_name = ''

    def __str__(self):
        return "%s.%s" % (self.__module__, self.__class__.__name__)
   
    def start(self):
        """Run the server forever."""
        self.bind()
        self.ready = True
        while self.ready:
            self.tick()

    def bind(self):
        """Connect our ZeroMQ queues."""
        reqs = ctx.socket(zmq.PULL)
        reqs.connect(self.sub_addr)
        
        resp = ctx.socket(zmq.PUB)
        resp.connect(self.pub_addr)
        resp.setsockopt(zmq.IDENTITY, self.sender_id)

        self.reqs = reqs
        self.resp = resp

    def tick(self):
        """Accept a new connection and put it on the Queue."""
        mongrel2_request = Request.parse(self.reqs.recv())
        if (not self.ready) or mongrel2_request.is_disconnect():
            return
        conn = self.ConnectionClass(self, self.resp, mongrel2_request)
        self.requests.spawn_n(conn.communicate)

    def stop(self):
        """Gracefully shutdown a server that is serving forever."""
        self.ready = False

wsgi_gateways = wsgiserver.wsgi_gateways

