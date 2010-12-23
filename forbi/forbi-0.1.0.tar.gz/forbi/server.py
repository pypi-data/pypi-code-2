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
##[ Description ]## Server communicator

from forbi.communicator import ForbiCommunicator, \
    ForbiRequestHandler, ForbiSocket
import forbi.misc as misc
import forbi.usersaves as usersaves
import forbi.connlist as connlist
import forbi.crypt as crypt
import socket
import time

class ForbiServer(ForbiCommunicator):
    """
    A server capable of receiving and sending messages from and to an
    arbitrary number of sources independently
    """
    def __init__(self, port=54547, host='', **kwds):
        self.port = port
        self.host = host

        self.default_client_port = kwds.get(u'default_client_port') or \
            self.port

        self.user_saves = usersaves.UserSaves(kwds.get(u'save_file'))
        self.connections = connlist.ConnectionsList()

        # Create the server handler
        ForbiCommunicator.__init__(
            self, self.port, '', ForbiServerRequestHandler,
            kwds.get(u'runner'))

    def start(self):
        """Start the server"""
        self.set_output_prefix(u'server')
        ForbiCommunicator.start(self)
        self.port = self.serving_port
        self.user_saves.load()
        self.run()

class ForbiServerRequestHandler(ForbiRequestHandler):
    """
    A request handler that creates a new socket back to the source
    whenever a new connection is made
    """
    def start(self):
        """Finalize the connection"""
        self.conn_info = \
            self.parent.connections.add(addr=self.client_address)
        self.addr_text_recv = repr(self.conn_info.addr)
        self.ping_thread = None

    def end(self):
        # Terminate ping thread
        if self.ping_thread is not None:
            self.ping_thread.terminate()
        # Remove this connection from list of connections
        if self.conn_info.user is not None:
            self.state(u'%s logged out' % repr(self.conn_info.user)[1:])
        self.parent.connections.remove(self.conn_info)
        self.end = misc.nothing # If it's called again

    def connect_back(self):
        """Create a connection back to the source connector"""
        self.state(u'creating socket to %s...' % \
                       repr(self.client_address[0]))
        self.addr_text_send = repr((self.conn_info.addr[0],
                                    self.conn_info.port))
        self.sender = ForbiSocket(self.conn_info.addr[0],
                                  self.conn_info.port,
                                  self.parent.priv_key)
        self.conn_info.sender = self.sender
        if self.do_crypt:
            self.sender.pub_key = self.pub_key
            self.sender.do_crypt = True

        self.state(u'address %s uses %d as server port' %
                   (self.addr_text_recv, self.conn_info.port))
        self.state(u'sending identifier string back to %s' % self.addr_text_send)
        ans = self.send('id ' + self.conn_info.id, False)
        if ans == u'ok':
            self.state(u'%s has accepted identifier string' %
                       self.addr_text_send)
        else:
            self.error(u'%s has not accepted identifier string' %
                       self.addr_text_send)
            raise misc.ForbiError
        self.ping_thread = misc.BasicQuickThread(self.ping)
        self.ping_thread.start()

    def ping(self):
        """Ping source connector with an interval of 256 seconds"""
        self.state(u'started pinging %s.' % self.addr_text_send)
        while True:
            if self.ping_thread.do_terminate:
                break
            try:
                self.state(u'pinging %s.' % self.addr_text_send)
                if self.send(u'ping') != u'pong':
                    self.error(u'did not receive a pong from %s.'
                               % self.addr_text_send)
                    break
                time.sleep(256)
            except Exception:
                break
        self.state(u'stopped pinging %s.' % self.addr_text_send)
        try:
            self.request.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass

    def send(self, msg, utf8=True):
        """Send a message"""
        return self.sender.send(msg, utf8)

    def receive(self, msg):
        """Receive a message and act on it"""
        if msg.startswith('public_key '):
            # Receive public key from client and send own public key back
            pub_key_str = msg.split(' ', 1)[1]
            pub_key = crypt.create_pub_key_from_string(pub_key_str)
            self.pub_key = pub_key
            self.answer(self.parent.pub_key_str, False)
            self.do_crypt = True
            self.state(u'now using encryption')

        elif msg.startswith(u'version '):
            # Receive client version and compare with own version
            client_version = msg.split(u' ', 1)[1]
            self.answer(misc.version_num_text)
            if tuple(map(int, client_version.split(u'.'))) > \
                    misc.version_num:
                self.error(u'incompatible versions with %s' % self.addr_text_recv)
                return True
            self.state(u'client at %s using version %s' %
                       (self.addr_text_recv, client_version))
            self.state(u'server using version %s' % misc.version_num_text)
            self.state(u'versions compatible')

        elif msg.startswith('id '):
            # Receive random id string and save for later when
            # identification is needed
            self.state(u'received identifier string from %s' % self.addr_text_recv)
            self.conn_info.id = msg.split(' ', 1)[1]
            self.answer(u'ok')

        elif msg.startswith(u'port'):
            # Receive client listening port number and create a
            # connection to it
            self.state(u'received port number from %s' % self.addr_text_recv)
            if u' ' in msg:
                port = int(msg.split(u' ', 1)[1])
            else:
                port = self.parent.default_client_port
            self.conn_info.port = port
            self.answer(u'ok')
            self.connect_back()

        elif msg.startswith(u'register '):
            # Attempt to register the user
            user, password = msg.split(u' ', 1)[1].split(u'\t')
            try:
                self.parent.user_saves.add(user, password)
                self.answer(u'ok')
            except AssertionError:
                self.answer(u'error 1')

        elif msg.startswith(u'login '):
            # Attempt to login
            user, password = msg.split(u' ', 1)[1].split(u'\t')
            if user in self.parent.connections.get_users():
                self.answer(u'error 1')
            elif not self.parent.user_saves.has(user):
                self.answer(u'error 3')
            elif not self.parent.user_saves.match(user, password):
                self.answer(u'error 2')
            else:
                self.state(u'%s logged in' % repr(user)[1:])
                self.conn_info.user = user
                self.answer(u'ok')

        elif msg == 'logout':
            # Attempt to logout
            if self.conn_info.user is not None:
                self.state(u'%s logged out' % repr(self.conn_info.user)[1:])
                # The only way to tell if there is someone logged in
                # from this connection is to look at self.conn_info.user
                self.conn_info.user = None
                self.answer(u'ok')
            else:
                self.answer(u'error no one logged in')

        elif msg == 'unregister':
            # Attempt to unregister (and logout at the same time)
            if self.conn_info.user is not None:
                self.parent.user_saves.remove(self.conn_info.user)
                self.state(u'%s unregistered' % repr(self.conn_info.user)[1:])
                self.conn_info.user = None
                self.answer(u'ok')
            else:
                self.answer(u'error no one logged in')

        elif msg == u'exit':
            # Client shuts down, end this thread
            self.end()
            self.answer(u'ok')
            return True

        elif msg == u'users':
            # Send a list of users back (but only if the client is
            # logged in)
            if self.conn_info.user is not None:
                self.answer(u'ok ' + u'\t'.join(sorted(self.parent.connections.get_users())))
            else:
                self.answer(u'error')

        elif msg.startswith(u'message '):
            # Attempt to forward the message
            user_to, mesg = msg.split(u' ', 1)[1].split(u'\t')
            user_from = self.conn_info.user
            self.state(u'message from %s to be sent to %s' %
                       (repr(user_from)[1:], repr(user_to)[1:]))
            conn = self.parent.connections.find(user=user_to)
            if conn is None:
                self.answer(u'error user does not exist')
            else:
                self.answer(u'ok')
                conn.sender.send(u'message %s\t%s' % (user_from, mesg))
