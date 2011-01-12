# -*- coding: utf-8 -*-

# This file is part of the Rocket Web Server
# Copyright (c) 2009 Timothy Farrell

# Import System Modules
import sys
import time
import socket
try:
    from io import StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
try:
    import ssl
    has_ssl = True
except ImportError:
    has_ssl = False
# Import Package Modules
from . import IS_JYTHON, SOCKET_TIMEOUT, BUF_SIZE

class Connection(object):
    __slots__ = [
        'buffer',
        'client_addr',
        'client_port',
        'fileno',
        'makefile',
        'read',
        'secure',
        'sendall',
        'server_port',
        'setblocking',
        'shutdown',
        'socket',
        'ssl',
        'start_time',
    ]

    def __init__(self, sock_tuple, port, secure=False):
        self.buffer = StringIO()
        
        self.client_addr, self.client_port = sock_tuple[1]
        self.server_port = port
        self.socket = sock_tuple[0]
        self.start_time = time.time()
        self.ssl = has_ssl and isinstance(self.socket, ssl.SSLSocket)
        self.secure = secure

        if IS_JYTHON:
            # In Jython we must set TCP_NODELAY here since it does not
            # inherit from the listening socket.
            # See: http://bugs.jython.org/issue1309
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.socket.settimeout(SOCKET_TIMEOUT)

        self.sendall = self.socket.sendall
        self.shutdown = self.socket.shutdown
        self.fileno = self.socket.fileno
        self.makefile = self.socket.makefile
        self.setblocking = self.socket.setblocking
        
        self.read = self.socket.recv
        
    def readline(self, buf_size=BUF_SIZE):
        data = b('')
        data_read = 0
        c = self.read(1)
        while c and c != b('\n') and data_read < buf_size:
            data += c
            c = self.read(1)
            data_read += 1
        data += c
        return data

    def read(self, size):
        return self.socket.recv(size)

    def close(self):
        if hasattr(self.socket, '_sock'):
            try:
                self.socket._sock.close()
            except socket.error:
                info = sys.exc_info()
                if info[1].errno != socket.EBADF:
                    raise info[1]
                else:
                    pass
        self.socket.close()
