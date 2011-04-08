
import persistent # Not sure
from zope import interface, component, event
import zope.app.container.contained
import zope.lifecycleevent
import zope.proxy
import rwproperty
import zc.freeze.interfaces

from zc.vault import interfaces, core

def makeItem(rel, inventory):
    if rel.token == inventory.vault.top_token:
        return InventoryContents(inventory, relationship=rel)
    else:
        return InventoryItem(inventory, relationship=rel)

class InventoryContents(object):
    interface.implements(interfaces.IInventoryContents)

    def __init__(self, inventory, relationship=None):
        self.__parent__ = self.inventory = inventory
        if relationship is not None:
            if relationship.token != self.inventory.vault.top_token:
                raise ValueError('contents must use top_token')
            if not inventory.manifest.isOption(relationship):
                raise ValueError('relationship is not in manifest')
            self._relationship = relationship
        else:
            rel = inventory.manifest.get(self.inventory.vault.top_token)
            if rel is None:
                rel = core.Relationship(self.inventory.vault.top_token)
                rel.__parent__ = inventory.manifest
                event.notify(
                    zope.lifecycleevent.ObjectCreatedEvent(rel))
                inventory.manifest.addLocal(rel)
            self._relationship = rel

    def __getstate__(self):
        raise RuntimeError('This should not be persisted.') # negotiable

    def __eq__(self, other):
        return (interfaces.IInventoryContents.providedBy(other) and 
                self.relationship is other.relationship and
                self.inventory.manifest is other.inventory.manifest)

    def __ne__(self, other):
        return not (self == other)

    @property
    def relationship(self):
        return self._relationship

    def _getRelationshipFromKey(self, key, default=None):
        token = self.relationship.containment.get(key)
        if token is None:
            return default
        return self.inventory.manifest.get(token)

    def __len__(self):
        return len(self.relationship.containment)

    def __getitem__(self, key):
        rel = self._getRelationshipFromKey(key)
        if rel is None:
            raise KeyError(key)
        return rel.object

    def get(self, key, default=None):
        rel = self._getRelationshipFromKey(key)
        if rel is None:
            return default
        return rel.object

    def items(self):
        get = self.inventory.manifest.get
        return [(k, get(t).object) for k, t in
                self.relationship.containment.items()]

    def keys(self):
        return self.relationship.containment.keys()

    def values(self):
        get = self.inventory.manifest.get
        return [get(t).object for t in self.relationship.containment.values()]

    def __iter__(self):
        return iter(self.relationship.containment)

    def __contains__(self, key):
        return key in self.relationship.containment

    has_key = __contains__

    def getKey(self, item, default=None):
        if interfaces.IInventoryItem.providedBy(item):
            item = item.relationship
        return self.relationships.containment.getKey(item.token, default)

    def makeMutable(self):
        # local is mutable normally; modified is mutable while updating
        if self.inventory.manifest._z_frozen:
            raise zc.freeze.interfaces.FrozenError
        typ = self.type
        if not self.inventory.manifest.updating:
            if typ == interfaces.LOCAL:
                return typ
            elif self.has_local:
                raise ValueError('Local revision already created')
        elif typ == interfaces.MODIFIED:
            return typ
        selected = self.selected
        rel = core.Relationship(
            self.relationship.token, relationship=self.relationship,
            source_manifest=self.inventory.manifest)
        rel.__parent__ = self.inventory.manifest
        event.notify(zope.lifecycleevent.ObjectCreatedEvent(rel))
        if not self.inventory.manifest.updating:
            self.inventory.manifest.addLocal(rel)
            if selected:
                self.inventory.manifest.select(rel)
            res = interfaces.LOCAL
        else:
            self.inventory.manifest.addModified(rel)
            if selected:
                self.inventory.manifest.select(rel)
            res = interfaces.MODIFIED
        self._relationship = rel
        return res

    def __delitem__(self, key):
        self.makeMutable()
        old = self.relationship.containment[key]
        del self.relationship.containment[key]

    def __setitem__(self, key, value):
        relset = self.inventory.manifest
        token = self.relationship.containment.get(key)
        if token is None:
            self.makeMutable()
            sub_rel = core.Relationship()
            sub_rel.__parent__ = self.inventory.manifest
            sub_rel.token = self.inventory.vault.intids.register(sub_rel)
            event.notify(
                zope.lifecycleevent.ObjectCreatedEvent(sub_rel))
            sub_rel.object = value
            if self.inventory.updating:
                relset.addModified(sub_rel)
            else:
                relset.addLocal(sub_rel)
            self.relationship.containment[key] = sub_rel.token
        else:
            sub_rel = self.inventory.manifest.get(token)
            assert sub_rel is not None
            if relset.getType(sub_rel) not in (
                interfaces.LOCAL, interfaces.SUGGESTED, interfaces.MODIFIED):
                item = makeItem(sub_rel, self.inventory)
                item.makeMutable()
                sub_rel = item.relationship
            sub_rel.object = value

    def updateOrder(self, order):
        self.makeMutable()
        self.relationship.containment.updateOrder(order)

    def updateOrderFromTokens(self, order):
        self.makeMutable()
        c = self.relationship.containment
        c.updateOrder(c.getKey(t) for t in order)

    @property
    def token(self):
        return self.relationship.token

    def __call__(self, name, *args):
        if args:
            if len(args) > 1:
                raise TypeError(
                    '__call__() takes at most 2 arguments (%d given)' %
                    len(args) + 1)
            rel = self.relationship.containment.get(name)
            if rel is None:
                return args[0]
        else:
            rel = self.relationship.containment[name]
        return InventoryItem(self.inventory, rel)

    @property
    def previous(self):
        previous = self.inventory.manifest.previous
        if previous is None:
            return None
        previous_relationship = previous.get(self.relationship.token)
        if previous_relationship is None:
            return None
        return makeItem(previous_relationship, Inventory(previous))

    @property
    def next(self):
        next = self.inventory.manifest.next
        if next is None:
            return None
        next_relationship = next.get(self.relationship.token)
        if next_relationship is None:
            return None
        return makeItem(next_relationship, Inventory(next))

    @property
    def previous_version(self):
        rel = self.inventory.vault.getPrevious(self.relationship)
        if rel is not None:
            return makeItem(rel, Inventory(rel.__parent__))

    @property
    def next_version(self):
        rel = self.inventory.vault.getNext(self.relationship)
        if rel is not None:
            return makeItem(rel, Inventory(rel.__parent__))

    @property
    def type(self):
        return self.inventory.manifest.getType(self.relationship)

    @property
    def selected(self):
        return self.inventory.manifest.isSelected(self.relationship)

    def select(self):
        self.inventory.manifest.select(self.relationship)

    @property
    def is_update_conflict(self):
        return self.inventory.manifest.isUpdateConflict(
            self.relationship.token)

    def resolveUpdateConflict(self):
        if not self.inventory.manifest.updating:
            raise RuntimeError('can only resolve merges while updating')
        if not self.is_update_conflict:
            raise RuntimeError('Not a conflict')
        self.select() # XXX is this good behavior?
        self.inventory.manifest.resolveUpdateConflict(
            self.relationship.token)

    @property
    def has_base(self):
        return bool(self.inventory.manifest.getBase(
            self.relationship.token))

    @property
    def has_local(self):
        return bool(self.inventory.manifest.getLocal(
            self.relationship.token))

    @property
    def has_updated(self):
        return bool(self.inventory.manifest.getUpdated(
            self.relationship.token))

    @property
    def has_suggested(self):
        return bool(list(
            self.inventory.manifest.iterSuggested(
                self.relationship.token)))

    @property
    def has_modified(self):
        return bool(list(
            self.inventory.manifest.iterModified(
                self.relationship.token)))

    @property
    def has_merged(self):
        return bool(list(
            self.inventory.manifest.iterMerged(
                self.relationship.token)))

    @property
    def base_item(self):
        rel = self.inventory.manifest.getBase(
            self.relationship.token)
        if rel is not None:
            return makeItem(rel, self.inventory)

    @property
    def local_item(self):
        rel = self.inventory.manifest.getLocal(
            self.relationship.token)
        if rel is not None:
            return makeItem(rel, self.inventory)

    @property
    def updated_item(self):
        rel = self.inventory.manifest.getUpdated(
            self.relationship.token)
        if rel is not None:
            return makeItem(rel, self.inventory)

    def iterSuggestedItems(self):
        for rel in self.inventory.manifest.iterSuggested(
            self.relationship.token):
            yield makeItem(rel, self.inventory)

    def iterModifiedItems(self):
        for rel in self.inventory.manifest.iterModified(
            self.relationship.token):
            yield makeItem(rel, self.inventory)

    def iterMergedItems(self):
        for rel in self.inventory.manifest.iterMerged(
            self.relationship.token):
            yield makeItem(rel, self.inventory)

    @property
    def copy_source(self):
        if self.relationship.copy_source is not None:
            return makeItem(
                self.relationship.copy_source[0],
                Inventory(self.relationship.copy_source[1]))

    @property
    def selected_item(self):
        if self.selected:
            return self
        return makeItem(
            self.inventory.manifest.get(self.relationship.token),
            self.inventory)

