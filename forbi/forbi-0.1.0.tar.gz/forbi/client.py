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
##[ Description ]## Client communicator

import sys
import socket

from forbi.communicator import ForbiCommunicator, \
    ForbiRequestHandler, ForbiSocket
import forbi.misc as misc
import forbi.crypt as crypt
import forbi.localconn as localconn
import forbi.messagereceived as msgrecv

class ForbiClient(ForbiCommunicator):
    """A client server meant for requesting data from a remote server"""
    def __init__(self, host, port=54547, user=None, password=None,
                 **kwds):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.sender = None
        self.logged_in = False

        self.client_port = kwds.get('client_port') or self.port
        self.program = kwds.get('program')

        # Create the client server handler
        ForbiCommunicator.__init__(
            self, self.client_port, '', ForbiClientRequestHandler,
            kwds.get('runner'))

    def start(self):
        """Start the local server and connect to the remote server"""
        if self.host is None:
            self.host = self.runner.get_input(u'Enter host: ')
        self.set_output_prefix(u'client')
        ForbiCommunicator.start(self)
        self.client_port = self.serving_port
        self.addr_text_send = repr((self.host, self.port))
        self.state(u'creating socket to %s' % repr((self.host,
                                                   self.port)))
        self.sender = ForbiSocket(self.host, self.port, self.priv_key)
        self.identifier_string = crypt.generate_random_bytes()
        self.run()

    def send(self, msg, utf8=True):
        """Send a message to the remote server"""
        try:
            return self.sender.send(msg, utf8)
        except socket.error, e:
            self.error(u'socket error: %s' % str(e))

    def run(self):
        """Perform basic post-connection stuff"""
        self.state(u'exchanging public keys')
        pub_key_str = self.send('public_key %s' % self.pub_key_str,
                                False)
        pub_key = crypt.create_pub_key_from_string(pub_key_str)
        self.sender.pub_key = pub_key
        self.server_pub_key = pub_key
        self.sender.do_crypt = True
        self.do_crypt = True
        self.state(u'now using encryption')

        self.state(u'exchanging version numbers')
        server_version = self.send(u'version %s' %
                                   misc.version_num_text)
        if tuple(map(int, server_version.split(u'.'))) < misc.version_num:
            self.error(u'versions incompatible')
            sys.exit()
        self.state(u'client using v%s' % misc.version_num_text)
        self.state(u'server using v%s' % server_version)
        self.state(u'versions compatible')

        self.state(u'sending identifier string to server')
        if self.send('id %s' % self.identifier_string, False) != u'ok':
            self.error(u'not ok')
            return

        self.state(u'sending port number to server')
        if self.send(u'port %s' % self.client_port) != u'ok':
            self.error(u'not ok')
            return

        if self.user is None or self.password is None:
            self.state(u'creating user...')
            if self.user is None:
                while True:
                    user = self.runner.get_input(u'Enter user name: ')
                    if user == '':
                        self.error(u'username cannot be empty')
                    elif '\t' in user:
                        self.error(u'username cannot contain tabs')
                    else:
                        break
                self.user = user
            if self.password is None:
                while True:
                    password = self.runner.get_input(u'Enter password: ', False)
                    if password == '':
                        self.error(u'password cannot be empty')
                        continue
                    password_check = self.runner.get_input(u'Reenter password: ', False)
                    if password != password_check:
                        self.error(u'the two passwords do not match')
                    else:
                        break
                self.password = password
        try:
            self.login()
        except misc.ForbiError:
            return
        
        self.state(u'asking for list of online users')
        users = self.send(u'users')
        if users.startswith(u'ok '):
            users = u', '.join(repr(x)[1:] for x in users.split(u' ', 1)[1].split(u'\t'))
        else:
            users = u'none'
        self.state(u'users online: %s' % users)

        self.local_connection_server = localconn.LocalServer(self)
        self.local_connection_server.start()
        misc.QuickThread(self.local_connection_server.run)
        ForbiCommunicator.run(self)

    def receive_local_command(self, all_args):
        """Receive command from computer via D-Bus and act on it"""
        command = all_args[0]
        args = all_args[1:]

        if command == u'message':
            # Receive and show message
            if not self.logged_in:
                return u'error: not logged in'
            recp = repr(args[0])[1:]
            self.state(u'sending message to %s' % recp)
            msg = u'%s %s\t%s' % tuple(all_args)
            ans = self.send(msg)
            if ans == u'ok':
                self.state(u'message to %s succesfully sent' % recp)
                return u'ok'
            elif ans.startswith(u'error'):
                if u' ' in ans:
                    extra = u': ' + ans.split(u' ', 1)[1]
                else:
                    extra = ''
                self.error(u'message to %s not sent%s' % (recp, extra))
                return u'error%s' % extra
            else:
                self.error(u'not ok')
                return u'not ok'
                raise misc.ForbiError

        elif command == u'users':
            # Receive list of users
            ans = self.send(u'users')
            if ans.startswith(u'ok '):
                ans = ans.split(u' ', 1)[1]
                if ans:
                    return u', '.join([repr(u)[1:] for u in ans.split('\t')])
                else:
                    return u'none'
            else:
                return u'error: not logged in'

        elif command == u'logout':
            # Logout
            try:
                self.logout()
                return u'ok'
            except misc.ForbiError:
                return u'error: %s' % self.runner.prev_error

        elif command == u'exit':
            # Exit completely
            self.exit()
            return u'ok'

        elif command == u'login':
            # Login (and register if necessary)
            if self.logged_in:
                return u'error: currently logged in as %s' % repr(self.user)[1:]
            else:
                self.user, self.password = args
                try:
                    self.login()
                    return u'ok'
                except misc.ForbiError:
                    return u'error: %s' % self.runner.prev_error

        elif command == u'register':
            # Register (but don't login)
            if self.logged_in:
                return u'error: currently logged in as %s' % repr(self.user)[1:]
            else:
                self.user, self.password = args
                try:
                    self.register()
                    return u'ok'
                except misc.ForbiError:
                    return u'error: %s' % self.runner.prev_error

        elif command == u'unregister':
            # Unregister
            try:
                self.unregister()
                return u'ok'
            except misc.ForbiError:
                return u'error: %s' % self.runner.prev_error

    def login(self):
        """Attempt to login to remote server"""
        self.state(u'attempting to log in...')
        ans = self.send(u'login %s\t%s' % (self.user, self.password))
        if ans.startswith(u'error'):
            if u' ' in ans:
                errnum = int(ans.split(u' ', 1)[1])
            else:
                errnum = 0
            if errnum == 1:
                self.error(u'user is already logged in on server')
                raise misc.ForbiError
            elif errnum == 2:
                self.error(u'incorrect password')
                raise misc.ForbiError
            elif errnum == 3:
                self.error(u'user does not exist on server')
                self.register()
                self.login()
            else:
                self.error(u'not ok')
                raise misc.ForbiError
        else:
            self.state(u'succesfully logged in')
            self.logged_in = True

    def register(self):
        """Attempt to register user on the server"""
        self.state(u'attempting to register...')
        ans = self.send(u'register %s\t%s' % (self.user,
                                              self.password))
        if ans.startswith(u'error'):
            if u' ' in ans:
                errnum = int(ans.split(u' ', 1)[1])
            else:
                errnum = 0
            if errnum == 1:
                self.error(u'user is already registered on server')
                raise misc.ForbiError
            else:
                self.error(u'not ok')
                raise misc.ForbiError
        else:
            self.state(u'succesfully registered')

    def logout(self):
        """Logout from remote server"""
        self.state(u'logging out...')
        if not self.logged_in:
            self.error(u'not logged in')
            raise misc.ForbiError
        ans = self.send(u'logout')
        if ans == u'ok':
            self.state(u'logged out')            
            self.logged_in = False
        else:
            self.error(u'not ok')
            raise misc.ForbiError

    def unregister(self):
        """Unregister on remote server"""
        self.state(u'unregistering...')
        if not self.logged_in:
            self.error(u'not logged in')
            raise misc.ForbiError
        ans = self.send(u'unregister')
        if ans == u'ok':
            self.state(u'unregistered')
            self.logged_in = False
            self.user = None
            self.password = None
        else:
            self.error(u'not ok')
            raise misc.ForbiError

    def exit(self):
        """Send an exit message to the server and quit"""
        self.state(u'exiting...')
        self.send(u'exit')
        self.end()

    def end(self):
        """Stop the sender socket and end everything"""
        self.end = misc.nothing
        try:
            self.exit()
        except misc.ForbiError:
            pass
        if self.sender is not None:
            self.sender.close()
        ForbiCommunicator.end(self)

