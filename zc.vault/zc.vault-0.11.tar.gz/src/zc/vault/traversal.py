import zope.component
import zope.interface
import zope.interface.common.mapping
import zope.location
import zope.proxy
import zope.copypastemove.interfaces
import zope.app.container.interfaces
import zope.app.container.constraints

import zc.copy
import zc.freeze.interfaces
import zc.shortcut
import zc.shortcut.proxy
import zc.shortcut.interfaces

# interfaces

class IInventoryItemAware(zope.interface.Interface):
    _z_inventory_node = zope.interface.Attribute(
        """a zc.vault.interfaces.IContained (an IInventoryItem or an
        IInventoryContents.""")

class IInventoryItemAwareFactory(zope.interface.Interface):
    def __call__(item, parent, name):
        """returns an object that provudes IInventoryItemAware"""

class IProxy(
    IInventoryItemAware, zc.shortcut.interfaces.ITraversalProxy):
    """these proxies have _z_inventory_node, __traversed_parent__, and
    __traversed_name__"""

class IData(zope.interface.Interface):
    """A marker interface that indicates that this object should be adapted
    to IInventoryItemAwareFactory, and then the factory should be called with
    the object's item, its parent, and its name within the parent."""

# the proxy

class Proxy(zc.shortcut.proxy.ProxyBase):
    zc.shortcut.proxy.implements(IProxy)
    __slots__ = '_z_inventory_node',

    def __new__(self, ob, parent, name, item):
        return zc.shortcut.proxy.ProxyBase.__new__(self, ob, parent, name)

    def __init__(self, ob, parent, name, item):
        zc.shortcut.proxy.ProxyBase.__init__(self, ob, parent, name)
        self._z_inventory_node = item

# the containers

class ReadContainer(zope.location.Location):
    zope.interface.classProvides(IInventoryItemAwareFactory)
    zope.interface.implements(
        IInventoryItemAware, zope.interface.common.mapping.IEnumerableMapping)

    def __init__(self, item, parent=None, name=None):
        self.__parent__ = parent
        self.__name__ = name
        self._z_inventory_node = item

    def __len__(self):
        return len(self._z_inventory_node)

    def __iter__(self):
        return iter(self._z_inventory_node)

    def __contains__(self, key):
        return key in self._z_inventory_node

    def __getitem__(self, key):
        item = self._z_inventory_node(key)
        if item.object is None:
            factory = zope.component.getUtility(IInventoryItemAwareFactory)
            return factory(item, self, key)
        elif IData.providedBy(item.object):
            factory = IInventoryItemAwareFactory(item.object)
            return factory(item, self, key)
        else:
            return Proxy(item.object, self, key, item)

    def keys(self):
        return self._z_inventory_node.keys()

    def values(self):
        return [self[key] for key in self]

    def items(self):
        return [(key, self[key]) for key in self]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __getstate__(self):
        raise RuntimeError('This should not be persisted.')

class Container(ReadContainer):
    zope.interface.implements(zope.interface.common.mapping.IMapping)

    def __setitem__(self, key, value):
        self._z_inventory_node[key] = value

    def __delitem__(self, key):
        del self._z_inventory_node[key]

    def updateOrder(self, order):
        self._z_inventory_node.updateOrder(order)

# the movers and shakers

# Unfortunately we have to duplicate the standard checkObject so we can
# weed out the IContainer check, which is not pertinent here.
def checkObject(container, name, object):
    """Check containment constraints for an object and container
    """

    # check __setitem__ precondition
    containerProvided = zope.interface.providedBy(container)
    __setitem__ = containerProvided.get('__setitem__')
    if __setitem__ is not None:
        precondition = __setitem__.queryTaggedValue('precondition')
        if precondition is not None:
            precondition(container, name, object)

    # check the constraint on __parent__
    __parent__ = zope.interface.providedBy(object).get('__parent__')
    if __parent__ is not None:
        try:
            validate = __parent__.validate
        except AttributeError:
            pass
        else:
            validate(container)

def isInventoryObject(obj):
    return obj._z_inventory_node.object is zope.proxy.removeAllProxies(obj)

class ObjectMover(object):
    """can only move objects within and among manifests; moving elsewhere
    has reparenting connotations that are inappropriate, since inventory
    membership and parentage are unrelated."""
    zope.interface.implements(zope.copypastemove.interfaces.IObjectMover)
    zope.component.adapts(IInventoryItemAware)

    def __init__(self, context):
        self.context = context
        self.__parent__ = context

    def moveTo(self, target, new_name=None):
        if not IInventoryItemAware.providedBy(target):
            raise ValueError('target must be IInventoryItemAware')
        node = self.context._z_inventory_node
        if new_name is None:
            new_name = node.name
        if node == target._z_inventory_node and new_name == node.name:
            return # noop
        manifest = node.inventory.manifest
        if manifest._z_frozen:
            raise zc.freeze.interfaces.FrozenError(manifest)
        if target._z_inventory_node.inventory.manifest._z_frozen:
            raise zc.freeze.interfaces.FrozenError(
                target._z_inventory_node.inventory.manifest)
        checkObject(target, new_name, self.context)
        chooser = zope.app.container.interfaces.INameChooser(target)
        new_name = chooser.chooseName(new_name, node.object)
        node.moveTo(target._z_inventory_node, new_name)
        return new_name

    def moveable(self):
        manifest = self.context._z_inventory_node.inventory.manifest
        return not manifest._z_frozen

    def moveableTo(self, target, new_name=None):
        node = self.context._z_inventory_node
        manifest = node.inventory.manifest
        if (not manifest._z_frozen and
            IInventoryItemAware.providedBy(target) and
            not target._z_inventory_node.inventory.manifest._z_frozen):
            if new_name is None:
                new_name = node.name
            try:
                checkObject(target, new_name, self.context)
            except zope.interface.Invalid:
                pass
            else:
                return True
        return False

