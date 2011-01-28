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

from zope.app.component.interfaces import ILocalSiteManager

from z3c.menu.ready2go import item


class GlobalSiteManagerMenuItem(item.GlobalMenuItem):
    """Site manager menu item."""

    viewName = '++etc++site'
    weight = 3


class RegistrationAddMenuItem(item.AddMenuItem):
    """The add registration menu item."""

    viewName = 'addRegistration.html'
    weight = 150


class RegistrationMenuItem(item.ContextMenuItem):
    """The registrations.html menu item."""

    viewName = 'registration.html'
    weight = 150

    @property
    def available(self):
        return not ILocalSiteManager.providedBy(self.context)


class RegistrationsMenuItem(item.ContextMenuItem):
    """ILocalSiteManager registrations.html menu item."""

    viewName = 'registrations.html'
    weight = 150


class SiteManagementFolderContentsMenuItem(item.ContextMenuItem):
    """ISiteManagementFolder contents.html menu item."""

    viewName = 'contents.html'
    weight = 1


class LocalSiteManagerContentsMenuItem(item.ContextMenuItem):
    """ILocalSiteManager contents.html menu item."""

    viewName = 'contents.html'
    weight = 1
