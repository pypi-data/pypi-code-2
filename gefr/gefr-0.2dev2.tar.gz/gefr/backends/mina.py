#
# Apache Mina integration for gefr
# Author: Sun Ning<classicning@gmail.com>
#

from java.lang import String
from java.net import InetSocketAddress
from java.nio.charset import Charset

from org.apache.mina.transport.socket.nio import NioSocketAcceptor
from org.apache.mina.core.service import IoHandlerAdapter
from org.apache.mina.core.buffer import IoBuffer
from org.apache.mina.filter.codec import ProtocolCodecFilter, ProtocolCodecFactory, ProtocolEncoderAdapter, CumulativeProtocolDecoder

from StringIO import StringIO

from gefr.core import GefrBackend, StartResponse
from gefr.wsgi import *

class MinaBackend(GefrBackend):
    def __init__(self, app, host, port):
        GefrBackend.__init__(self, app, host, port)

    def start(self):
        self.handler = HttpHandler(self.app)
        self.acceptor = NioSocketAcceptor()
        self.acceptor.getFilterChain().addLast("protocol", ProtocolCodecFilter(HttpCodecFactory()))
        self.acceptor.setHandler(self.handler)
        self.acceptor.bind(InetSocketAddress(self.host, self.port))

    def shutdown(self):
        self.acceptor.unbind(InetSocketAddress(self.host, self.port))

class HttpHandler(IoHandlerAdapter):
    HTTP_KEEP_ALIVE = 'HTTP_KEEP_ALIVE'
    def __init__(self, app):
        self.app = app
    
    def messageReceived(self, session, message):
        """handles http request"""
        keep_alive = message.header_dict.get('Connection', '').upper() == 'KEEP-ALIVE'
        session.setAttribute(self.HTTP_KEEP_ALIVE, keep_alive)

        environ = message.to_wsgi_environ()
        start_response = StartResponse()
        body_data = self.app(environ, start_response)
        http_response = HttpMessage(session)
        http_response.to_wsgi_response(start_response, body_data, environ)
        session.write(http_response)

    def messageSent(self, session, message):
        if not session.getAttribute(self.HTTP_KEEP_ALIVE, False):
            session.close(True)

class HttpRequestDecoder(CumulativeProtocolDecoder):
    GEFR_HTTP_HEADER_COMPLETE = 'GEFR_HTTP_HEADER_COMPLETE'
    GEFR_HTTP_MESSAGE = 'GEFR_HTTP_MESSAGE'
    def doDecode(self, session, buf, out):
        header_complete = session.getAttribute(self.GEFR_HTTP_HEADER_COMPLETE, False)
        http_msg = session.getAttribute(self.GEFR_HTTP_MESSAGE, None)

        ### caution: msg is a jython string, not a java string
        msg = buf.getString(Charset.forName('UTF-8').newDecoder())
        delimeter = msg.find('\r\n\r\n')
        if not header_complete:
            if delimeter > 0: ## header complete
                headers = msg[:delimeter]
                http_msg = HttpMessage(session)
                http_msg.parse_header(headers)
                header_complete = True

                session.setAttribute(self.GEFR_HTTP_HEADER_COMPLETE, header_complete)
                session.setAttribute(self.GEFR_HTTP_MESSAGE, http_msg)

        if header_complete:
            ## read body
            finish = self.read_body(msg, delimeter, http_msg, out)
            if finish: self.cleanup(session)
            return finish
        else:
            return False

    def read_body(self, msg, delimeter, http_msg, out, headers=None):
        if headers is None:
            headers = msg[:delimeter]

        body_size = len(msg) - len(headers) - 4
        expected_body_size = int(http_msg.header_dict.get('Content-Length', 0))
        if expected_body_size > body_size:
            return False
        else:
            body_data = msg[len(headers)+4:]
            http_msg.set_body(body_data)
            out.write(http_msg)
            return True

    def cleanup(self, session):
        ## clean up
        session.setAttribute(self.GEFR_HTTP_HEADER_COMPLETE, None)
        session.setAttribute(self.GEFR_HTTP_MESSAGE, None)

class HttpResponseEncoder(ProtocolEncoderAdapter):
    def encode(self, session, message, out):
        data = message.output
        buf_size = len(data)
        buf = IoBuffer.allocate(buf_size, False)
        buf.put(data)
        buf.flip()
        out.write(buf)

class HttpCodecFactory(ProtocolCodecFactory):
    def __init__(self):
        self.encoder = HttpResponseEncoder()
        self.decoder = HttpRequestDecoder()

    def getEncoder(self, session):
        return self.encoder

    def getDecoder(self, session):
        return self.decoder

class HttpMessage(object):
    def __init__(self, session):
        self.session = session

    def parse_header(self, header_data):
        lines = header_data.split('\r\n')
        first_line = lines[0]
        self.method, self.request_uri, _ = tuple(first_line.split(' '))
        if self.request_uri.find('?') > 0:
            self.request_path, self.query_string = self.request_uri.split('?')
        else:
            self.request_path = self.request_uri
            self.query_string = ''
        self.header_dict = {}
        for i in range(1, len(lines)):
            line = lines[i]
            attr, val = tuple(map(lambda x: x.strip(), line.split(':', 1)))
            self.header_dict[attr] = val

    def serialize_header(self):
        status_line = ' '.join(str(self.status), self.message)
        header_lines = '\r\n'.join(['%s: %s' % (key, str(val)) for key,val in self.header_dict.items()])
        return '%s\r\n%s\r\n\r\n' % (status_line, header_lines)
        
    def set_status(self, status, message):
        self.status = status
        self.message = message

    def set_header(self, header_dict):
        self.header = header_dict

    def set_body(self, body):
        self.body = body
        self.header_dict['Content-Length'] = len(body)

    def to_wsgi_environ(self):
        environ = get_default_environ()
        environ['REQUEST_METHOD'] = self.method
        environ['SCRIPT_NAME'] = ''
        environ['PATH_INFO'] = self.request_path
        environ['QUERY_STRING'] = self.query_string
        environ['CONTENT_TYPE'] = self.header_dict.get('Content-Type', '')
        environ['CONTENT_LENGTH'] = int(self.header_dict.get('Content-Length', 0))
        environ['SERVER_NAME'] = self.session.getServiceAddress().getHostName()
        environ['SERVER_PORT'] = str(self.session.getServiceAddress().getPort())
        environ['REMOTE_ADDR'] = self.session.getRemoteAddress().getHostName()
        environ['SERVER_PROTOCOL'] = 'http'
        environ['wsgi.input'] = StringIO(self.body)

        environ['gefr.backend'] = 'mina'
        header_dict_to_environ(self.header_dict, environ)
        return environ

    def to_wsgi_response(self, start_response, body_data, environ):
        self.output = get_response(start_response, body_data, environ)
        