class ObjectCopier(object):
    """Generally, make new copies of objects.
    
    If target is from a non-versioned manifest, use
    copyTo and then copy all of the non-None data objects in the tree.

    otherwise if the object is a proxied leaf node, do a normal copy; otherwise
    puke (can't copy a vault-specific object out of a vault).
    """
    zope.interface.implements(zope.copypastemove.interfaces.IObjectCopier)
    zope.component.adapts(IInventoryItemAware)

    def __init__(self, context):
        self.context = context
        self.__parent__ = context

    def copyTo(self, target, new_name=None):
        if IInventoryItemAware.providedBy(target):
            if target._z_inventory_node.inventory.manifest._z_frozen:
                raise zc.freeze.interfaces.FrozenError(
                    target._z_inventory_node.inventory.manifest)
        else:
            if not isInventoryObject(self.context):
                raise ValueError # TODO better error
            return zope.copypastemove.interfaces.IObjectCopier(
                zc.shortcut.proxy.removeProxy(self.context)).copyTo(
                    target, new_name)
        node = self.context._z_inventory_node
        manifest = node.inventory.manifest
        if new_name is None:
            new_name = node.name
        checkObject(target, new_name, self.context)
        chooser = zope.app.container.interfaces.INameChooser(target)
        new_name = chooser.chooseName(new_name, node.object)
        node.copyTo(target._z_inventory_node, new_name)
        new_node = zope.proxy.removeAllProxies(
            target._z_inventory_node(new_name))
        stack = [(lambda x: new_node, iter(('',)))]
        while stack:
            node, i = stack[-1]
            try:
                key = i.next()
            except StopIteration:
                stack.pop()
            else:
                next = node(key)
                original = next.object
                next.object = zc.copy.copy(original)
                stack.append((next, iter(next)))
        return new_name

    def copyable(self):
        return True

    def copyableTo(self, target, new_name=None):
        if not self.copyable():
            return False
        if IInventoryItemAware.providedBy(target):
            if target._z_inventory_node.inventory.manifest._z_frozen:
                return False
            check = checkObject
        else:
            if not isInventoryObject(self.context):
                return False
            check = zope.app.container.constraints.checkObject
        node = self.context._z_inventory_node
        manifest = node.inventory.manifest
        if new_name is None:
            new_name = node.name
        try:
            check(target, new_name, self.context)
        except zope.interface.Invalid:
            return False
        else:
            return True

class ObjectLinker(object):
    zope.component.adapts(IInventoryItemAware)
    zope.interface.implements(zc.shortcut.interfaces.IObjectLinker)

    def __init__(self, context):
        self.context = context
        self.__parent__ = context

    def linkTo(self, target, new_name=None):
        if IInventoryItemAware.providedBy(target):
            if target._z_inventory_node.inventory.manifest._z_frozen:
                raise zc.freeze.interfaces.FrozenError(
                    target._z_inventory_node.inventory.manifest)
        else:
            if not isInventoryObject(self.context):
                raise ValueError # TODO better error
            return zc.shortcut.interfaces.IObjectLinker(
                zc.shortcut.proxy.removeProxy(self.context)).linkTo(
                    target, new_name)
        node = self.context._z_inventory_node
        manifest = node.inventory.manifest
        if new_name is None:
            new_name = node.name
        checkObject(target, new_name, self.context)
        chooser = zope.app.container.interfaces.INameChooser(target)
        new_name = chooser.chooseName(new_name, node.object)
        node.copyTo(target._z_inventory_node, new_name)
        return new_name

    def linkable(self):
        return True

    def linkableTo(self, target, new_name=None):
        if IInventoryItemAware.providedBy(target):
            if target._z_inventory_node.inventory.manifest._z_frozen:
                return False
            obj = self.context
            check = checkObject
        else:
            if not isInventoryObject(self.context):
                return False
            obj = self._createShortcut(
                zc.shortcut.proxy.removeProxy(self.context))
            check = zope.app.container.constraints.checkObject
        node = self.context._z_inventory_node
        manifest = node.inventory.manifest
        if new_name is None:
            new_name = node.name
        try:
            check(target, new_name, obj)
        except zope.interface.Invalid:
            return False
        else:
            return True

    def _createShortcut(self, target):
        return zc.shortcut.Shortcut(target)
