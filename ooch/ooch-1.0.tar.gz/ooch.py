'''Mooching files with Python

Sharing files on a local network made kinda easy.

**Share files with:**

  python -mooch -s filename filename dirname

Sharing a dirname shares all the files in that directory.

**Find files to mooch:**

  python -mooch

**Mooch a specific file / directory with:**

  python -mooch pathname

Use python -mooch to discover the other command-line arguments, such as
verbosity and port number controls.


Version History (in Brief)
--------------------------

- 1.0 is the initial release

See the end of the source file for the license of use.
'''
__version__ = '1.0'

import os
import sys
import json
import socket
import optparse

from twisted.internet import reactor
from twisted.internet import protocol
from twisted.python import log
from twisted.web.client import Agent
from twisted.internet import task
from twisted.internet import error
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.web.static import File


#
# CLIENT
#
class Client(protocol.DatagramProtocol):
    def __init__(self, fetch_files):
        self.seen = {}
        self.fetch_files = fetch_files
        # wait for at least 1 second to allow all the servers to announce
        reactor.callLater(1, self.maybeShutdown)

    def startProtocol(self):
        self.transport.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)

    def datagramReceived(self, data, addr):
        key = ip_address, port = tuple(data.split(';'))
        if key in self.seen:
            return
        self.seen[key] = RemoteFiles(ip_address, port, fetch_files=self.fetch_files)

    def maybeShutdown(self):
        files_missing = set(self.fetch_files)
        for r in self.seen.values():
            if not r.done:
                reactor.callLater(1, self.maybeShutdown)
                return
            else:
                files_missing -= r.files_fetched
        if files_missing:
            print 'Unavailable files:'
            for filename in files_missing:
                print ' ', filename
        reactor.stop()

class CallbackResponse(protocol.Protocol):
    def __init__(self, callback):
        self.callback = callback
        self.data = []

    def dataReceived(self, bytes):
        self.data.append(bytes)

    def connectionLost(self, reason):
        if isinstance(reason.type, error.ConnectionLost):
            log.info('client connection %r lost: %r'%(self,
                reason.getErrorMessage()))
            self.callback(None)
        else:
            self.callback(''.join(self.data))

class StoreResponse(protocol.Protocol):
    def __init__(self, filename):
        self.filename = filename
        if '/' in filename:
            d = os.path.dirname(filename)
            if not os.path.exists(d):
                os.makedirs(d)
        self.f = open(filename, 'wb')

    def dataReceived(self, bytes):
        self.f.write(bytes)

    def connectionLost(self, reason):
        self.f.close()
        if isinstance(reason.type, error.ConnectionLost):
            log.info('client connection %r lost: %r'%(self,
                reason.getErrorMessage()))
        else:
            print 'Fetched', self.filename

class RemoteFiles(object):
    def __init__(self, ip_address, port, fetch_files=[]):
        self.ip_address, self.port, self.fetch_files = ip_address, port, fetch_files
        self.agent = Agent(reactor)
        url = 'http://%s:%s/' % (ip_address, port)
        d = self.agent.request('GET', url)
        d.addCallback(self.listRequest)
        self.done = False
        self.files_fetched = set()

    def listRequest(self, response):
        if response.code == 200:
            response.deliverBody(CallbackResponse(self.gotList))
        else:
            print 'File listing failed:', response.phrase

    def gotList(self, contents):
        self.done = True
        if contents is None:
            print 'Failed to retrieve file list'
            return

        # ugh, map, str, ugh
        files = map(str, json.loads(contents))

        if not self.fetch_files:
            print 'Files offered by %s:%s are:' % (self.ip_address, self.port)
            for entry in files:
                print ' ', entry

        for filename in self.fetch_files:
            for avail in files:
                if filename == avail or avail.startswith(filename + '/'):
                    self.files_fetched.add(filename)
                    url = 'http://%s:%s/%s' % (self.ip_address, self.port, avail)
                    d = self.agent.request('GET', url)
                    d.addCallback(self.storeRequest, avail)

    def storeRequest(self, response, filename):
        if response.code == 200:
            response.deliverBody(StoreResponse(filename))
        else:
            print 'File fetch failed:', response.phrase

#
# SERVER
#
class Server(protocol.DatagramProtocol):
    def __init__(self, http_port, port):
        self.http_port = http_port
        self.port = port
        self.ip_address = socket.gethostbyname(socket.gethostname())

    def startProtocol(self):
        self.transport.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self.call = task.LoopingCall(self.tick)
        self.dcall = self.call.start(1)

    def stopProtocol(self):
        self.call.stop()

    def tick(self):
        self.transport.write(self.getPacket(), ("<broadcast>", self.port))

    def getPacket(self):
        return '%s;%s' % (self.ip_address, self.http_port)

    def datagramReceived(self, data, addr):
        if data == '%s;%s' % (self.ip_address, self.http_port):
            return
        # we've seen a peer who is also sharing data!
        pass

class Index(Resource):
    isLeaf = True
    def __init__(self, paths):
        self.paths = paths
        Resource.__init__(self)

    def render_GET(self, request):
        return json.dumps(self.paths)

#
# MAIN
#
def main():
    parser = optparse.OptionParser()
    parser.add_option('-p', '--http-port', dest='http_port', type="int", default=8880,
        help='the port to serve files on (default 8880)')
    parser.add_option('-b', '--broadcast-port', dest='broadcast_port', type="int", default=6624,
        help='the port to broadcast on (default 6624)')
    parser.add_option('-s', '--serve', action='store_true', dest='serve', default=False,
        help='serve files from the current directory')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False,
        help='be verbose on the console')
    args, paths = parser.parse_args()

    if args.verbose:
        log.startLogging(sys.stdout)

    if args.serve:
        if not paths:
            paths = os.listdir('.')
        l = []
        for p in paths:
            if os.path.isdir(p):
                for dirpath, dirnames, filenames in os.walk(p):
                    for f in filenames:
                        # XXX dirpath might be windows
                        l.append('%s/%s' % (dirpath, f))
            else:
                l.append(p)

        reactor.listenUDP(args.broadcast_port, Server(args.http_port, args.broadcast_port))
        root = Resource()
        root.putChild('', Index(l))
        for path in paths:
            root.putChild(path, File(os.path.abspath(path)))
        reactor.listenTCP(args.http_port, Site(root))
        reactor.run()
    else:
        reactor.listenUDP(args.broadcast_port, Client(paths))
        reactor.run()

if __name__ == '__main__':
    main()

# Copyright (c) 2011 Richard Jones <http://mechanicalcat.net/richard>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
