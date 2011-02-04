##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"

from zope.traversing.api import getRoot
from zope.app.applicationcontrol.interfaces import IApplicationControl

from z3c.menu.ready2go import item


class ProcessMenuItem(item.GlobalMenuItem):
    """Process menu item."""

    weight = 10

    @property
    def available(self):
        """Only available IApplicationControl is available."""
        root = getRoot(self.context)
        appControl = IApplicationControl(root, None)
        if appControl is not None:
            return True
        else:
            return False

    def getURLContext(self):
        root = getRoot(self.context)
        return IApplicationControl(root)


class AppControlContextMenuItem(item.ContextMenuItem):
    """Base IApplicationControl context menu item."""

    def getURLContext(self):
        # make sure we use the app control as context
        root = getRoot(self.context)
        return IApplicationControl(root)


class RuntimeMenuItem(AppControlContextMenuItem):
    """Runtime menu item."""

    viewName = 'index.html'
    weight = 1


class ZODBControlMenuItem(AppControlContextMenuItem):
    """ZODB control menu item."""

    viewName = 'ZODBControl.html'
    weight = 2


class GenerationsMenuItem(AppControlContextMenuItem):
    """Generation management menu item."""

    viewName = 'generations.html'
    weight = 3