class ForbiClientRequestHandler(ForbiRequestHandler):
    """A request handler with support for ponging and receiving messages"""
    def start(self):
        """Finalize the connection"""
        self.addr_text_recv = repr(self.client_address)
        self.is_server = None
        msgrecv.init(self.parent.program)

    def end(self):
        if self.is_server:
            self.parent.end()

    def receive(self, msg):
        """
        Receive and check identification strings and, if the server
        succesfully identifies itself as being the server, continue
        with receiving other commands.
        """
        if msg.startswith('id'):
            if ' ' in msg and msg.split(' ', 1)[1] == \
                    self.parent.identifier_string:
                self.state(u'received matching identifier string from server')
                self.is_server = True
                self.receive = self.server_receive
                self.answer(u'ok')
            else:
                if msg == 'id':
                    self.error(u'received empty identifier string from server')
                else:
                    self.error(u'received non-matching identifier string from server')
                self.is_server = False
                self.receive = self.foreign_client_receive

    def server_receive(self, msg):
        """Receive a message from a remote server and act on it"""
        if msg == u'ping':
            # Ping.. pong..
            self.state(u'received ping from server. Ponging.')
            self.answer(u'pong')
        elif msg.startswith(u'message '):
            # Show message using either internal GUI or external program
            user_from, mesg = msg.split(u' ', 1)[1].split(u'\t')
            self.state(u'message received from server. Showing.')
            msgrecv.new_message(user_from, self.parent.user, mesg)
            self.answer(u'ok')

    def foreign_client_receive(self, msg):
        # Foreign clients aren't meant to contact other clients
        # directly, so this is left out intentionally, not because I
        # was too lazy to implement it. Nevertheless, it could work.
        pass
