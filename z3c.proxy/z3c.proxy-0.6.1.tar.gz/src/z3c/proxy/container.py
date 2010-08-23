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
"""
$Id: container.py 115867 2010-08-23 06:16:25Z icemac $
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.copypastemove import ObjectCopier
from zope.copypastemove import ObjectMover
from zope.copypastemove import ContainerItemRenamer
from zope.location import LocationProxy
from zope.proxy import getProxiedObject
from zope.proxy import non_overridable
from zope.proxy import isProxy

from zope.container.interfaces import IContainer
from z3c.proxy import interfaces


def proxify(container, item):
    if IContainer.providedBy(item):
        proxy = ContainerLocationProxy(item)
    else:
        proxy = LocationProxy(item)
    proxy.__name__ = item.__name__
    proxy.__parent__ = container
    return proxy


def _unproxy(obj):
    # precondition: treate only proxied objects
    if not isProxy(obj):
        return obj
    # essential
    return getProxiedObject(obj)


class ContainerLocationProxy(LocationProxy):
    """Proxy the location of a container an its items."""

    implements(interfaces.IContainerLocationProxy)

    # zope.app.conatiner.interfaces.IReadContainer
    @non_overridable
    def __getitem__(self, key):
        return proxify(self, getProxiedObject(self).__getitem__(key))

    @non_overridable
    def __contains__(self, key):
        return getProxiedObject(self).__contains__(key)

    @non_overridable
    def has_key(self, key):
        return getProxiedObject(self).has_key(key)

    @non_overridable
    def keys(self):
        return getProxiedObject(self).keys()

    @non_overridable
    def items(self):
        return [(key, proxify(self, item)) for key, item in getProxiedObject(self).items()]

    @non_overridable
    def get(self, key, default=None):
        item = getProxiedObject(self).get(key, default)

        if item is not default:
            return proxify(self, item)

        else:
            return default

    @non_overridable
    def __iter__(self):
        return iter(getProxiedObject(self))

    @non_overridable
    def values(self):
        return [proxify(self, value) for value in getProxiedObject(self).values()]

    @non_overridable
    def __len__(self):
        return getProxiedObject(self).__len__()

    # zope.app.conatiner.interfaces.IWriteContainer
    @non_overridable
    def __delitem__(self, key):
        getProxiedObject(self).__delitem__(key)

    @non_overridable
    def __setitem__(self, key, value):
        getProxiedObject(self).__setitem__(key, value)


class ProxyAwareObjectMover(ObjectMover):
    """Adapter for moving objects between containers that removes proxies."""
    def __init__(self, object):
        super(ProxyAwareObjectMover, self).__init__(_unproxy(object))


class ProxyAwareObjectCopier(ObjectCopier):
    """Adapter for copying objects between containers that removes proxies."""
    def __init__(self, object):
        super(ProxyAwareObjectCopier, self).__init__(_unproxy(object))


class ProxyAwareContainerItemRenamer(ContainerItemRenamer):
    """An IContainerItemRenamer adapter for containers."""
    def __init__(self, container):
        super(ProxyAwareContainerItemRenamer, self).__init__(
            _unproxy(container))

