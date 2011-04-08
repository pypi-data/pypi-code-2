
from ZODB.interfaces import IConnection
from BTrees import IOBTree, OIBTree, OOBTree, IFBTree, Length
import persistent
from zope import interface, component, event
import zope.lifecycleevent
import zope.location
import zope.location.interfaces
import zope.app.container.contained
from zope.app.container.interfaces import INameChooser
import zope.app.intid
import zope.app.intid.interfaces
from zc.relationship import index
import zc.freeze
import zc.freeze.interfaces
import zope.app.keyreference.interfaces
import rwproperty

from zc.vault import interfaces, keyref

# vault -> relationships -> relationship -> mapping
#                        -> held

# XXX Missing relationships (child token without matching selected
# relationship) is handled but not very gracefully.  Especially a problem with
# beginCollectionUpdate.  Other situations are addressed in reindex.

class approvalmethod(object):

    def __init__(self, reindex=False):
        self.reindex = reindex

    def __call__(self, func):
        self.func = func
        return self.wrapper

    def wrapper(self, wself, *args, **kwargs):
        manifest = None
        rel = wself.__parent__
        if rel is not None:
            manifest = rel.__parent__
            if manifest is not None:
                if rel.token is None:
                    raise ValueError(
                        'cannot change containment without token on '
                        'relationship')
                manifest.checkRelationshipChange(rel)
        self.func(wself, *args, **kwargs)
        if self.reindex and manifest is not None:
            manifest.reindex(rel)

class Mapping(persistent.Persistent, zc.freeze.Freezing):

    interface.implements(interfaces.IRelationshipContainment)

    __parent__ = None

    def __init__(self, data=None):
        self._forward = OIBTree.OIBTree()
        self._reverse = IOBTree.IOBTree()
        self._length = Length.Length()
        self._order = ()
        if data is not None:
            self.update(data)

    def __len__(self):
        return self._length.value

    def __getitem__(self, key):
        return self._forward[key]

    def get(self, key, default=None):
        return self._forward.get(key, default)

    def items(self):
        return [(k, self._forward[k]) for k in self._order]

    def keys(self):
        return self._order

    def values(self):
        return [self._forward[k] for k in self._order]

    @property
    def valuesBTree(self): # for optimization
        return self._reverse

    @property
    def keysBTree(self): # for symmetry :-)
        return self._forward

    def __iter__(self):
        return iter(self._order)

    def __contains__(self, key):
        return key in self._forward

    has_key = __contains__

    def getKey(self, value, default=None):
        if not isinstance(value, int):
            return default
        return self._reverse.get(value, default)

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def __delitem__(self, key):
        self._delitem(key)

    def _delitem(self, key):
        old = self._forward.pop(key)
        order = list(self._order)
        order.remove(key)
        self._order = tuple(order)
        self._reverse.pop(old)
        self._length.change(-1)
        event.notify(interfaces.ObjectRemoved(old, self, key))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def __setitem__(self, key, value):
        self._setitem(key, value)

    def _setitem(self, key, value):
        bad = False
        if isinstance(key, basestring):
            try:
                unicode(key)
            except UnicodeError:
                bad = True
        else:
            bad = True
        if bad: 
            raise TypeError("'%s' is invalid, the key must be an "
                            "ascii or unicode string" % key)
        if len(key) == 0:
            raise ValueError("The key cannot be an empty string")
        if not isinstance(value, int):
            raise ValueError("The value must be an integer")
        old_key = self._reverse.get(value)
        if old_key is not None:
            if old_key != key:
                raise ValueError(
                    'name mapping can only contain unique values')
            # else noop
        else:
            old_value = self._forward.get(key)
            if old_value is None:
                self._order += (key,)
                self._length.change(1)
            else:
                old_old_key = self._reverse.pop(old_value)
                assert old_old_key == key
            self._forward[key] = value
            self._reverse[value] = key
            if old_value is not None:
                event.notify(interfaces.ObjectRemoved(old_value, self, key))
            event.notify(interfaces.ObjectAdded(value, self, key))

    @zc.freeze.method
    @approvalmethod(reindex=True)
    def update(self, data):
        if getattr(data, 'keys', None) is not None:
            data = [(k, data[k]) for k in data.keys()]
        if len(self):
            # since duplication of values is disallowed, we need to remove
            # any current overlapped values so we don't get spurious errors.
            keys = set()
            probs = []
            for k, v in data:
                keys.add(k)
                old_k = self._reverse.get(v)
                if old_k is not None and old_k != k:
                    probs.append((old_k, v))
            for k, v in probs:
                if k not in keys:
                    raise ValueError(
                        'name mapping can only contain unique values', v)
            for k, v in probs:
                self._delitem[k]
        for k, v in data:
            self._setitem(k, v)

    @zc.freeze.method
    @approvalmethod(reindex=False)
    def updateOrder(self, order):
        order = tuple(order)
        if self._order != order:
            if len(order) != len(self):
                raise ValueError('Incompatible key set.')
            for k in order:
                if k not in self._forward:
                    raise ValueError('Incompatible key set.')
            old_order = self._order
            self._order = order
            event.notify(interfaces.OrderChanged(self, old_order))

    def __eq__(self, other):
        return self is other or (
            (interfaces.IBidirectionalNameMapping.providedBy(other) and
             self.keys() == other.keys() and self.values() == other.values()))

    def __ne__(self, other):
        return not (self == other)

