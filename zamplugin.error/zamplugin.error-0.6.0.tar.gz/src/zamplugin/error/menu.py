##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import IContainmentRoot
from zope.error.interfaces import IErrorReportingUtility

from z3c.menu.ready2go import item
from zamplugin.error import interfaces


class ErrorsMenuItem(item.GlobalMenuItem):
    """Errors menu item."""

    viewName = 'index.html'
    viewInterface = interfaces.IErrorReportingUtilityPage
    weight = 2
    
    @property
    def available(self):
        util = zope.component.getUtility(IErrorReportingUtility)
        #TODO: this sucks here, but could not solve it differently
        return util.__parent__ is not None 

    def getURLContext(self):
        return zope.component.getUtility(IErrorReportingUtility)


class IndexMenuItem(item.ContextMenuItem):
    """Index menu item."""

    viewName = 'index.html'
    contextInterface = IErrorReportingUtility
    weight = 1


class EditMenuItem(item.ContextMenuItem):
    """Edit menu item."""

    viewName = 'edit.html'
    contextInterface = IErrorReportingUtility
    weight = 2