class InventoryItem(InventoryContents):

    interface.implements(interfaces.IInventoryItem)

    def __init__(self, inventory, token=None, relationship=None):
        if token is inventory.vault.top_token:
            raise ValueError('Cannot create inventory item with top_token')
        self.__parent__ = self.inventory = inventory
        if relationship is None:
            if token is None:
                raise ValueError('must provide one of relationship or token')
            relationship = inventory.manifest.get(token)
            if relationship is None:
                raise ValueError('token is not used in this inventory')
        elif not inventory.manifest.isOption(relationship):
            raise ValueError('relationship is not in inventory')
        self._relationship = relationship

    def resolveOrphanConflict(self):
        self.inventory.manifest.resolveOrphanConflict(
            self.relationship.token)

    @property
    def is_orphan(self):
        return self.inventory.manifest.isOrphan(self.relationship.token)

    @property
    def is_orphan_conflict(self):
        return self.inventory.manifest.isOrphanConflict(
            self.relationship.token)

    @property
    def is_parent_conflict(self):
        return len(list(
            self.inventory.manifest.iterSelectedParents(
                self.relationship.token))) > 1

    @property
    def parent(self):
        res = self.inventory.manifest.getParent(self.relationship.token)
        if res is not None:
            return makeItem(res, self.inventory)

    @property
    def name(self):
        res = self.inventory.manifest.getParent(self.relationship.token)
        if res is not None:
            return res.containment.getKey(self.relationship.token)

    def iterSelectedParents(self):
        return (makeItem(rel, self.inventory) for rel in
                self.inventory.manifest.iterSelectedParents(
                    self.relationship.token))

    def iterParents(self):
        return (makeItem(rel, self.inventory) for rel in
                self.inventory.manifest.iterParents(
                    self.relationship.token))

    @property
    def object(self):
        return self.relationship.object
    @rwproperty.setproperty
    def object(self, value):
        self.relationship.object = value # may raise VersionedError

    def moveTo(self, location=None, name=None):
        clean_location = zope.proxy.removeAllProxies(location)
        if clean_location.inventory.manifest is not self.inventory.manifest:
            self.copyTo(location, name)
            if self.name:
                del self.parent[self.name]
            # go down & resolve all orphan conflicts: too much of a heuristic?
            stack = [(lambda x: self, iter(('',)))]
            while stack:
                s, i = stack[-1]
                try:
                    key = i.next()
                except StopIteration:
                    stack.pop()
                else:
                    val = s(key)
                    if val.is_orphan_conflict:
                        val.resolveOrphanConflict()
                    stack.append((val, iter(val)))
            return
        if location is None:
            location = self.parent
        if location is None:
            raise ValueError('location must be supplied for orphans')
        old_name = self.name
        if name is None:
            name = old_name
        if name is None:
            raise ValueError('Must specify name')
        if name in location:
            if zope.proxy.removeAllProxies(
                location(name).relationship) is self.relationship:
                return
            raise ValueError(
                'Object with same name already exists in new location')
        if (self.selected and location.selected and
            self.inventory.manifest.isLinked(
                self.relationship.token, location.relationship.token)):
            # location is in self
            raise ValueError('May not move item to within itself')
        parent = self.parent
        if old_name:
            del parent[old_name]
        if (parent is None or
            clean_location.relationship.token != parent.relationship.token):
            location.makeMutable()
        else:
            location = parent
        location.relationship.containment[name] = self.relationship.token
        if location.selected and not self.selected:
            self.select()

    def copyTo(self, location, name=None):
        if name is None:
            name = self.name
        if name in location:
            raise ValueError(
                'Object with same name already exists in new location')
        location.makeMutable()
        # to get around error-checking constraints in the core, we go from
        # bottom-to-top.
        # this also prevents the possibility of infinite recursion in the copy.
        stack = [
            (location.relationship, iter((name,)), lambda x: self, {})]
        if location.inventory.updating:
            add = location.inventory.manifest.addModified
        else:
            add = location.inventory.manifest.addLocal
        clean_location = zope.proxy.removeAllProxies(location)
        while stack:
            relationship, keys, src, queued = stack[-1]
            try:
                key = keys.next()
            except StopIteration:
                stack.pop()
                for k, v in queued.items():
                    relationship.containment[k] = v
                if (zope.proxy.removeAllProxies(relationship) is not
                    clean_location.relationship):
                    add(relationship)
            else:
                value = src(key)
                rel = core.Relationship(
                    relationship=value.relationship,
                    source_manifest=value.inventory.manifest)
                rel.__parent__ = clean_location.inventory.manifest
                rel.token = location.inventory.vault.intids.register(rel)
                event.notify(
                    zope.lifecycleevent.ObjectCreatedEvent(rel))
                queued[key] = rel.token
                stack.append((rel, iter(value), value, {}))

