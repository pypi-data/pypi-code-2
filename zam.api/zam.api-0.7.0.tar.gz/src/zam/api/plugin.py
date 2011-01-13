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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
from zope.security.proxy import removeSecurityProxy
from zope.schema.fieldproperty import FieldProperty

from zam.api import interfaces


class Plugin(object):
    """Plugin base."""

    zope.interface.implements(interfaces.IPlugin)

    title = FieldProperty(interfaces.IPlugin['title'])
    description = FieldProperty(interfaces.IPlugin['description'])

    def isInstalled(self, site):
        """See interfaces.IPlugin"""
        raise NotImplemented

    def install(self, site):
        """See interfaces.IPlugin"""
        raise NotImplemented

    def uninstall(self, site):
        """See interfaces.IPlugin"""
        raise NotImplemented


class BaseRegistryPlugin(Plugin):
    """Base registry plugin base."""

    zope.interface.implements(interfaces.IBaseRegistryPlugin)

    registry = FieldProperty(interfaces.IBaseRegistryPlugin['registry'])

    def isInstalled(self, site):
        """See interfaces.IPlugin"""
        sm = site.getSiteManager()
        if not zope.component.interfaces.IComponents.providedBy(sm):
            raise ValueError('Site does not provide ``IComponents``.',
                sm)
        # __bases__ is a private attribute and not declared in any interface
        # of ILocalSiteManager
        sm = removeSecurityProxy(sm)
        return self.registry in sm.__bases__

    def install(self, site):
        """See interfaces.IPlugin"""
        if self.isInstalled(site):
            return
        sm = site.getSiteManager()
        # new custom registry first
        # __bases__ is a private attribute and not declared in any interface
        sm = removeSecurityProxy(sm)
        sm.__bases__ = tuple([self.registry] + list(sm.__bases__))

    def uninstall(self, site):
        """See interfaces.IPlugin"""
        if not self.isInstalled(site):
            return
        sm = site.getSiteManager()
        # __bases__ is a private attribute and not declared in any interface
        sm = removeSecurityProxy(sm)
        bases = list(sm.__bases__)
        bases.remove(self.registry)
        sm.__bases__ = bases
