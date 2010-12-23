#!/usr/bin/env python
# -*- coding: utf-8 -*-

# forbi: a TCP-based communication tool
# Copyright (C) 2010  Niels Serup

# This file is part of forbi.
#
# forbi is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# forbi is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General
# Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with forbi. If not, see
# <http://www.gnu.org/licenses/>.

##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Generic classes for sending and receiving data

import socket
import SocketServer
import threading
import time
import struct
import random
import traceback

import forbi.crypt as crypt
import forbi.misc as misc

class SenderReceiverEncoderDecoder(object):
    """Encodes when sending, decodes when receiving"""
    def encode(self, msg, pub_key=None, do_encrypt=False, utf8=True):
        """Encode and encrypt a message"""
        if utf8:
            msg = msg.encode('utf-8')
            msg += '1'
        else:
            msg += '0'
        if do_encrypt:
            # Creates 128-byte blocks, each with 86 or less characters
            # of the full message.
            omsg = msg
            msg = ''
            while omsg:
                # PKCS#1 requires 11 bytes of the RSA modulus, but
                # OAEP requires 41. 1024/8 - 41 = 87 bytes left.
                msg += crypt.encrypt(omsg[:86], pub_key)
                omsg = omsg[86:]
        len_str = struct.pack('<I', len(msg) + 4)
        msg = len_str + msg
        return msg

    def decode(self, recv, priv_key=None, do_decrypt=False):
        """Decode and decrypt a message"""
        msg = recv(4096)
        try:
            msg_len = struct.unpack('<I', msg[:4])[0]
        except struct.error:
            raise misc.ForbiError('lost connection')
        msg = msg[4:]
        idx = 4096
        while idx < msg_len:
            msg += recv(4096)
            idx += 4096
        if do_decrypt:
            omsg = msg
            msg = ''
            while omsg:
                # 1024 / 8 = 128
                msg += crypt.decrypt(omsg[:128], priv_key)
                omsg = omsg[128:]
        utf8 = bool(int(msg[-1:]))
        msg = msg[:-1]
        if utf8:
            msg = msg.decode('utf-8')
        return msg

class ForbiSocket(SenderReceiverEncoderDecoder):
    """
    A high level socket class capable of receiving and sending large
    amounts of data in one go with or without encryption
    """
    def __init__(self, host, port=54547, priv_key=None):
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.pub_key = None
        self.priv_key = priv_key
        self.do_crypt = False

        # Create a socket
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        # Connect to it
        self.socket.connect(self.addr)

    def send(self, msg, utf8=True):
        """Send a message"""
        msg = self.encode(msg, self.pub_key, self.do_crypt, utf8)
        self.socket.sendall(msg)
        return self.recv()

    def recv(self):
        """Receive an answer"""
        return self.decode(self.socket.recv, self.priv_key, self.do_crypt)

    def close(self):
        self.socket.close()

    def end(self):
        self.close()

class BasicThreadedTCPServer(SocketServer.ThreadingMixIn,
                             SocketServer.TCPServer):
    pass

class ThreadedTCPServer(BasicThreadedTCPServer):
    def __init__(self, addr, handler, parent):
        self.parent = parent
        BasicThreadedTCPServer.__init__(self, addr, handler)

class ForbiRequestHandler(SocketServer.BaseRequestHandler,
                          SenderReceiverEncoderDecoder):
    """A base request handler"""
    def setup(self):
        # Setup variables for when new requests come in
        self.parent = self.server.parent
        self.priv_key = None
        self.pub_key = None
        self.do_crypt = False
        self.state = self.parent.state
        self.error = self.parent.error
        self.state(u'connected to %s' % repr(self.client_address))
        self.start()

    def handle(self):
        # Continously handle incoming messages
        self.state(u'started handling requests from %s' % repr(self.client_address))
        while True:
            try:
                msg = self.recv()
                if not msg:
                    raise Exception(u'no more messages')
                if self.receive(msg):
                    break
            except socket.error:
                break
            except Exception, e:
                self.error(u'handling error: %s' % repr(e))
#                traceback.print_exc()
                break
        self.state(u'stopped handling requests from %s' % repr(self.client_address))
        self.end()

    def receive(self, msg):
        """
        Is run when a new message is received (should be overridden by
        subclasses)
        """

    def answer(self, msg, utf8=True):
        self.request.sendall(self.encode(
                msg, self.pub_key or self.parent.server_pub_key,
                self.do_crypt or self.parent.do_crypt, utf8))

    def recv(self):
        return self.decode(self.request.recv, self.priv_key or
                           self.parent.priv_key, self.do_crypt
                           or self.parent.do_crypt)

    def start(self):
        """Is run after setup (should be overridden by subclasses)"""

    def end(self):
        """
        Is run when there is nothing more to handle (should be
        overridden by subclasses)
        """

class ForbiCommunicator(misc.TextOutputter):
    """A commmunicator server receiving and answering messages"""
    def __init__(self, serving_port=54547, server_host='',
                 handler=None, runner=None):
        self.serving_port = serving_port
        self.server_host = server_host
        self.server = None
        self.handler = handler or ForbiRequestHandler
        self.pub_key = None
        self.priv_key = None
        self.runner = runner
        self.quit_program = False
        misc.TextOutputter.__init__(self, self.runner)
        
    def start(self):
        """Start the communicator"""
        self.state(u'generating keys...')
        self.do_crypt = False
        self.generate_keys()
        self.server_pub_key = None

        self.state(u'creating server...')

        # Create a threaded TCP server
        if self.serving_port != -1:
            self.server = ThreadedTCPServer((self.server_host, self.serving_port),
                                            self.handler, self)
        else:
            while True:
                serving_port = random.randint(49152, 65536)
                try:
                    self.server = ThreadedTCPServer(
                        (self.server_host, serving_port),
                        self.handler, self)
                    break
                except socket.error, e:
                    if e[0] == 98: # "Address already in use"
                        continue
                    else:
                        traceback.print_exc()
                        break
            self.serving_port = serving_port
        
        self.server_ip, self.serving_port = self.server.server_address

        # Run the server in a thread. This thread will start a new
        # thread for every client connection request
        self.server_thread = threading.Thread(target=self.server.serve_forever)

        # Exit the server thread when the main thread terminates
        self.server_thread.setDaemon(True)
        self.server_thread.start()

        self.state('serving on port %d' % self.serving_port)

    def generate_keys(self):
        """Generate keypair"""
        self.priv_key, self.pub_key, self.pub_key_str = \
            crypt.generate_keys()

    def run(self, extra_func=None):
        """Run communicator server without end"""
        if extra_func is None:
            extra_func = lambda: time.sleep(.5)
        self.state(u'running indefinitely...')
        while not self.quit_program:
            extra_func()

    def end(self):
        """End everything"""
        self.state(u'shutting down...')
        if self.server is not None:
            self.server.shutdown()
            self.quit_program = True
        self.end = misc.nothing
