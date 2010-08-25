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
from coils.core import Broker
import BaseHTTPServer, socket, os

class CoilsHTTPServer(BaseHTTPServer.HTTPServer):

    def __init__(self, listen, handler):
        BaseHTTPServer.HTTPServer.__init__(self, listen, handler)
        self.protocol_version = 'HTTP/1.1'
        self.socket.settimeout(60)
        self._shutdown = False
        self._name = 'coils.http.{0}'.format(os.getpid())
        self._broker = Broker()
        self._broker.subscribe(self._name, self.receive_message)

    @property
    def broker(self):
        return self._broker

    def server_bind(self):
        BaseHTTPServer.HTTPServer.server_bind(self)

    def receive_message(self, message):
        return

    def check_messages(self):
        pass

    def get_request(self):
        while not self._shutdown:
            try:
                #print ' HTTP worker {0} waiting for connection.'.format(self.pid)
                #self.log.debug('Waiting for connection...')
                s, a = self.socket.accept()
                s.settimeout(None)
                return (s, a)
            except socket.timeout:
                self.check_messages()
        return None, None
