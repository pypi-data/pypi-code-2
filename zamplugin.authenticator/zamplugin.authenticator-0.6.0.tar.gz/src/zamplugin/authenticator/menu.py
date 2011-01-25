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

from z3c.menu.ready2go import item



# IAddMenu
class AddUserContainerMenuItem(item.AddMenuItem):
    """Add user container menu item."""

    viewName = 'addUserContainer.html'
    weight = 1


class AddGroupContainerMenuItem(item.AddMenuItem):
    """Add user container menu item."""

    viewName = 'addGrouContainer.html'
    weight = 1


class AddGroupMenuItem(item.AddMenuItem):
    """Add user menu item."""

    viewName = 'addGroup.html'
    weight = 1


class AddUserMenuItem(item.AddMenuItem):
    """Add user menu item."""

    viewName = 'addUser.html'
    weight = 1


# IContextMenu
class ContentsMenuItem(item.ContextMenuItem):
    """Contents menu item."""

    viewName = 'contents.html'
    weight = 1


class EditMenuItem(item.ContextMenuItem):
    """Edit menu item."""

    viewName = 'edit.html'
    weight = 2
