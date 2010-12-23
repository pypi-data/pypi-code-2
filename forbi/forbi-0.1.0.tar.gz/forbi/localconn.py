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

# This file is based on an example by Red Hat Inc. and Collabora Ltd.
#
# Copyright (C) 2004-2006 Red Hat Inc. <http://www.redhat.com/>
# Copyright (C) 2005-2007 Collabora Ltd. <http://www.collabora.co.uk/>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the 'Software'), to deal in the Software without
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## D-Bus specifics

import dbus
import dbus.service
import dbus.mainloop.glib
import gobject
import traceback

# Make sure threads work nicely together with gobject
gobject.threads_init()

class LocalServerObject(dbus.service.Object):
    def __init__(self, parent, *args):
        self.parent = parent
        dbus.service.Object.__init__(self, *args)

    # Receive an array of strings (as) and return a string (s)
    @dbus.service.method('org.forbi', in_signature='as', out_signature='s')
    def request(self, args):
        args = map(unicode, args)
        return self.parent.receive(args)

class LocalServer(object):
    """A D-Bus server listening for commands sent by D-Bus clients"""
    def __init__(self, parent):
        self.parent = parent
    
    def start(self):
        """Prepare the D-Bus loop"""
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        self.session_bus = dbus.SessionBus()
        self.name = dbus.service.BusName('org.forbi', self.session_bus)
        self.object = LocalServerObject(self, self.session_bus, '/Server')

        self.mainloop = gobject.MainLoop()

    def receive(self, args):
        """
        Receive commands and forward them to this server object's
        parent object
        """
        try:
            return self.parent.receive_local_command(args)
        except Exception:
            traceback.print_exc()

    def run(self):
        """Start the D-Bus loop"""
        self.mainloop.run()

class LocalClient(object):
    """A D-Bus client sending commands to a D-Bus server"""
    def __init__(self):
        self.bus = dbus.SessionBus()
        # Connect to the server
        self.remote_object = self.bus.get_object('org.forbi', '/Server')
        self.interface = dbus.Interface(self.remote_object, 'org.forbi')

    def send(self, args):
        """Send a command -- an array of strings -- to the server"""
        reply = unicode(self.interface.request(args))
        return reply

if __name__ == '__main__':
    # A simple server
    class SimpleParent(object):
        def receive_local_command(self, args):
            print 'received', repr(args)
    s = LocalServer(SimpleParent())
    s.start()
    s.run()
