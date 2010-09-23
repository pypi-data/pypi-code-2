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
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
import zope.i18nmessageid
import zope.i18n
from zope.security.interfaces import Unauthorized
from zope.security.interfaces import Forbidden
from zope.traversing import api
from zope.container.interfaces import IReadContainer

from z3c.jsontree import interfaces

_ = zope.i18nmessageid.MessageFactory('z3c')


class SubItemAware(object):
    """Base class for sub item lookup."""

    zope.interface.implements(interfaces.ISubItemAware)

    def getSubItems(self, item):
        """Delegate call to ITreeItems adapter."""
        adapter = zope.component.getMultiAdapter((item, self.request, self),
            interfaces.ITreeItems)
        return adapter.subItems


class TreeItemsMixin(object):
    """Base class for ITreeItems adapter."""

    zope.interface.implements(interfaces.ITreeItems)

    def __init__(self, context, request, tree):
        self.context = context
        self.request = request
        self.tree = tree


class NoneTreeItems(TreeItemsMixin):
    """Returns no items.
    
    Default tree item adapter for all objects.
    """

    @property
    def subItems(self):
        return []


class ContainerTreeItems(TreeItemsMixin):
    """Knows the items listed in tree for the given context.
    
    This is the default tree item adapter for IReadContainer.
    """

    maxItems = 50

    def _hasSubItems(self, item):
        """This method allows us to decide if a sub item has items from the 
        point of view of the context."""
        res = False
        if IReadContainer.providedBy(item):
            try:
                if len(item) > 0:
                    res = True
            except(Unauthorized, Forbidden):
                pass
        return res

    @property
    def subItems(self):
        """Collect all tree items for the given context."""
        items = []
        keys = []
        append = items.append
        if IReadContainer.providedBy(self.context):
            try:
                keys = list(self.context.keys())
            except(Unauthorized, Forbidden):
                return items
        else:
            return items
        counter = 1
        for name in keys:
            # Only include items we can traverse to
            subItem = api.traverse(self.context, name, None)
            if subItem is not None:
                append((api.getName(subItem), subItem,
                    self._hasSubItems(subItem)))
            counter += 1
            if counter == self.maxItems:
                # add context which should support a item listing view with 
                # batch
                lenght = len(keys) - self.maxItems
                default = '[%s more items...]' % lenght
                name = zope.i18n.translate(
                    _('[${lenght} more items...]', mapping={'lenght':lenght}),
                    context=self.request, default=default)
                append((name, self.context, False))
                break
        return items
