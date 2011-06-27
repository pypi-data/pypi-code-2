#
# Netty backend support for gefr
# 
#

from java.net import InetSocketAddress
from java.util.concurrent import Executors
from org.python.core.util import FileUtil

from org.jboss.netty.bootstrap import ServerBootstrap
from org.jboss.netty.buffer import ChannelBufferInputStream, ChannelBuffers
from org.jboss.netty.channel import \
        SimpleChannelHandler, ChannelPipelineFactory, Channels
from org.jboss.netty.channel.socket.nio import \
        NioServerSocketChannelFactory
from org.jboss.netty.handler.codec.http import \
        HttpRequestDecoder, HttpResponseEncoder, \
        HttpHeaders, DefaultHttpResponse, HttpVersion, HttpResponseStatus

from gefr import gefr_version
from gefr.core import GefrBackend, StartResponse
from gefr.wsgi import get_default_environ

class NettyBackend(GefrBackend):
    def __init__(self, app, host, port):
        GefrBackend.__init__(self, app, host, port)

    def start(self):
        wsgiHandler = WsgiHandler(self.app, self.host, self.port)

        channelFactory = NioServerSocketChannelFactory(
                Executors.newCachedThreadPool(),
                Executors.newCachedThreadPool())
        serverBootstrap = ServerBootstrap(channelFactory)
        serverBootstrap.setPipelineFactory(
                HttpWsgiChannelPipelineFactory(wsgiHandler))

        serverBootstrap.setOption('reuseAddress', True)
        
        serverBootstrap.bind(InetSocketAddress(self.host, self.port))

    def shutdown(self):
        pass

BACKEND = NettyBackend    

class HttpWsgiChannelPipelineFactory(ChannelPipelineFactory):
    def __init__(self, wsgiHandler):
        self.wsgiHandler = wsgiHandler

    def getPipeline(self):
        return Channels.pipeline(
                HttpRequestDecoder(),
                HttpResponseEncoder(),
                self.wsgiHandler)

class WsgiHandler(SimpleChannelHandler):
    def __init__(self, app, host, port):
        self.app = app
        self.host = host
        self.port = port

    def messageReceived(self, ctx, e):
        request = e.getMessage()
        environ = self._get_environ(e, request)
        
        start_response = StartResponse()
        data_generator = self.app(environ, start_response)
        
        status = int(start_response.status)
        response = DefaultHttpResponse(HttpVersion.HTTP_1_1, \
                HttpResponseStatus.valueOf(status))
        buf = ChannelBuffers.dynamicBuffer(4096)
        for key,value in start_response.headers.items():
            response.setHeader(key, value)
        response.setHeader('Server',  "gefr-%s/%s" % (environ['gefr.backend'], gefr_version))
        for data in data_generator:
            buf.writeBytes(data)

        response.setContent(buf)
        response.setHeader("Content-Length", buf.writerIndex());
        ch = e.getChannel()
        ch.write(response)                

    def exceptionCaught(self, ctx, e):
        e.getCause().printStackTrace();
        e.getChannel().close()

    def _get_environ(self, event, request):
        environ = get_default_environ()

        environ['REQUEST_METHOD'] = request.getMethod().getName()
        environ['SCRIPT_NAME'] = ''

        requestUri = request.getUri()
        if '?' in requestUri:
            environ['PATH_INFO'],environ['QUERY_STRING'] = requestUri.split('?')
        else:
            environ['PATH_INFO'],environ['QUERY_STRING'] = requestUri, ''

        environ['CONTENT_TYPE'] = request.getHeader('Content-Type')
        environ['CONTENT_LENGTH'] = HttpHeaders.getContentLength(request)

        environ['SERVER_NAME'] = self.host
        environ['SERVER_PORT'] = str(self.port)
        environ['REMOTE_ADDR'] = event.getRemoteAddress().getHostName()
        environ['SERVER_PROTOCOL'] = 'http'
        environ['wsgi.input'] = FileUtil.wrap(ChannelBufferInputStream(request.getContent()))

        for header in request.getHeaderNames():
            environ['HTTP_'+header.replace('-','_')] = request.getHeader(header)

        environ['gefr.backend'] = 'netty'

        return environ

