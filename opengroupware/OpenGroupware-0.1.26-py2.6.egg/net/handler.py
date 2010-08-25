# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import sys, logging, urllib, urlparse
from base64               import b64decode
#import BaseHTTPServer, BaseHTTPRequestHandler
from BaseHTTPServer       import BaseHTTPRequestHandler
from coils.net.root       import RootFolder
from coils.core           import CoilsException, NoSuchPathException, AuthenticationException, AccessForbiddenException

class CoilsRequestHandler(BaseHTTPRequestHandler):
#class HTTPRequestHandler(DAVRequestHandler):
    def __init__(self, request, client_address, server):
        self.payload = None
        self.log = logging.getLogger('http')
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        #DAVRequestHandler.__init__(self, request, client_address, server)

    # client_address
    # server
    # command
    # path
    # request_version
    # headers (MessageClass of the request headers)
    # rfile - stream of the body of the request
    # wfile - output stream of the response
    def get_session():
        return None

    @property
    def user_agent(self):
        return self.headers.get('USER-AGENT', 'Unknown')

    def send_response(self, code, message):
        BaseHTTPRequestHandler.send_response(self, code, message)

    def get_request_payload(self):
        if (self.command == 'GET'):
            return None
        if (self.payload is None):
            if 'Content-length' in self.headers:
                self.payload = self.rfile.read(int(self.headers['Content-length']))
            else:
                self.log.warn('Request had not Content-Length header')
                #self.wfile.write("HTTP/1.1 100 Continue\r\n\r\n")
                self.payload = self.rfile.read()
            #self.log.debug('Request: {0} {1}'.format(self.command, self.payload))
        return self.payload

    def get_metadata(self):
        metadata = { }
        metadata['amq_broker'] = self.server.broker
        metadata['connection'] = { }
        metadata['connection']['user_agent'] = self.user_agent
        metadata['connection']['client_address'] = self.client_address[0]
        metadata['connection']['client_port']    = self.client_address[1]
        metadata['authentication'] = { }
        authorization = self.headers.get('authorization')
        if (authorization == None):
            claimstobe = self.headers.get('X-REMOTE-USER')
            if (claimstobe is None):
                metadata['authentication']['mechanism'] = 'anonymous'
            else:
                metadata['authentication']['mechanism'] = 'trust'
                metadata['authentication']['claimstobe'] = claimstobe
        else:
            (kind, data) = authorization.split(' ')
            if (kind.upper() == 'BASIC'):
                (username, _, password) = b64decode(data).partition(':')
                metadata['authentication']['login'] = username
                metadata['authentication']['claimstobe'] = username
                metadata['authentication']['secret'] = password
                metadata['authentication']['options'] = { }
                metadata['authentication']['mechanism'] = 'PLAIN'
            else:
                metadata['authentication']['mechanism'] = 'UNKNOWN'
                raise AuthenticationException(401, 'Only BASIC Authentication Supported')
        metadata['path'] = self.path
        return metadata

    def marshall_handler(self):
        ''' Retrieve the handler object, a PathObject, to process the request
            This method returns None if there is no handler for the path.
            A path may be, at most, 64 elements long '''
        #path = self.path[1:]
        url        = urlparse.urlparse(self.path)
        path       = url.path[1:]
        parameters = urlparse.parse_qs(url.query, True)
        self.log.debug('Request for {0}'.format(urllib.unquote(path)))
        if (path[-1:] == '/'):
            path=path[:-1]
        path_elements = path.split('/', 64)
        #print path_elements
        if (self.command in ['PUT', 'DELETE']):
            # If request is a PUT then we drop the last element of the path
            # for handler look-up since a PUT is managed by the collection
            # containing the resource, not the resource itself (which may not
            # exist yet if the PUT is intended to create the resource).
            self.request_name = path_elements[-1:][0]
            path_elements = path_elements[:-1]
        handler = RootFolder(None, request=self, parameters=parameters)
        for i in range(len(path_elements)):
            # Any of these objects in the tree may throw an exception,
            # most notably a 401 (Authentication Required) or a 404
            # (No such path).
            handler = handler.object_for_key(urllib.unquote(path_elements[i]))
            #print 'got handler {0} for name {1}'.format(handler, path_elements[i])
        self.log.debug('Selected {0} as handler'.format(repr(handler)))
        url           = None
        path          = None
        parameters    = None
        path_elements = None
        return handler

    def process_request(self):
        """Respond to a request"""
        handler = None
        try:
            handler = self.marshall_handler()
            if (handler is None):
                # Was unable to marshall a handler for the requested path
                raise NoSuchPathException(self.path)
            else:
                if (self.command in ['PUT', 'DELETE']):
                    # In the case of a PUT the do_ method expects the name of the
                    # request as the last element is the target resource within the
                    # managing collection.
                    getattr(handler, 'do_{0}'.format(self.command))(self.request_name)
                else:
                    getattr(handler, 'do_{0}'.format(self.command))()
                # release handler
        except AuthenticationException, err:
            self.log.exception(err)
            self.send_response(401, 'Authentication Required')
            self.send_header('WWW-Authenticate', 'Basic realm="OpenGroupware COILS"')
            self.end_headers()
            self.wfile.write('Authentication failure')
        except NoSuchPathException, err:
            self.log.exception(err)
            self.send_response(404, 'No such path as {0}'.format(self.path))
            self.end_headers()
            self.wfile.write('No such path.')
        except AccessForbiddenException, err:
            self.log.exception(err)
            self.send_response(err.error_code(), err)
            self.send_header('Content-Length', str(len('Access forbidden.')))
            self.end_headers()
            self.wfile.write('Access forbidden.')
            return
        except CoilsException, err:
            self.log.exception(err)
            self.send_response(err.error_code(), err.error_text())
            self.end_headers()
        except Exception, err:
            self.log.exception(err)
            self.send_response(500, 'A generic server failure has occurred.')
            self.end_headers()
        finally:
            if (handler is not None):
                handler.close()
                handler = None
