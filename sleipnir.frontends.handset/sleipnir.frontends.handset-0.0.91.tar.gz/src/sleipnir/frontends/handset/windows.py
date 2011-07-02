#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
QWindow

Main Application Component Manager
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
import os

# QML required deps
from PySide.QtCore import Qt
from PySide.QtDeclarative import QDeclarativeView

__all__ = ['QWindowFactory']

# Project requirements
from sleipnir.shell.platform import Platform

# local submodule requirements


class WindowError(Exception):
    """Main Window exception"""


#pylint: disable-msg=W0232,E0602,R0903
class QViewStatus(enum):
    """View status indicators"""
    STORED, DELETED, INSERT, REMOVE = xrange(4)


#pylint: disable-msg=W0232,E0602,R0903
class QWindowOrientaion(enum):
    """Window orientation indicators"""
    LOCK_PORTRAIT, LOCK_LANDSCAPE, AUTO = xrange(128, 131)


#pylint: disable-msg=R0904
class QWindow(QDeclarativeView):
    """Main Window representation"""

    def __init__(self, presenter, platform=None, parent=None):
        QDeclarativeView.__init__(self, parent)
        self._platform = platform or Platform()
        self._presenter = presenter

    @property
    def platform(self):
        """Peek selected platform"""
        return self._platform

    def lookup(self, object_id):
        """Lookup for object_id window hierachy"""
        root_object = self.rootObject()
        if root_object is not None:
            return root_object.findChild(object_id)

    def set_orientation(self, value):
        """Set screen orientation"""
        if value not in QWindowOrientation:
            raise WindowError("unknown orientation value %d", value)
        self.setAttribute(value, True)


class QHandsetWindow(QWindow):
    """ A handset based declarative view"""

    def __init__(self, presenter=None, platform=None, parent=None):
        presenter = presenter or QFremabtlePresenter(self)
        QWindow.__init__(self, presenter, parent)

        # Omit Frames
        self.setAttribute(Qt.FramelessWindowHint)
        # Save some cycles
        self.setAttribure(Qt.WA_NoSystemBackground)
        # Make window traslucent
        self.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set graphics capabilities...
        fmt = QGLFormat.defaultFormat()
        fmt.setDirectRendering(True)
        fmt.setDoubleBuffer(True)
        fmt.setSampleBuffers(False)

        # ... and replace viewport
        glw = QGLWidget(fmt)
        glw.setAutoFillBackground(False)
        self.setViewport(glw)

        # Experimental Qt Mobility packages are installed in /opt
        for qtm in ('qtm11', 'qtm12'):
            path = os.path.join(os.sep, 'opt', qtm, 'imports')
            engine.addImportPath(path)


class QDesktopWindow(QWindow):
    """Generic Desktop view"""
    def __init__(self, presenter=None, platform=None, parent=None):
        presenter = presenter or QDesktopPresenter(self)
        QWindow.__init__(self, presenter, parent)
