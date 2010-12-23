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
##[ Description ]## Functions for maintaining a list of connections

import forbi.misc as misc

class ConnectionInfo(misc.Container):
    """Info about a connection"""
    def __init__(self, **kwargs):
        # All of these arguments are not meant to be filled at once.
        self.addr = kwargs.get('addr')
        self.user = kwargs.get('user')
        self.port = kwargs.get('port')
        self.id = kwargs.get('id')
        self.sender = kwargs.get('sender')

class ConnectionsList(misc.Container):
    """A list of connections with info"""
    def __init__(self):
        self.connections = []

    def add(self, **kwargs):
        """Add a connection with as many or as few arguments as you want"""
        new_info = ConnectionInfo(**kwargs)
        self.connections.append(new_info)
        return new_info

    def remove(self, conn):
        """Remove a connection"""
        assert conn in self.connections, \
            'connection object not in connections list'
        self.connections.remove(conn)

    def get_users(self):
        """Get all usernames"""
        return set(x.user for x in self.connections if x.user is not None)

    def find(self, **kwds):
        """
        Find the first connection whose items match all of the
        keyword arguments
        """
        for conn in self.connections:
            ok = True
            for key, val in kwds.iteritems():
                if conn.__dict__[key] != val:
                    ok = False
                    break
            if ok:
                return conn
