# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
import xmlrpclib
import transport
import sys
import time
from base64 import b64decode
from coils.net import *

#transport.set_proxy("squid.mormail.com:3128")
class Proxy(Protocol, PathObject):
    __pattern__   = 'proxy'
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        self.name = 'proxy'
        PathObject.__init__(self, parent, **params)

    def local_methods(self):
        return [ 'zogi.getLoginAccount' ]

    def do_POST(self):
        request = self.request
        # Set authorization information
        authorization = request.headers.get('authorization')
        if (authorization == None):
            raise AuthenticationException('Authentication Required')
        (kind, data) = authorization.split(' ')
        if (kind == 'Basic'):
            (username, _, password) = b64decode(data).partition(':')
        else:
            raise 'Proxy can only process Basic authentication'
            return

        # Break down request
        payload = request.get_request_payload()
        rpc = xmlrpclib.loads(payload, use_datetime=True)

        # Issue request
        x = transport.Transport()
        x.credentials = (username, password)
        if rpc[1] in self.local_methods():
            self.log.info('Proxy selecting local method for call to {0}'.format(rpc[1]))
            server = XMLRPCServer(self, self.parent._protocol_dict['RPC2'], context=self.context,
                                                                             request=self.request)
            server.do_POST()
            return
        else:
            self.log.info('Proxy calling remote method for call to {0}'.format(rpc[1]))
            server = xmlrpclib.Server('http://localhost/zidestore/so/%s/' % username,
                                      transport=x)
        method = getattr(server, rpc[1])
        for attempt in range(1, 3):
            try:
                result = method(*rpc[0])
                break
            except xmlrpclib.ProtocolError, err:
                self.log.warn('****Protocol Error, trying again in 0.5 seconds****')
                self.log.exception(err)
                time.sleep(0.5)
            except xmlrpclib.Fault, err:
                # Return the fault to the client; this is BROKEN!
                self.log.warn('Fault code: %d' % err.faultCode)
                self.log.warn('Fault string: %s' % err.faultString)
                return
            except Exception, err:
                self.log.exception(err)
                request.send_response(500, 'XML-RPC Request Failed')
                request.end_headers()
                return
        result = xmlrpclib.dumps(tuple([result]), methodresponse=True)
        request.send_response(200, 'OK')
        request.send_header('Content-Type', 'text/xml')
        request.end_headers()
        request.wfile.write(result)
        return
