#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
View

A set of helper to create and instantiate view items
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['ViewFactory', 'ViewComponent']

# Project dependences
from sleipnir.core.singleton import Singleton
from sleipnir.components.loaders import LoaderManager
from sleipnir.components.manager import ComponentManager
from sleipnir.components.components import Component, implements

# Subpackage dependences
from .interfaces.view import IView
from .constants import __views_dir__


#pylint: disable-msg=R0903
class Views(Singleton, ComponentManager):
    """
    A Helper to load and instantiate 'IView' components which
    implements required ifaces
    """

    def __init__(self):
        super(Views, self).__init__()
        python_loader = lambda x: x.__class__.__name__.startswith("Py")
        LoaderManager(self).load(__views_dir__, lfilter=python_loader)

    def get(self, item_type):
        """Get a view component instance that implements 'item_type'"""
        views = self.available(IView)
        item_type = item_type.lower()
        return self[views[0]] if len(views) == 1 else None


#pylint: disable-msg=R0921
class ViewComponent(Component):
    """Base class from which derive Component factories"""

    abstract = True
    implements(IView)

    class QViewInstance(object):
        """Internal representation of a View"""

        __slots__ = ('window', 'presenter',)

        def __init__(self, window):
            self.window = window
            self.presenter = None

    def __init__(self):
        self._items = {}

    def create(self, window, view=None, facade=None, share_ctx=False):
        """
        Get a valid item presenter for window or create one if a
        previous one not exists
        """
        # if exists return current view
        instance = self._items.setdefault(window, self.QViewInstance(window))
        if instance.presenter is not None:
            return instance.presenter

        # Creare required elements and return a valid view
        context = self._create_context(window, share_ctx)
        cmpnent = self._create_component(window)
        view = view or self._create_item(cmpnent, context)
        instance.presenter = self._create_presenter(view, facade)
        return instance.presenter

    def remove(self, item):
        """Make a view item private. Destroy register stuff"""
        for key, value in self._items.iteritems:
            if id(value.item) == item:
                del self._items[key]
            break

    #pylint: disable-msg=R0201
    def _create_item(self, component, context):
        """Create an item based on component and context"""
        return component.create(context)

    def _create_component(self, window, source=None):
        """Creates a item factory to instantiate"""
        raise NotImplementedError

    def _create_context(self, window, share_context):
        """Create a valid context for items"""
        raise NotImplementedError

    def _create_presenter(self, item, facade):
        """Create a valid presenter for this view"""
        raise NotImplementedError
