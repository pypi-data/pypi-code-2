#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
DBus

Dbus connection and wrrapper classes
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
# pylint:disable-msg=W0406
import dbus
import dbus.service
import dbus.mainloop.glib
import functools

__all__ = ['RPCObject', 'Connection', 'rpc_method']

# Project requirements
from sleipnir.core.singleton import Singleton

# local submodule requirements
from . import constants


#pylint: disable-msg=E1101
class Connection(Singleton):
    """A Wrapper around session dbus"""

    def __init__(self, name=constants.__appname__, instance_name=None):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SessionBus()
        self._bus_name = name
        self._bus_instance = "".join(("/", instance_name))
        self._remote = None

    def __register(self):
        """
        Try to register get a previously registered instance. if fails
        take ownership of bus for name
        """
        if not self._remote:
            if self._bus_instance:
                try:
                    self._remote = self._bus.get_object( \
                        self._bus_name,                  \
                        self._bus_instance)
                    return
                except dbus.DBusException:
                    pass
            self._remote = dbus.service.BusName(self._bus_name, self._bus)

    @property
    def session_bus(self):
        """Get session bus"""
        return self._bus

    @property
    def bus_name(self):
        """Get registered service name"""
        return self._bus_name

    @property
    def bus_object_name(self):
        """Get registered service instance"""
        return self._bus_instance

    def is_client(self):
        """Check if a connection to a remote was established"""
        self.__register()
        return type(self._remote) not in (dbus.service.BusName,)

    def is_server(self):
        """True if we are the implementation server"""
        return not self.is_client

    def get_interface(self, interface):
        """Get a remote interface to 'interface'"""
        assert self.is_client()
        return dbus.Interface(self._remote, interface)


#pylint: disable-msg=R0903, R0923
class RPCObject(dbus.service.Object):
    """A weapper around an inplemented service"""

    def __init__(self, connection, wrapper):
        # export this object to dbus
        session_bus = connection.session_bus
        session_nam = connection.bus_object_name
        dbus.service.Object.__init__(self, session_bus, session_nam)
        self._wrapper = wrapper
        self._bus = connection

        # To export a Qt signal as a DBus-signal, you need to connect
        # it to a method in this class.  The method MUST have the
        # signal annotation, so python-dbus will export it as a
        # dbus-signal

    @property
    def wrapper(self):
        """Gets wrapper object"""
        return self._wrapper

#pylint: disable-msg=C0103
rpc_method = functools.partial(dbus.service.method, out_signature='')
