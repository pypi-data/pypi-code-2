#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Shell

Main QML Shell instance
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
import sys

# QML required deps
from PySide.QtGui import QApplication

__all__ = ['QShell']

# Project requirements
from sleipnir.shell.shell import Shell

# local submodule requirements
from .lrpc import Connection, rpc_method, RPCObject
from .presenters import QWindowFactory
from .import constants


#pylint: disable-msg=E1101
class QShell(Shell):
    """Main Handset shell"""

    SHELL_DAEMON = "__Daemon"
    SHELL_WINDOWS = "__Windows"

    # pylint: disable-msg=R0923
    class RPC(RPCObject):
        """Wraps a Shell instance inside a RPC object"""

        @rpc_method(constants.__appname__, in_signature='biss')
        def create_window(self, new, screen, target, profiles):
            """creates a window"""
            window = self.wrapper.create_window(new, screen, target)
            window.show(profiles)

    def __init__(self, name="Handset"):
        # Build parent classes
        Shell.__init__(self, name)

        # First instance ? => All done
        self._conn = Connection.get_instance(instance_name="Shell")
        if self._conn.is_client():
            return

        # Add an accessor for dbus daemon
        self.register(self.SHELL_DAEMON, self.RPC(self._conn, self))

        # Create Qt application and the QDeclarative view
        QApplication.setGraphicsSystem("raster")
        self._app = QApplication(sys.argv)
        self._app.setApplicationName(name)

        # Add an accessor for windows
        self.register(self.SHELL_WINDOWS, [])

    @property
    def windows(self):
        """Get list of windows associated to shell"""
        return self.objects[self.SHELL_WINDOWS]

    def create_window(self, new=True, screen=None, target=None):
        """Create a window in screen"""
        desktop = self._app.desktop()
        wscreen = screen or desktop.primaryScreen()
        wscreen = desktop.screenCount() - 1 if screen == -1 else wscreen

        # create window and move to screen wscreen
        loopfilter = lambda x: x.screen(desktop) == wscreen
        wviews = [window for window in self.windows if loopfilter(window)]
        window = wviews[0] if len(wviews) > 0 else None

        # not found. create one
        if any((new, not window)):
            # create window
            factory = QWindowFactory.get_instance()
            window = factory.create(self, target)
            self.objects[self.SHELL_WINDOWS].append(window)
            # move to wscreen
            geometry = desktop.screenGeometry(wscreen)
            window.move(window.x() + geometry.x(), window.y() + geometry.y())
        return window

    def remove_window(self, window):
        """Remove window from active windows"""
        self.windows.remove(window)
        del window
        if len(self.windows) == 0:
            self._app.aboutToQuit.emit()
            self._app.quit()

    #pylint: disable-msg=W0613
    def run(self, args, opt):
        "Invoke application"
        # process options
        new, screen, target = opt['new'], int(opt['screen']), opt['target']
        if self._conn.is_client():
            iface = self._conn.get_interface(constants.__appname__)
            iface.create_window(new, screen, target, opt['profiles'])
            return 0
        window = self.create_window(new, screen, target)
        window.show(opt['profiles'])
        return self._app.exec_()