class Inventory(persistent.Persistent, zope.app.container.contained.Contained):

    interface.implements(interfaces.IInventory)

    def __init__(
        self, manifest=None, inventory=None, vault=None, mutable=False):
        if manifest is None:
            if vault is None:
                if inventory is None:
                    raise ValueError(
                        'must provide manifest, inventory, or vault')
                manifest = inventory.manifest
            else: # vault exists
                if inventory is None:
                    manifest = vault.manifest
                    if manifest is None:
                        manifest = core.Manifest(vault=vault)
                        event.notify(
                            zope.lifecycleevent.ObjectCreatedEvent(
                                manifest))
                else:
                    manifest = inventory.manifest
        elif inventory is not None:
            raise ValueError('cannot pass both manifest and inventory')
        if mutable and manifest._z_frozen:
            manifest = core.Manifest(manifest, vault)
            event.notify(
                zope.lifecycleevent.ObjectCreatedEvent(manifest))
        self._manifest = manifest
        self.__parent__ = manifest.vault

    def __eq__(self, other):
        return (interfaces.IInventory.providedBy(other) and
                self.manifest is other.manifest)

    def __ne__(self, other):
        return not (self == other)

    @property
    def vault(self):
        return self._manifest.vault
    @rwproperty.setproperty
    def vault(self, value):
        self._manifest.vault = value

    @property
    def contents(self):
        return InventoryContents(
            self, self.manifest.get(self.vault.top_token))

    @property
    def manifest(self):
        return self._manifest

    def iterUpdateConflicts(self):
        return (makeItem(r, self)
                for r in self.manifest.iterUpdateConflicts())

    def iterUpdateResolutions(self):
        return (makeItem(r, self)
                for r in self.manifest.iterUpdateResolutions())

    def iterOrphanConflicts(self):
        return (makeItem(r, self)
                for r in self.manifest.iterOrphanConflicts())

    def iterOrphanResolutions(self):
        return (makeItem(r, self)
                for r in self.manifest.iterOrphanResolutions())

    def iterUnchangedOrphans(self):
        return (makeItem(r, self)
                for r in self.manifest.iterUnchangedOrphans())

    def iterParentConflicts(self):
        return (makeItem(r, self)
                for r in self.manifest.iterParentConflicts())

    def __iter__(self): # selected items
        return (makeItem(r, self) for r in self.manifest)

    @property
    def updating(self):
        return self.manifest.updating

    @property
    def merged_sources(self):
        return tuple(Inventory(r) for r in self.manifest.merged_sources)

    @property
    def update_source(self):
        res = self.manifest.update_source
        if res is not None:
            return Inventory(res)

    def beginUpdate(self, source=None, previous=None):
        if interfaces.IInventory.providedBy(source):
            source = source.manifest
        if interfaces.IInventory.providedBy(previous):
            previous = previous.manifest
        self.manifest.beginUpdate(source, previous)

    def completeUpdate(self):
        self.manifest.completeUpdate()

    def abortUpdate(self):
        self.manifest.abortUpdate()

    def beginCollectionUpdate(self, items):
        self.manifest.beginCollectionUpdate(
            frozenset(i.relationship for i in items))

    def iterChangedItems(self, source=None):
        if interfaces.IInventory.providedBy(source):
            source = source.manifest
        return (makeItem(r, self)
                for r in self.manifest.iterChanges(source))

    def getItemFromToken(self, token, default=None):
        rel = self.manifest.get(token)
        if rel is None:
            return default
        return makeItem(rel, self)

    @property
    def previous(self):
        p = self.manifest.previous
        if p is not None:
            return Inventory(p)
        return None

    @property
    def next(self):
        p = self.manifest.next
        if p is not None:
            return Inventory(p)
        return None

class Vault(core.Vault):
    interface.implements(interfaces.IInventoryVault)

    def getInventory(self, ix):
        return Inventory(self[ix])

    @property
    def inventory(self):
        if self._data:
            return Inventory(self._data[self._data.maxKey()])
        return None

    def commit(self, value):
        if interfaces.IInventory.providedBy(value):
            value = value.manifest
        super(Vault, self).commit(value)

    def commitFrom(self, value):
        if interfaces.IInventory.providedBy(value):
            value = value.manifest
        super(Vault, self).commitFrom(value)
