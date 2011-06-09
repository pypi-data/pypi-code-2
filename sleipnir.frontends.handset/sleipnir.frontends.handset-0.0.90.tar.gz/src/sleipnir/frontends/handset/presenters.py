#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Presenters

Passive View pattern implementations
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
import os


# QML required deps
from PySide.QtCore import QObject, Slot
from PySide.QtDeclarative import QDeclarativeView

__all__ = ['QWindowFactory']

# Project requirements
from sleipnir.core.singleton import Singleton
from sleipnir.shell.platform import Platform

# local submodule requirements
from .windows import QDesktopWindow, QHandsetWindow
from .controller import QApplicationController
from .helpers import QProxy
from .constants import QML


#pylint: disable-msg=R0903
class QWindowFactory(Singleton):
    """
    A Application Window factory based on target platform

    Each application window is composed of a view, and a helper,
    approaching to TemplateView pattern from [PEAA03]
    """
    def __init__(self):
        self._backends = {
            "desktop":   (QDesktopWindow,   QDesktopPresenter,),
            "handset": (QHandsetWindow, QHandsetPresenter,),
        }

    def create(self, service, target):
        """Create a valid window for this platform"""
        platform = Platform(target)
        platform_name = platform.real.name
        if platform_name in self._backends:
            window, presenter = self._backends[platform_name]
            presenter = presenter(service)
            presenter.set_window(window(presenter, platform))
            return presenter
        raise AttributeError("'%s'not available" % platform_name.capitalize())


#pylint: disable-msg=R0904
class QWindowPresenter(QObject):
    """Base Controller for Sleipnir Window"""

    # pylint: disable-msg=W0142
    class QWindowController(QApplicationController):
        """Custom Application Controller for QWindowPresenter"""

        #pylint: disable-msg=W0232, R0903
        class QWindowStatus(QApplicationController.QApplicationStatus):
            """Custom valid application controller status"""
            CUSTOM = len(QApplicationController.QApplicationStatus)

        FLOW = []

        def __init__(self, profiles=None):
            QApplicationController.__init__(self, profiles)
            [self.register(*flow, profile=None) for flow in self.FLOW]

        def dispatch(self, event, state):
            state = self.QWindowStatus(state)
            return QApplicationController.dispatch(self, event, state)

        #pylint: disable-msg=W0221
        def register(self, event, state, *args, **kwrgs):
            state = self.QWindowStatus(state)
            QApplicationController.register(self, event, state, *args, **kwrgs)

    def __init__(self, service, window=None):
        super(QWindowPresenter, self).__init__()
        #  app controller stuff
        self._app_controller = None
        # service stuff
        self._service = service
        # window stuff
        self._window = None
        self._bridge = None
        self.set_window(window)

    def __getattr__(self, value):
        if self._window:
            return getattr(self._window, value)
        raise AttributeError(value)

    def __del__(self):
        self._window.close()

    def set_window(self, window):
        """Set window to be handle by this presenter"""
        assert not self._window
        if window is not None:
            self._window = window
            self._window.statusChanged.connect(self.ready)
            # Now load source
            self._window.setSource(self.source)

    @property
    def source(self):
        """Get url for qml resource file"""
        return QML("window", self._window.platform.name)

    @Slot(int)
    def ready(self, status=QDeclarativeView.Null):
        """connect bridge to presenter variant prop in root object"""
        if not self._bridge and status == QDeclarativeView.Ready:
            self._bridge = QProxy(self._window.rootObject())
            self._bridge.presenter = self

    @Slot()
    def quit(self):
        """Quit window"""
        self._service.remove_window(self)

    @Slot(object)
    def screen(self, desktop):
        """Get screen number for view"""
        return desktop.screenNumber(self._window)

    @Slot(str)
    def show(self, profiles):
        """Show view"""
        # check that app has been initiated.
        if not self._app_controller:

            # This line register all valid BaseProfiles into App controller
            ctrl = self._app_controller = self.QWindowController(profiles)
            action, view_component, move = ctrl.dispatch(None, "STARTING")
            assert self.status() == QDeclarativeView.Ready

            # create or get a previously created view
            presenter = view_component.create(self._window, facade=None)

            # invoke action:
            if callable(action):
                action(window, presenter, "STARTING")
            # FIXME: Signal or call directly
            # FIXME: Use a valid Facade
            if hasattr(self._bridge, "navigate_to"):
                self._bridge.navigate_to(presenter.window, move)

    @Slot()
    def switch(self):
        """Call to a task manager"""
        raise NotImplementedError


class QHandsetPresenter(QWindowPresenter):
    """A handset based helper"""

    DBUS_SWITCHER_EVENT = "/com/nokia/hildon_desktop " \
        "com.nokia.hildon_desktop.exit_app_view"

    @Slot()
    def switch(self):
        """Send a switch event or minimize"""
        os.system('dbus-send' + self.DBUS_EXIT_EVENT)

    def show(self, profiles):
        """Show view"""
        QWindowPresenter.show(self, profiles)
        self.showFullScreen()


class QDesktopPresenter(QWindowPresenter):
    """Desktop presenter"""

    @Slot()
    def switch(self):
        """Send a switch event or minimize"""
        self._window.showMinimized()

    def show(self, profiles):
        """Show view"""
        QWindowPresenter.show(self, profiles)
        self._window.show()
