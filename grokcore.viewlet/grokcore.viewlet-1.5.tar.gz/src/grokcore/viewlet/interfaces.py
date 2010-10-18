##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Grok interfaces
"""
from zope import interface
from zope.viewlet.interfaces import IViewletManager as IViewletManagerBase

import grokcore.component.interfaces
import grokcore.security.interfaces
import grokcore.view.interfaces


class IBaseClasses(grokcore.component.interfaces.IBaseClasses,
                   grokcore.security.interfaces.IBaseClasses,
                   grokcore.view.interfaces.IBaseClasses):

    ViewletManager = interface.Attribute("Base class for viewletmanager.")
    Viewlet = interface.Attribute("Base class for viewlet.")


class IDirectives(grokcore.component.interfaces.IDirectives,
                  grokcore.security.interfaces.IDirectives,
                  grokcore.view.interfaces.IDirectives):

    def view(view):
        """Define on which view a viewlet manager/viewlet is registered.
        """

    def viewletmanager(manager):
        """Define on which viewlet manager a viewlet is registered.
        """

    def order(value=None):
        """Control the ordering of components.

        If the value is specified, the order will be determined by sorting on
        it.
        If no value is specified, the order will be determined by definition
        order within the module.
        If the directive is absent, the order will be determined by class name.
        (unfortunately our preferred default behavior on absence which would
        be like grok.order() without argument is hard to implement in Python)

        Inter-module order is by dotted name of the module the
        components are in; unless an explicit argument is specified to
        ``grok.order()``, components are grouped by module.

        The function grok.util.sort_components can be used to sort
        components according to these rules.
        """


class IGrokcoreViewletAPI(grokcore.component.interfaces.IGrokcoreComponentAPI,
                          grokcore.security.interfaces.IGrokcoreSecurityAPI,
                          grokcore.view.interfaces.IGrokcoreViewAPI,
                          IBaseClasses, IDirectives):
    pass


class IViewletManager(IViewletManagerBase):
    """The Grok viewlet manager.
    """
