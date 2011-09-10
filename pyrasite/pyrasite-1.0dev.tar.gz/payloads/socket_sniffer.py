# This file is part of pyrasite.
#
# pyrasite is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyrasite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyrasite.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2011 Red Hat, Inc.

import sys
import socket
import httplib

_socket = socket.socket

_request = httplib.HTTPConnection.request
def request(self, *args, **kw):
    print locals()
    return _request(self, *args, **kw)
httplib.HTTPConnection.request = request

_getresponse = httplib.HTTPConnection.getresponse
def getresponse(self, *args, **kw):
    print locals()
    return _getresponse(self, *args, **kw)
httplib.HTTPConnection.getresponse = _getresponse

class SocketSniffer(_socket):

    def connect(self, *args, **kw):
        print "connect(%s)" % locals()
        return _socket.connect(self, *args, **kw)
    
    def send(self, *args, **kw):
        print "send(%s)" % locals()
        return _socket.send(self, *args, **kw)

    def sendall(self, *args, **kw):
        print "sendall(%s)" % locals()
        return _socket.sendall(self, *args, **kw)

    def sendto(self, *args, **kw):
        print "sendto(%s)" % locals()
        return _socket.sendto(self, *args, **kw)

    def read(self, *args, **kw):
        print "wtf"
        data = _socket.read(*args, **kw)
        print "read(%s)" % data
        return data

    # FIXME: for some reason these aren't getting called...
    def recv(self, *args, **kw):
        data = _socket.recv(*args, **kw)
        print "recv(%r)" % data
        return data

    def recvfrom(self, *args, **kw):
        print "wtf"
        data = _socket.recvfrom(*args, **kw)
        print "recvfrom(%r)" % data
        return data

    def recvfrom_into(self, *args, **kw):
        print "wtf"
        data = _socket.recvfrom_into(*args, **kw)
        print "recvfrom_into(%r)" % data
        return data

    def recv_into(self, *args, **kw):
        print "wtf"
        data = _socket.recv_into(*args, **kw)
        print "recv_into(%r)" % data
        return data

socket.socket = SocketSniffer
sys.modules['socket'] = socket