class Relationship(keyref.Token, zc.freeze.Freezing):
    interface.implements(interfaces.IRelationship)

    _token = _copy_source = None

    def __init__(self, token=None, object=None, containment=None,
                 relationship=None, source_manifest=None):
        if source_manifest is not None:
            if relationship is None:
                raise ValueError(
                    'source_inventory must be accompanied with relationship')
        if relationship is not None:
            if (source_manifest is None and
                relationship.__parent__ is not None):
                tmp = getattr(
                    relationship.__parent__, '__parent__', None)
                if interfaces.IManifest.providedBy(tmp):
                    source_manifest = tmp
            if source_manifest is not None:
                self._copy_source = (relationship, source_manifest)
            if object is not None or containment is not None:
                raise ValueError(
                    'cannot specify relationship with object or containment')
            object = relationship.object
            containment = relationship.containment
        if token is not None:
            if not isinstance(token, int):
                raise ValueError('token must be int')
            self._token = token
        self._object = object
        self._containment = Mapping(containment)
        self._containment.__parent__ = self

    @property
    def copy_source(self): # None or tuple of (relationship, inventory)
        return self._copy_source

    @zc.freeze.method
    def _z_freeze(self):
        if self.token is None:
            raise zc.freeze.interfaces.FreezingError(
                'Cannot version without a token')
        vault = self.__parent__.vault
        if not self.containment._z_frozen:
            prev = vault.getPrevious(self)
            if prev is not None:
                if prev.containment == self.containment:
                    assert prev.containment._z_frozen
                    self._containment = prev.containment
            if not self._containment._z_frozen:
                self.containment._z_freeze()
        if self._object is not None:
            obj_v = zc.freeze.interfaces.IFreezing(self.object)
            if not obj_v._z_frozen:
                factory = interfaces.IVersionFactory(vault, None)
                if factory is not None:
                    res = factory(self.object, self.__parent__)
                    if res is not self.object:
                        self.object = res
                        obj_v = zc.freeze.interfaces.IFreezing(res)
                if not obj_v._z_frozen:
                    obj_v._z_freeze()
        super(Relationship, self)._z_freeze()

    @property
    def token(self):
        return self._token
    @rwproperty.setproperty
    def token(self, value):
        if self._token is None:
            self._token = value
        elif not isinstance(value, int):
            raise ValueError('token must be int')
        else:
            self._token = value

    @property
    def object(self):
        return self._object
    @zc.freeze.setproperty
    def object(self, value):
        if self.token is None and self.__parent__ is not None:
            raise ValueError('cannot change object without token')
        if self.token == self.__parent__.vault.top_token:
            raise ValueError('cannot set object of top token')
        if (value is not None and
            not zc.freeze.interfaces.IFreezable.providedBy(value)):
            raise ValueError(
                'can only place freezable objects in vault, or None')
        if self.__parent__ is not None:
            self.__parent__.checkRelationshipChange(self)
        if value is not self._object:
            old = self._object
            self._object = value
            if (self.__parent__ is not None and
                self.__parent__.getType(self) is not None):
                self.__parent__.reindex(self)
                event.notify(interfaces.ObjectChanged(self, old))

    @property
    def containment(self):
        return self._containment

    @property
    def children(self):
        return self.containment.valuesBTree

def localDump(obj, index, cache):
    # NOTE: a reference to this function is persisted!
    return index.__parent__.vault.intids.register(obj)

def localLoad(token, index, cache):
    # NOTE: a reference to this function is persisted!
    return index.__parent__.vault.intids.getObject(token)