#            objgraph.show_most_common_types(limit=20)
#            print 'dict s referenced from:'
#            for obj in objgraph.by_type('dict'):
#                pprint.pprint(objgraph.show_backrefs([obj], max_depth=10))

    def do_GET(self):
        ''' Respond to a GET request '''
        #print '%s GET' % repr(self)
        self.process_request()

    def do_POST(self):
        ''' Respond to a POST request '''
        #print '%s POST' % repr(self)
        self.process_request()

    def do_PUT(self):
        ''' Respond to a POST request '''
        #print '%s POST' % repr(self)
        self.process_request()

    def do_DELETE(self):
        ''' Respond to a DELETE request '''
        #print '%s DELETE' % repr(self)
        self.process_request()

    def do_OPTIONS(self):
        ''' Respond to a OPTIONS request '''
        #print '%s OPTIONS' % repr(self)
        self.process_request()

    def do_PROPFIND(self):
        ''' Respond to a PROPFIND request '''
        #print '%s OPTIONS' % repr(self)
        self.process_request()

    def do_REPORT(self):
        ''' Respond to a REPORT request '''
        #print '%s REPORT' % repr(self)
        self.process_request()

    def do_HEAD(self):
        ''' Respond to a HEAD request '''
        #print '%s HEAD' % repr(self)
        self.process_request()

    def send_headers(self, headers):
        for header in headers:
            self.send_header(header, headers.get(header))

    def send_chunked_data(self, headers, content_type, data):
        self.send_response(200, 'OK')
        self.send_headers(headers)
        self.send_header('Content-Type', content_type)
        self.send_header('Transfer-Encoding', 'chunked')
        self.end_headers()
        length = len(data)
        self.wfile.write("%x\r\n" % (len(data)))
        self.wfile.write(data)
        self.wfile.write("\r\n")
        self.wfile.write("0\r\n")
        self.wfile.write("\r\n")
        self.wfile.flush()

    def send_chunked_stream(self, headers, content_type, stream):
        self.send_response(200, 'OK')
        self.send_headers(headers)
        self.send_header('Content-Type', content_type)
        self.send_header('Transfer-Encoding', 'chunked')
        self.end_headers()
        c = True
        while c:
            data = stream.read(65535)
            if (len(data) > 0):
                length = len(data)
                self.wfile.write("%x\r\n" % (len(data)))
                self.wfile.write(data)
                self.wfile.write("\r\n")
            else:
                c = False
        self.wfile.write("0\r\n")
        self.wfile.write("\r\n")
        self.wfile.flush()

    def send_start_stream(self, headers, content_type):
        self.send_response(200, 'OK')
        self.send_headers(headers)
        self.send_header('Content-Type', content_type)
        self.send_header('Transfer-Encoding', 'chunked')
        self.end_headers()

    def send_to_stream(self, data):
        length = len(data)
        self.wfile.write("%x\r\n" % (len(data)))
        self.wfile.write(data)
        self.wfile.write("\r\n")

    def send_end_stream(self):
        self.wfile.write("0\r\n")
        self.wfile.write("\r\n")
        self.wfile.flush()
