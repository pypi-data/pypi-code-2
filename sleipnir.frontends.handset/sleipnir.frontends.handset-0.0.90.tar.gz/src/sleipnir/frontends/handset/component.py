#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
QComponent

Main Application Component Manager
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules

# QML required deps
from PySide.QtCore import QObject, Slot
from PySide.QtDeclarative import QDeclarativeComponent, QDeclarativeContext

__all__ = ['ComponentFactory', 'QComponent']

# Project requirements

# local submodule requirements
from .view import ViewComponent


#pylint: disable-msg=R0904,W0223
class QViewComponent(QObject, ViewComponent):
    """Abstracft implementation targeted to PySide views"""

    abstract = True

    # pylint: disable-msg=C0103,W0232,R0903
    class __metaclass__(type(QObject), type(ViewComponent)):
        def __new__(cls, name, bases, dct):
            new_class = type(QObject).__new__(cls, name, bases, dct)
            if name not in ('Component', ) and 'abstract' not in dct:
                type(ViewComponent).__register_component__(new_class)
            return new_class

    def __init__(self):
        QObject.__init__(self)
        ViewComponent.__init__(self)

    def create(self, window, view=None, facade=None, share_ctx=False):
        connect = window in self._items
        item = ViewComponent.create(self, window, view, facade, share_ctx)
        if connect is True:
            item.close.connect(self.remove)
        return item

    @Slot(object)
    def remove(self, item):
        ViewComponent.remove(self, item)

    def _create_component(self, window, source=None):
        return QDeclarativeComponent(window.engine(), source)

    def _create_context(self, window, share_context):
        context = window.engine().rootContext()
        if share_context is False:
            context = QDeclarativeContext(context)
        return context


#pylint: disable-msg=E1101,E0102
class QViewPresenter(QObject):
    """Main QDashBoard Presenter"""

    #pylint: disable-msg=R0903
    class FacadeStub(object):
        """Simple stub for testing double purposes"""

    def __init__(self, window, facade=None):
        QObject.__init__(self)
        self._facade = facade
        self._window = window
        self._window.setProperty("presenter", self)

    @property
    def window(self):
        """Get window to be handle by this presenter"""
        return self._window

    @property
    def facade(self):
        """Set facade to be handle by this presenter"""
        self._facade = self._facade or self.FacadeStub()
        return self._facade

    @facade.setter
    def facade(self, value):
        """Set facade according to value"""
        self._facade = value