class Manifest(persistent.Persistent, zc.freeze.Freezing,
               zope.app.container.contained.Contained):

    interface.implements(interfaces.IManifest)

    _updateSource = _updateBase = None

    def __init__(self, base=None, vault=None):
        if vault is None:
            if base is None:
                raise ValueError('must provide base or vault')
            vault = base.vault
        elif base is not None:
            if base.vault is not vault and base.getBaseSource(vault) is None:
                raise ValueError(
                    "explicitly passed vault must have a base in base_source.")
        else: # vault but not base
            base = vault.manifest
        if base is not None and not base._z_frozen:
            raise ValueError('base must be versioned')
        self.__parent__ = self._vault = vault
        self._index = index.Index(
            ({'element':interfaces.IRelationship['token'],
              'dump': None, 'load': None, 'btree': IOBTree},
             interfaces.IRelationship['object'],
             {'element':interfaces.IRelationship['children'],
              'multiple': True, 'dump': None, 'load': None,
              'name': 'child', 'btree': IOBTree}),
            index.TransposingTransitiveQueriesFactory('token', 'child'),
            localDump, localLoad)
        self._index.__parent__ = self
        self._selections = IFBTree.IFTreeSet()
        self._oldSelections = IFBTree.IFTreeSet()
        self._conflicts = IFBTree.IFTreeSet()
        self._resolutions = IFBTree.IFTreeSet()
        self._orphanResolutions = IFBTree.IFTreeSet()
        self._oldOrphanResolutions = IFBTree.IFTreeSet()
        self._updated = IFBTree.IFTreeSet()
        self._local = IFBTree.IFTreeSet()
        self._suggested = IFBTree.IFTreeSet()
        self._modified = IFBTree.IFTreeSet()
        self._bases = IOBTree.IOBTree()
        if base:
            self._indexBases(base.getBaseSources(), base, True)
        if vault.held is None:
            self._held = HeldContainer()
            zope.location.locate(self._held, self, "held")
        else:
            self._held = vault.held

    @property
    def held(self):
        return self._held

    def _indexBases(self, bases, base=None, select=False):
        intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
        bases = dict((intids.register(b.vault), b) for b in bases)
        if base is not None:
            bid = intids.register(base.vault)
            bases[bid] = base
        else:
            bid = None
        assert not self._bases, (
            'programmer error: _indexBases should not be called with '
            'populated _bases')
        for iid, b in bases.items():
            select_this = select and iid==bid
            base_set = IFBTree.IFTreeSet()
            data = (base_set, b)
            register = self.vault.intids.register
            for rel in b:
                rid = register(rel)
                base_set.insert(rid)
                if select_this:
                    self._selections.insert(rid)
                    event.notify(interfaces.RelationshipSelected(rel, self))
                self._index.index_doc(rid, rel)
            self._bases[iid] = data

    zc.freeze.makeProperty('vault_index')

    def getBaseSources(self):
        return tuple(data[1] for data in self._bases.values())

    def getBaseSource(self, vault):
        intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
        iid = intids.queryId(vault)
        if iid is not None:
            data = self._bases.get(iid)
            if data is not None:
                return data[1]

    @property
    def base_source(self):
        return self.getBaseSource(self.vault)

    _vault = None
    @property
    def vault(self):
        return self._vault
    @zc.freeze.setproperty
    def vault(self, value):
        if self.updating:
            raise interfaces.UpdateError('Cannot change vault while updating')
        if value is not self._vault:
            old = self._vault
            s = set(old.intids.getObject(t) for t in self._selections)
            bases = tuple(self.getBaseSources())
            self._selections.clear()
            l = set(old.intids.getObject(t) for t in self._local)
            self._local.clear()
            self._index.clear()
            self._bases.clear()
            self._vault = value
            self._indexBases(bases)
            for r in l:
                self._add(r, self._local, True)
            self._selections.update(value.intids.register(r) for r in s)
            event.notify(interfaces.VaultChanged(self, old))

    @property
    def merged_sources(self):
        v = self.vault
        return tuple(b for b in self.getBaseSources() if b.vault is not v)

    @property
    def update_source(self):
        return self._updateSource

    @property
    def update_base(self):
        return self._updateBase

    @property
    def updating(self):
        return self._updateSource is not None

    @zc.freeze.method
    def _z_freeze(self):
        if self.updating:
            raise zc.freeze.interfaces.FreezingError(
                'cannot version during update')
        if (list(self.iterParentConflicts()) or
            list(self.iterOrphanConflicts())):
            raise zc.freeze.interfaces.FreezingError(
                'cannot version with conflicts')
        selections = set(self._iterLinked())
        b = base = self.base_source
        for r in list(self._local):
            if r not in selections:
                self._local.remove(r)
                self._index.unindex_doc(r)
            else:
                rel = self.vault.intids.getObject(r)
                if base is not None:
                    b = base.get(rel.token)
                if (b is None or
                    b.object is not rel.object or
                    b.containment != rel.containment):
                    if not rel._z_frozen:
                        rel._z_freeze()
                else:
                    selections.remove(r)
                    self._local.remove(r)
                    selections.add(self.vault.intids.getId(b))
                    self._index.unindex_doc(r)
        self._selections.clear()
        self._selections.update(selections)
        super(Manifest, self)._z_freeze()

    def _locateObject(self, relationship, force=False):
        if not force:
            for child in relationship.children:
                if self.get(child) is None:
                    raise ValueError(
                        'child tokens must have selected relationships')
        if relationship.token == self.vault.top_token:
            assert relationship.object is None
            return
        obj = relationship.object
        if obj is not None and getattr(obj, '__parent__', None) is None:
            if zope.location.interfaces.ILocation.providedBy(obj):
                dest = self.held
                dest[INameChooser(dest).chooseName('', obj)] = obj
            else:
                obj.__parent__ = self.vault

    def _add(self, relationship, set, force=False):
        self._locateObject(relationship, force)
        if relationship.__parent__ is not self:
            if relationship.__parent__ is None:
                relationship.__parent__ = self
            else:
                raise ValueError(
                    'cannot add relationship already in another set')
        iid = self.vault.intids.register(relationship)
        set.insert(iid)
        self._index.index_doc(iid, relationship)

    @zc.freeze.method
    def addLocal(self, relationship):
        if self.updating:
            raise interfaces.UpdateError(
                'cannot add local relationships during update')
        if self.getLocal(relationship.token) is not None:
            raise ValueError(
                'cannot add a second local relationship for the same token')
        self._add(relationship, self._local)
        event.notify(interfaces.LocalRelationshipAdded(relationship))
        if len(self._index.findRelationshipTokenSet(
            self._index.tokenizeQuery({'token': relationship.token}))) == 1:
            self.select(relationship)

    @zc.freeze.method
    def addModified(self, relationship):
        if not self.updating:
            raise interfaces.UpdateError(
                'can only add modified relationships during update')
        self._add(relationship, self._modified)
        event.notify(interfaces.ModifiedRelationshipAdded(relationship))
        if len(self._index.findRelationshipTokenSet(
            self._index.tokenizeQuery({'token': relationship.token}))) == 1:
            self.select(relationship)

    @zc.freeze.method
    def addSuggested(self, relationship):
        if not self.updating:
            raise interfaces.UpdateError(
                'can only add suggested relationships during update')
        if len(self._index.findRelationshipTokenSet(
               {'token': relationship.token})) == 0:
            raise ValueError('cannot add suggested relationship for new token')
        self._add(relationship, self._suggested)
        event.notify(interfaces.SuggestedRelationshipAdded(relationship))

    @zc.freeze.method
    def beginUpdate(self, source=None, base=None):
        if self.updating:
            raise interfaces.UpdateError(
                'cannot begin another update while updating')
        if source is None:
            source = self.vault.manifest
        if not interfaces.IManifest.providedBy(source):
            raise ValueError('source must be manifest')
        if source.vault.intids is not self.vault.intids:
            raise ValueError('source must share intids')
        if base is None:
            if self.base_source is None or source.vault != self.vault:
                myBase = self.getBaseSource(source.vault)
                otherBase = source.getBaseSource(self.vault)
                if myBase is None:
                    if otherBase is None:
                        # argh.  Need to walk over all bases and find any
                        # shared ones.  Then pick the most recent one.
                        for b in self.getBaseSources():
                            if b.vault == self.vault:
                                continue
                            o = source.getBaseSource(b.vault)
                            if o is not None:
                                # we found one!
                                if (o._z_freeze_timestamp >
                                    b._z_freeze_timestamp):
                                    b = o
                                if base is None or (
                                    b._z_freeze_timestamp >
                                    base._z_freeze_timestamp):
                                    base = b
                        if base is None:
                            raise ValueError('no shared previous manifest')
                    else:
                        base = otherBase
                elif (otherBase is None or
                      otherBase._z_freeze_timestamp <=
                      myBase._z_freeze_timestamp):
                    base = myBase
                else:
                    base = otherBase
            else:
                base = self.base_source

        if base is source:
            raise ValueError('base is source')
        elif base._z_freeze_timestamp > source._z_freeze_timestamp:
            raise NotImplementedError(
                "don't know how to merge to older source")
        if not interfaces.IManifest.providedBy(base):
            raise ValueError('base must be manifest')
        if not source._z_frozen or not base._z_frozen:
            raise ValueError('manifests must be versioned')
        intids = self.vault.intids
        self._oldSelections.update(self._selections)
        self._oldOrphanResolutions.update(self._orphanResolutions)
        self._updateSource = source
        self._updateBase = base
        to_be_resolved = []
        for s in source:
            b = base.get(s.token)
            source_changed = (b is None or s.object is not b.object or 
                              s.containment != b.containment)
            l = self.get(s.token)
            if l is None: # even if base is non-None, that change is elsewhere
                local_changed = False
            elif b is None:
                local_changed = True
            else:
                local_changed = l is not b and (
                    l.object is not b.object or l.containment != b.containment)
            if source_changed:
                iid = intids.register(s)
                self._updated.insert(iid)
                self._index.index_doc(iid, s)
                if local_changed:
                    self._conflicts.insert(s.token)
                    if l is not s and (l.object is not s.object or
                                       l.containment != s.containment):
                        # material difference.  Give resolver a chance.
                        to_be_resolved.append((l, s, b))
                    else:
                        # we'll use the merged version by default
                        self.select(s)
                        self._resolutions.insert(s.token)
                else:
                    self.select(s)
        if to_be_resolved:
            resolver = interfaces.IConflictResolver(self.vault, None)
            if resolver is not None:
                for l, s, b in to_be_resolved:
                    resolver(self, l, s, b)
        event.notify(interfaces.UpdateBegun(self, source, base))

    @zc.freeze.method
    def beginCollectionUpdate(self, source):
        if self.updating:
            raise interfaces.UpdateError(
                'cannot begin another update while updating')
        source = set(source)
        token_to_source = dict((r.token, r) for r in source)
        if len(token_to_source) < len(source):
            raise ValueError(
                'cannot provide more than one update relationship for the '
                'same source')
        for rel in source:
            if rel.__parent__.vault.intids is not self.vault.intids:
                raise ValueError('sources must share intids')
            for child in rel.children:
                if (token_to_source.get(child) is None and 
                    self.get(child) is None):
                    raise ValueError(
                        'cannot update from a set that includes children '
                        'tokens without matching relationships in which the '
                        'child is the token')
        intids = self.vault.intids
        self._oldSelections.update(self._selections)
        self._oldOrphanResolutions.update(self._orphanResolutions)
        tmp_source = set()
        for rel in source:
            if not rel._z_frozen:
                if rel.__parent__ is not None and rel.__parent__ is not self:
                    rel = Relationship(rel.token, relationship=rel)
                    rel.__parent__ = self
                    event.notify(
                        zope.lifecycleevent.ObjectCreatedEvent(rel))
                self._add(rel, self._updated, force=True)
            else:
                iid = intids.register(rel)
                self._updated.insert(iid)
                self._locateObject(rel, force=True)
                self._index.index_doc(iid, rel)
            tmp_source.add(rel)
            local = self.getLocal(rel.token)
            if local is not None:
                self._conflicts.insert(rel.token)
                if (local.object is rel.object and 
                      local.containment == rel.containment):
                    self._resolutions.insert(rel.token)
                else:
                    resolver = component.queryMultiAdapter(
                        (local, rel, None), interfaces.IConflictResolver)
                    if resolver is not None:
                        resolver(self)
            else:
                self.select(rel)
        self._updateSource = frozenset(tmp_source)
        assert not self._getChildErrors()
        event.notify(interfaces.UpdateBegun(self, source, None))

    def _selectionsFilter(self, relchain, query, index, cache):
        return relchain[-1] in self._selections

    def _iterLinked(self):
        for p in self._index.findRelationshipTokenChains(
            {'token': self.vault.top_token}, filter=self._selectionsFilter):
            yield p[-1]

    def completeUpdate(self):
        source = self._updateSource
        if source is None:
            raise interfaces.UpdateError('not updating')
        if (list(self.iterUpdateConflicts()) or
            list(self.iterParentConflicts()) or
            list(self.iterOrphanConflicts())):
            raise interfaces.UpdateError(
                'cannot complete update with conflicts')
        assert not self._getChildErrors(), 'children without relationships!'
        manifest = interfaces.IManifest.providedBy(source)
        # assemble the contents of what will be the new bases
        intids = self.vault.intids
        selected = set(self._iterLinked())
        base = self._updateBase
        self._updateSource = self._updateBase = None
        self._selections.clear()
        self._selections.update(selected)
        self._local.clear()
        self._index.clear()
        self._updated.clear()
        self._modified.clear()
        self._suggested.clear()
        self._conflicts.clear()
        self._resolutions.clear()
        self._orphanResolutions.clear()
        self._oldOrphanResolutions.clear()
        self._oldSelections.clear()
        bases = self.getBaseSources()
        self._bases.clear()
        if manifest:
            global_intids = component.getUtility(
                zope.app.intid.interfaces.IIntIds)
            bases = dict((global_intids.register(b.vault), b) for b in bases)
            for b in source.getBaseSources():
                iid = global_intids.register(b.vault)
                o = bases.get(iid)
                if o is None or o._z_freeze_timestamp < b._z_freeze_timestamp:
                    bases[iid] = b
            self._indexBases(bases.values(), source)
            existing = IFBTree.multiunion(
                [data[0] for data in self._bases.values()])
            for i in selected:
                orig = rel = intids.getObject(i)
                if rel._z_frozen:
                    create_local = False
                    source_rel = source.get(rel.token)
                    if source_rel is rel:
                        create_local = True
                    elif source_rel is not None:
                        base_rel = base.get(rel.token)
                        if (base_rel is None or
                            source_rel._z_freeze_timestamp >
                            base_rel._z_freeze_timestamp):
                            create_local = True
                    if create_local:
                        rel = Relationship(
                            rel.token, relationship=rel, source_manifest=self)
                        rel.__parent__ = self
                        event.notify(
                            zope.lifecycleevent.ObjectCreatedEvent(rel))
                    else:
                        continue
                self._add(rel, self._local, True)
                event.notify(interfaces.LocalRelationshipAdded(rel))
                if orig is not rel:
                    self._selections.remove(i)
                    self.select(rel)
        else:
            self._indexBases(bases)
            existing = IFBTree.multiunion(
                [data[0] for data in self._bases.values()])
            for i in selected:
                if i not in existing:
                    rel = intids.getObject(i)
                    if rel._z_frozen:
                        rel = Relationship(
                            rel.token, relationship=rel, source_manifest=self)
                        rel.__parent__ = self
                        event.notify(
                            zope.lifecycleevent.ObjectCreatedEvent(rel))
                    self._add(rel, self._local, True)
                    event.notify(interfaces.LocalRelationshipAdded(rel))
        assert not (list(self.iterUpdateConflicts()) or
                    list(self.iterParentConflicts()) or
                    list(self.iterOrphanConflicts()) or
                    self._getChildErrors())
        event.notify(interfaces.UpdateCompleted(self, source, base))

    def checkRelationshipChange(self, relationship):
        reltype = self.getType(relationship)
        if self.updating and reltype == interfaces.LOCAL:
            raise interfaces.UpdateError(
                'cannot change local relationships while updating')
        if reltype in (interfaces.SUGGESTED, interfaces.UPDATED):
            assert self.updating, (
                'internal state error: the system should not allow suggested '
                'or updated relationships when not updating')
            raise TypeError(
                'cannot change relationships when used as suggested or '
                'updated values')

    def abortUpdate(self):
        if self._updateSource is None:
            raise interfaces.UpdateError('not updating')
        source = self._updateSource
        base = self._updateBase
        self._updateSource = self._updateBase = None
        for s in (self._updated, self._modified, self._suggested):
            for t in s:
                self._index.unindex_doc(t)
            s.clear()
        self._conflicts.clear()
        self._resolutions.clear()
        self._orphanResolutions.clear()
        self._orphanResolutions.update(self._oldOrphanResolutions)
        self._oldOrphanResolutions.clear()
        self._selections.clear()
        self._selections.update(self._oldSelections)
        self._oldSelections.clear()
        event.notify(interfaces.UpdateAborted(self, source, base))

    def iterChanges(self, base=None):
        get = self.vault.intids.getObject
        if base is None:
            base = self.base_source
        for t in self._selections:
            rel = get(t)
            if base is None:
                yield rel
            else:
                b = base.get(rel.token)
                if (b is None or
                    b.object is not rel.object or
                    b.containment != rel.containment):
                    yield rel

    @zc.freeze.method
    def reindex(self, relationship):
        t = self.vault.intids.queryId(relationship)
        if t is not None and (t in self._local or t in self._suggested or
                              t in self._modified or t in self._updated):
            self._locateObject(relationship)
            self._index.index_doc(t, relationship)

    def _getFromSet(self, token, set, default):
        res = list(self._yieldFromSet(token, set))
        if not res:
            return default
        assert len(res) == 1, 'internal error: too many in the same category'
        return res[0]

    def _yieldFromSet(self, token, set):
        get = self.vault.intids.getObject
        for t in self._index.findRelationshipTokenSet({'token': token}):
            if t in set:
                yield get(t)

    def get(self, token, default=None):
        # return the selected relationship
        return self._getFromSet(token, self._selections, default)

    def getType(self, relationship):
        t = self.vault.intids.queryId(relationship)
        if t is not None:
            if t in self._local:
                return interfaces.LOCAL
            elif t in self._updated:
                return interfaces.UPDATED
            elif t in self._suggested:
                return interfaces.SUGGESTED
            elif t in self._modified:
                return interfaces.MODIFIED
            else:
                intids = component.getUtility(
                    zope.app.intid.interfaces.IIntIds)
                iid = intids.queryId(relationship.__parent__.vault)
                if iid is not None and iid in self._bases:
                    iiset, rel_set = self._bases[iid]
                    if t in iiset:
                        return interfaces.BASE
                    for bid, (iiset, rel_set) in self._bases.items():
                        if bid == iid:
                            continue
                        if t in iiset:
                            return interfaces.MERGED
        return None

    def isSelected(self, relationship):
        t = self.vault.intids.queryId(relationship)
        return t is not None and t in self._selections

    @zc.freeze.method
    def select(self, relationship):
        t = self.vault.intids.queryId(relationship)
        if t is None or self.getType(relationship) is None:
            raise ValueError('unknown relationship')
        if t in self._selections:
            return
        rel_tokens = self._index.findRelationshipTokenSet(
            self._index.tokenizeQuery({'token': relationship.token}))
        for rel_t in rel_tokens:
            if rel_t in self._selections:
                self._selections.remove(rel_t)
                event.notify(interfaces.RelationshipDeselected(
                    self.vault.intids.getObject(rel_t), self))
                break
        self._selections.insert(t)
        event.notify(interfaces.RelationshipSelected(relationship, self))

    def getBase(self, token, default=None):
        vault = self.base_source
        for iiset, rel_set in self._bases.values():
            if rel_set is vault:
                return self._getFromSet(token, iiset, default)

    def getLocal(self, token, default=None):
        return self._getFromSet(token, self._local, default)

    def getUpdated(self, token, default=None):
        return self._getFromSet(token, self._updated, default)

    def iterSuggested(self, token):
        return self._yieldFromSet(token, self._suggested)

    def iterModified(self, token):
        return self._yieldFromSet(token, self._modified)

    def iterMerged(self, token):
        vault = self.vault
        seen = set()
        for iiset, rel_set in self._bases.values():
            if rel_set is not vault:
                for r in self._yieldFromSet(token, iiset):
                    if r not in seen:
                        yield r
                        seen.add(r)

    def _parents(self, token):
        return self._index.findRelationshipTokenSet({'child': token})

    def iterSelectedParents(self, token):
        get = self.vault.intids.getObject
        for iid in self._parents(token):
            if iid in self._selections:
                yield get(iid)

    def iterParents(self, token):
        get = self.vault.intids.getObject
        return (get(iid) for iid in self._parents(token))

    def getParent(self, token):
        good = set()
        orphaned = set()
        unselected = set()
        orphaned_unselected = set()
        for iid in self._parents(token):
            is_orphaned = self.isOrphan(iid)
            if iid in self._selections:
                if is_orphaned:
                    orphaned.add(iid)
                else:
                    good.add(iid)
            else:
                if is_orphaned:
                    orphaned_unselected.add(iid)
                else:
                    unselected.add(iid)
        for s in (good, orphaned, unselected, orphaned_unselected):
            if s:
                if len(s) > 1:
                    raise interfaces.ParentConflictError
                return self.vault.intids.getObject(s.pop())

    def isLinked(self, token, child):
        return self._index.isLinked(
            self._index.tokenizeQuery({'token': token}),
            filter=self._selectionsFilter,
            targetQuery=self._index.tokenizeQuery({'child': child}))

    def iterUpdateConflicts(self):
        # any proposed (not accepted) relationship that has both update and
        # local for its token
        if self._updateSource is None:
            raise StopIteration
        get = self.vault.intids.getObject
        for t in self._conflicts:
            if t not in self._resolutions:
                rs = list(self._index.findRelationshipTokenSet({'token': t}))
                for r in rs:
                    if r in self._selections:
                        yield get(r)
                        break
                else:
                    assert 0, (
                        'programmer error: no selected relationship found for '
                        'conflicted token')

    def iterUpdateResolutions(self):
        if self._updateSource is None:
            raise StopIteration
        get = self.vault.intids.getObject
        for t in self._resolutions:
            assert t in self._conflicts
            rs = list(self._index.findRelationshipTokenSet({'token': t}))
            for r in rs:
                if r in self._selections:
                    yield get(r)
                    break
            else:
                assert 0, (
                    'programmer error: no selected relationship found for '
                    'resolved token')

    def isUpdateConflict(self, token):
        return (token in self._conflicts and
                token not in self._resolutions)

    @zc.freeze.method
    def resolveUpdateConflict(self, token):
        if not self.updating:
            raise interfaces.UpdateError(
                'can only resolve merge conflicts during update')
        if token not in self._conflicts:
            raise ValueError('token does not have merge conflict')
        self._resolutions.insert(token)

    def _iterOrphans(self, condition):
        get = self.vault.intids.getObject
        res = set(self._selections)
        res.difference_update(self._iterLinked())
        bases = IFBTree.multiunion([d[0] for d in self._bases.values()])
        res.difference_update(bases)
        for t in res:
            tids = self._index.findValueTokenSet(t, 'token')
            assert len(tids) == 1
            tid = iter(tids).next()
            if not condition(tid):
                continue
            yield get(t)

    def iterOrphanConflicts(self):
        return self._iterOrphans(lambda t: t not in self._orphanResolutions)

    def iterOrphanResolutions(self):
        return self._iterOrphans(lambda t: t in self._orphanResolutions)

    def isOrphan(self, token):
        return not (token == self.vault.top_token or
                    self.isLinked(self.vault.top_token, token))

    def isOrphanConflict(self, token):
        return (self.isOrphan(token) and
                self.getType(token) not in (interfaces.BASE, interfaces.MERGED)
                and token not in self._orphanResolutions)

    @zc.freeze.method
    def resolveOrphanConflict(self, token):
        self._orphanResolutions.insert(token)

    @zc.freeze.method
    def undoOrphanConflictResolution(self, token):
        self._orphanResolutions.remove(token)

    def iterParentConflicts(self):
        get = self.vault.intids.getObject
        seen = set()
        for r in self._iterLinked():
            if r in seen:
                continue
            seen.add(r)
            ts = self._index.findValueTokenSet(r, 'token')
            assert len(ts) == 1
            t = iter(ts).next()
            paths = list(self._index.findRelationshipTokenChains(
                {'child': t}, filter=self._selectionsFilter,
                targetQuery={'token': self.vault.top_token}))
            if len(paths) > 1:
                yield get(r)

    def _getChildErrors(self):
        parents = set()
        children = set()
        for rid in self._iterLinked():
            parents.update(self._index.findValueTokenSet(rid, 'token'))
            children.update(self._index.findValueTokenSet(rid, 'child'))
        children.difference_update(parents)
        return children # these are token ids

    def iterAll(self): # XXX __iter__?
        get = self.vault.intids.getObject
        seen = set()
        for s in (self._local, self._updated, self._suggested,
                  self._modified):
            for t in s:
                if t not in seen:
                    yield get(t)
                    seen.add(t)
        for iidset, rel_set in self._bases.values():
            for t in iidset:
                if t not in seen:
                    yield get(t)
                    seen.add(t)

    def iterSelections(self): # XXX __iter__?
        get = self.vault.intids.getObject
        return (get(t) for t in self._selections)
            

    def __iter__(self): # XXX iterLinked?
        get = self.vault.intids.getObject
        return (get(t) for t in self._iterLinked())

    def iterUnchangedOrphans(self):
        get = self.vault.intids.getObject
        res = set(self._selections)
        res.difference_update(self._iterLinked())
        bases = IFBTree.multiunion([d[0] for d in self._bases.values()])
        res.intersection_update(bases)
        return (get(t) for t in res)

    @property
    def previous(self):
        i = self.vault_index
        if i is not None and len(self.vault)-1 >= i and self.vault[i] is self:
            if i > 0:
                return self.vault[i-1]
            return None
        return self.base_source

    @property
    def next(self):
        i = self.vault_index
        if i is not None and len(self.vault) > i+1 and self.vault[i] is self:
            return self.vault[i+1]
        return None

    def isOption(self, relationship): # XXX __contains__?
        for rel in self._index.findRelationships(
            self._index.tokenizeQuery(
                {'token': relationship.token, 'object': relationship.object})):
            if rel is relationship:
                return True
        return False

