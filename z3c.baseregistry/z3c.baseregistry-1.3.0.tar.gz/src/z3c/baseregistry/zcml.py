##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""ZCML Implementation to populate base registries.

$Id: zcml.py 118007 2010-10-28 13:39:39Z adamg $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.component.globalregistry
import zope.component.hooks
import zope.configuration.config
import zope.configuration.fields
from zope.configuration.exceptions import ConfigurationError


class IRegisterInDirective(zope.interface.Interface):
    """Use the specified registry for registering the contained components."""

    registry = zope.configuration.fields.GlobalObject(
        title=u"Registry",
        description=u"Python path to the registry to use.",
        required=True)


class ActionsProxy(object):
    """A proxy object for the actions list to decorate the incoming actions."""

    original = None
    registry = None

    def __init__(self, original, registry):
        self.original = original
        self.registry = registry

    def __decorate(self, item):
        discriminator = None
        if item[0] is not None:
            discriminator = (self.registry, item[0])
        return (discriminator,) + item[1:]

    def __setitem__(self, i, item):
        self.original.__setitem__(i, self.__decorate(item))

    def __setslice__(self, i, j, other):
        other = [self.__decorate(item) for item in other]
        self.original.__setslice__(i, j, other)

    def __iadd__(self, other):
        other = [self.__decorate(item) for item in other]
        self.original.__iadd__(other)

    def append(self, item):
        self.original.append(self.__decorate(item))

    def insert(self, i, item):
        self.original.insert(i, self.__decorate(item))

    def extend(self, other):
        other = [self.__decorate(item) for item in other]
        self.original.extend(other)

    def __getattr__(self, name):
        return getattr(self.original, name)


class FakeBaseRegistrySite(object):
    """This a minimal fake Site, the only responsibility it has
    is to store our registry as a SiteManager and return it later.
    This is needed to fool siteinfo via setSite, zope.component.zcml.handler
    will grab the registry via zope.component.getSiteManager() then."""

    def __init__(self, sm):
        self.sm = sm

    def getSiteManager(self):
        return self.sm

def setActiveRegistry(context, registry):
    context.original = zope.component.hooks.getSite()
    fakeSite = FakeBaseRegistrySite(registry)
    zope.component.hooks.setSite(fakeSite)

def resetOriginalRegistry(context):
    zope.component.hooks.setSite(context.original)


class RegisterIn(zope.configuration.config.GroupingContextDecorator):

    # Marker that this directive has been used in the path
    registryChanged=True

    # Storage for the original site
    original = None

    def __init__(self, context, registry, **kw):
        if hasattr(context, 'registryChanged') and context.registryChanged:
            raise ConfigurationError(
                'Nested ``registerIn`` directives are not permitted.')

        super(RegisterIn, self).__init__(context, **kw)
        self.registry = registry
        self.actions = ActionsProxy(context.actions, registry)

    def before(self):
        self.context.action(
            discriminator=None,
            callable=setActiveRegistry,
            args=(self, self.registry)
            )

    def after(self):
        self.context.action(
            discriminator=None,
            callable=resetOriginalRegistry,
            args=(self,)
            )