class HeldContainer(zope.app.container.btree.BTreeContainer):
    pass

class Vault(persistent.Persistent, zope.app.container.contained.Contained):
    interface.implements(interfaces.IVault)
    def __init__(self, intids=None, held=None):
        self._data = IOBTree.IOBTree()
        if intids is None:
            intids = zope.app.intid.IntIds()
        self.intids = intids
        if intids.__parent__ is None:
            zope.location.locate(intids, self, 'intids')
        self._next = OOBTree.OOBTree()
        self.top_token = intids.register(keyref.top_token)
        self._held = held

    @property
    def held(self):
        return self._held

    def createBranch(self, ix=-1, held=None):
        # ...shugah, shugah...
        # uh, that means that this is sugar for the "make sure you share the
        # intids when you make a branch" issue.
        if not isinstance(ix, int):
            raise ValueError('ix must be int')
        if held is None:
            held = self.held
        res = self.__class__(self.intids, held)
        res.commit(Manifest(self[ix]))
        return res

    def getPrevious(self, relationship):
        manifest = relationship.__parent__ # first one with this relationship
        ix = manifest.vault_index
        if ix > 0:
            return manifest.vault[ix-1].get(relationship.token)
        return None

    def getNext(self, relationship):
        return self._next.get(self.intids.getId(relationship))

    def __len__(self):
        if self._data:
            return self._data.maxKey() + 1
        else:
            return 0

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, stride = key.indices(len(self))
            if stride==1:
                return self._data.values(start, stop, excludemax=True)
            else:
                pos = start
                res = []
                while pos < stop:
                    res.append(self._data[pos])
                    pos += stride
                return res
        elif key < 0:
            effective_key = len(self) + key
            if effective_key < 0:
                raise IndexError(key)
            return self._data[effective_key]
        elif key >= len(self):
            raise IndexError(key)
        else:
            return self._data[key]

    def __iter__(self):
        return iter(self._data.values())

    @property
    def manifest(self):
        if self._data:
            return self._data[self._data.maxKey()]
        return None

    def commit(self, manifest):
        if not interfaces.IManifest.providedBy(manifest):
            raise ValueError('may only commit an IManifest')
        current = self.manifest
        if current is not None:
            current_vaults = set(id(b.vault) for b in current.getBaseSources())
            current_vaults.add(id(current.vault))
            new_vaults = set(id(b.vault) for b in manifest.getBaseSources())
            new_vaults.add(id(manifest.vault))
            if not current_vaults & new_vaults:
                raise ValueError(
                    'may only commit a manifest with at least one shared base')
            elif manifest.getBaseSource(self) is not current and (
                not manifest.updating or (
                    manifest.updating and
                    manifest.update_source is not current)):
                raise interfaces.OutOfDateError(manifest)
        self._commit(manifest)

    def _commit(self, manifest):
        if manifest._z_frozen:
            raise zc.freeze.interfaces.FrozenError(manifest)
        if manifest.get(self.top_token) is None:
            raise ValueError(
                'cannot commit a manifest without a top_token relationship')
        if (self.manifest is not None and
            not len(tuple(manifest.iterChanges(self.manifest)))):
            raise interfaces.NoChangesError(manifest)
        if manifest.updating:
            manifest.completeUpdate()
        elif (list(manifest.iterUpdateConflicts()) or
              list(manifest.iterOrphanConflicts()) or
              list(manifest.iterParentConflicts())):
            raise interfaces.ConflictError(manifest)
        manifest.vault = self
        ix = len(self)
        self._data[ix] = manifest
        manifest.vault_index = ix
        manifest._z_freeze()
        for r in manifest:
            if manifest.getLocal(r.token) is r:
                p = self.getPrevious(r)
                if p is not None and p.__parent__.vault is self:
                    pid = self.intids.getId(p)
                    self._next[pid] = r
        if (manifest.__parent__ is None or
            manifest.__name__ is None):
            # so absoluteURL on objects in held "works" (needs traversers to
            # really work)
            zope.location.locate(manifest, self, unicode(manifest.vault_index))
        event.notify(interfaces.ManifestCommitted(manifest))

    def commitFrom(self, source):
        if not interfaces.IManifest.providedBy(source):
            raise ValueError('source must be manifest')
        if source.vault.intids is not self.intids:
            raise ValueError('source must share intids')
        if not source._z_frozen:
            raise ValueError('source must already be versioned')
        res = Manifest(self.manifest)
        base_rels = dict((r.token, r) for r in res.base_source)
        for rel in source:
            base_rel = base_rels.pop(rel.token, None)
            if base_rel is not None and base_rel == rel:
                res.select(rel)
            else:
                rel = Relationship(
                    rel.token, relationship=rel, source_manifest=res)
                rel.__parent__ = res
                event.notify(
                    zope.lifecycleevent.ObjectCreatedEvent(rel))
                res._add(rel, res._local, True)
                res.select(rel)
                event.notify(interfaces.LocalRelationshipAdded(rel))
        for rel in base_rels.values():
            res.select(rel) # to make sure that any hidden local changes are
            # ignored.  We don't need to resolve the orphans because base
            # orphans are not regarded as conflicts
        self._commit(res)
