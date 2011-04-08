from zope import interface
import zope.interface.common.mapping
import zope.interface.common.sequence
import zope.app.container.interfaces
import zope.component.interfaces

#### CONSTANTS ####

# see IManifest.getType for definitions
LOCAL = 'local'
BASE = 'base'
UPDATED = 'updated'
SUGGESTED = 'suggested'
MODIFIED = 'modified'
MERGED = 'merged'

#### EXCEPTIONS ####

class OutOfDateError(ValueError):
    """Manifest to be committed is not based on the currently committed version
    """

class NoChangesError(ValueError):
    """Manifest to be committed has no changes from the currently committed
    version"""

class ConflictError(ValueError):
    """Manifest to be committed has unresolved conflicts"""

#### EVENTS ####

class IMappingEvent(zope.component.interfaces.IObjectEvent): # abstract

    mapping = interface.Attribute(
        'the affected mapping; __parent__ is relationship')

    key = interface.Attribute('the key affected')

class IObjectRemoved(IMappingEvent):
    """Object was removed from mapping"""

class IObjectAdded(IMappingEvent):
    """Object was added to mapping"""

class IOrderChanged(zope.component.interfaces.IObjectEvent):
    """Object order changed; object is mapping"""

    old_keys = interface.Attribute('A tuple of the old key order')

class IManifestCommitted(zope.component.interfaces.IObjectEvent):
    """Object is manifest."""

class ILocalRelationshipAdded(zope.component.interfaces.IObjectEvent):
    """Relationship added to manifest as a local version.
    Relationship.__parent__ must be manifest."""

class IModifiedRelationshipAdded(zope.component.interfaces.IObjectEvent):
    """Relationship added to manifest as a modified version.
    Relationship.__parent__ must be manifest."""

class ISuggestedRelationshipAdded(zope.component.interfaces.IObjectEvent):
    """Relationship added to manifest as a suggested version.
    Relationship.__parent__ must be manifest."""

class IUpdateEvent(zope.component.interfaces.IObjectEvent):

    source = interface.Attribute(
        '''source manifest (from beginUpdate) or collection
        (from beginCollectionUpdate)''')

    base = interface.Attribute(
        '''the base manifest from which the update proceeds, or None.''')

class IUpdateBegun(IUpdateEvent):
    '''fired from beginUpdate or beginCollectionUpdate'''

class IUpdateCompleted(IUpdateEvent):
    ''

class IUpdateAborted(IUpdateEvent):
    ''

class IObjectChanged(zope.component.interfaces.IObjectEvent):
    previous = interface.Attribute('the previous object')

class IVaultChanged(zope.component.interfaces.IObjectEvent):
    previous = interface.Attribute('the previous vault')

class IRelationshipSelected(zope.component.interfaces.IObjectEvent):
    """relationship was selected"""
    manifest = interface.Attribute(
        'the manifest in which this relationship was selected')

class IRelationshipDeselected(zope.component.interfaces.IObjectEvent):
    """relationship was deselected"""
    manifest = interface.Attribute(
        'the manifest in which this relationship was deselected')

class ObjectRemoved(zope.component.interfaces.ObjectEvent):
    interface.implements(IObjectRemoved)
    def __init__(self, obj, mapping, key):
        super(ObjectRemoved, self).__init__(obj)
        self.mapping = mapping
        self.key = key

class ObjectAdded(zope.component.interfaces.ObjectEvent):
    interface.implements(IObjectAdded)
    def __init__(self, obj, mapping, key):
        super(ObjectAdded, self).__init__(obj)
        self.mapping = mapping
        self.key = key

class OrderChanged(zope.component.interfaces.ObjectEvent):
    interface.implements(IOrderChanged)
    def __init__(self, obj, old_keys):
        super(OrderChanged, self).__init__(obj)
        self.old_keys = old_keys

class ManifestCommitted(zope.component.interfaces.ObjectEvent):
    interface.implements(IManifestCommitted)

class LocalRelationshipAdded(zope.component.interfaces.ObjectEvent):
    interface.implements(ILocalRelationshipAdded)

class ModifiedRelationshipAdded(zope.component.interfaces.ObjectEvent):
    interface.implements(IModifiedRelationshipAdded)

class SuggestedRelationshipAdded(zope.component.interfaces.ObjectEvent):
    interface.implements(ISuggestedRelationshipAdded)

class AbstractUpdateEvent(zope.component.interfaces.ObjectEvent):
    def __init__(self, obj, source, base):
        super(AbstractUpdateEvent, self).__init__(obj)
        self.source = source
        self.base = base

class UpdateBegun(AbstractUpdateEvent):
    interface.implements(IUpdateBegun)

class UpdateCompleted(AbstractUpdateEvent):
    interface.implements(IUpdateCompleted)

class UpdateAborted(AbstractUpdateEvent):
    interface.implements(IUpdateAborted)

class VaultChanged(zope.component.interfaces.ObjectEvent):
    interface.implements(IVaultChanged)
    def __init__(self, obj, previous):
        super(VaultChanged, self).__init__(obj)
        self.previous = previous

class ObjectChanged(zope.component.interfaces.ObjectEvent):
    interface.implements(IObjectChanged)
    def __init__(self, obj, previous):
        super(ObjectChanged, self).__init__(obj)
        self.previous = previous

class RelationshipSelected(zope.component.interfaces.ObjectEvent):
    interface.implements(IRelationshipSelected)
    def __init__(self, obj, manifest):
        super(RelationshipSelected, self).__init__(obj)
        self.manifest = manifest

class RelationshipDeselected(zope.component.interfaces.ObjectEvent):
    interface.implements(IRelationshipDeselected)
    def __init__(self, obj, manifest):
        super(RelationshipDeselected, self).__init__(obj)
        self.manifest = manifest

#### EXCEPTIONS ####

class ParentConflictError(StandardError):
    """the item has more than one selected parent"""

class UpdateError(StandardError):
    """Update-related operation cannot proceed"""

#### BASIC INTERFACES ####

class IVersionFactory(interface.Interface):
    """looked up as a adapter of vault"""
    def __call__(object, manifest):
        """return the object to be stored"""

class IConflictResolver(interface.Interface):
    """looked up as a adapter of vault."""
    def __call__(manifest, local, update, base):
        """React to conflict between local and update as desired."""

class IUniqueReference(interface.Interface):

    identifiers = interface.Attribute(
        """An iterable of identifiers for this object.
        From most general to most specific.  Combination uniquely identifies
        the object.""")

    def __hash__():
        """return a hash of the full set of identifiers."""

    def __cmp__(other):
        """Compare against other objects that provide IUniqueReference,
        using the identifiers.""" # note that btrees do not support rich comps

class IToken(IUniqueReference):
    """An object used as a token for a manifest relationship"""

class IBidirectionalNameMapping(zope.interface.common.mapping.IMapping):
    """all keys are unicode, all values are adaptable to IKeyReference.

    all values must be unique (no two keys may have the same value).

    items, values, keys, and __iter__ returns in the specified order."""

    def getKey(value, default=None):
        """return key for value, or None"""

    def updateOrder(order):
        """Revise the order of keys, replacing the current ordering.

        order is an iterable containing the set of existing keys in the new
        order. `order` must contain ``len(keys())`` items and cannot contain
        duplicate keys.

        Raises ``TypeError`` if order is not iterable or any key is not
        hashable.

        Raises ``ValueError`` if order contains an invalid set of keys.
        """

class IRelationshipContainment(IBidirectionalNameMapping):
    """If __parent__.__parent__ (manifest) exists, must call
    manifest.approveRelationshipChange before making any changes, and should
    call manifest.reindex after all changes except order changes.
    """

    __parent__ = interface.Attribute(
        """The IRelationship of this containment before versioning (may be
        reused for other relationships after versioning).""")

class IRelationship(IUniqueReference):
    """The relationship for mapping a token to its contents and its object.
    Not mutable if can_modify is False."""

    token = interface.Attribute(
        """The token that this relationship maps""")

    __parent__ = interface.Attribute(
        """The manifest of this relationship before versioning (may be
        reused for other manifests after being versioned)""")

    object = interface.Attribute(
        """the object that the token represents for this relationship.
        if __parent__ exists (manifest), should call
        manifest.approveRelationshipChange before making any changes, and
        call manifest.reindex after change.""")

    containment = interface.Attribute(
        """The IRelationshipContainment, mapping names to contained tokens,
        for this relationship.""")

    children = interface.Attribute(
        """readonly: the containment.values().  modify with the containment."""
        )

class IContained(IBidirectionalNameMapping):
    """Abstract interface."""

    previous = interface.Attribute(
        """The IContained in the vault's previous inventory, or None if
        it has no previous version.  May be equal to (have the same
        relationship as) this IContained.""")

    next = interface.Attribute(
        """The IContained in the vault's next inventory, or None if
        it has no next version.  May be equal to (have the same
        relationship as) this IContained.""")

    previous_version = interface.Attribute(
        """The previous version of the IContained in the vault, or None if
        it has no previous version.  Will never be equal to (have the same
        relationship as) this IContained.""")

    next_version = interface.Attribute(
        """The next version of the IContained in the vault, or None if
        it has no next version.  Will never be equal to (have the same
        relationship as) this IContained.""")

    __parent__ = interface.Attribute(
        """the inventory to which this IContained belongs; same as inventory.
        """)

    inventory = interface.Attribute(
        """the inventory to which this IContained belongs; same as __parent__.
        """)

    relationship = interface.Attribute(
        """The relationship that models the containment and object information
        for the token.""")

    token = interface.Attribute(
        """The token assigned to this IContained's relationship.

        Synonym for .relationship.token""")

    def __call__(name):
        """return an IContained for the name, or raise Key Error"""

    def makeMutable():
        """convert this item to a mutable version if possible. XXX"""

    type = interface.Attribute(
        '''readonly; one of LOCAL, BASE, MERGED, UPDATED, SUGGESTED, MODIFIED.
        see IManifest.getType (below) for definitions.''')

    selected = interface.Attribute(
        '''readonly boolean; whether this item is selected.
        Only one item (relationship) may be selected at a time for a given
        token in a given inventory''')

    selected_item = interface.Attribute(
        '''the selected version of this item''')

    def select():
        '''select this item, deselecting any other items for the same token'''

    is_update_conflict = interface.Attribute(
        '''whether this is an unresolved update conflict''')

    def resolveUpdateConflict():
        '''select this item and mark the update conflict as resolved.'''

    has_base = interface.Attribute("whether item has a base version")

    has_local = interface.Attribute("whether item has a local version")

    has_updated = interface.Attribute("whether item has an updated version")

    has_suggested = interface.Attribute(
        "whether item has any suggested versions")

    has_modified = interface.Attribute(
        "whether item has any modified versions")

    has_merged = interface.Attribute(
        "whether item has any merged versions")

    base_item = interface.Attribute('''the base item, or None''')

    local_item = interface.Attribute('''the local item, or None''')

    updated_item = interface.Attribute('''the updated item, or None''')

    def iterSuggestedItems():
        """iterate over suggested items"""

    def iterModifiedItems():
        """iterate over modified items"""

    def iterMergedItems():
        """iterate over merged items"""

    def updateOrderFromTokens(order):
        """Revise the order of keys, replacing the current ordering.

        order is an iterable containing the set of tokens in the new order.
        `order` must contain ``len(keys())`` items and cannot contain duplicate
        values.

        XXX what exceptions does this raise?
        """

class IInventoryContents(IContained):
    """The top node of an inventory's hierarchy"""

class IInventoryItem(IContained):

    is_orphan = interface.Attribute(
        '''whether this item cannot be reached from the top of the inventory's
        hierarchy via selected relationships/items''')

    is_orphan_conflict = interface.Attribute(
        '''whether this is an orphan (see is_orphan) that is not BASE or
        MERGED and not resolved.''')

    def resolveOrphanConflict():
        '''resolve the orphan conflict so that it no longer stops committing
        or completing an update'''

    is_parent_conflict = interface.Attribute(
        '''whether this object has more than one selected parent''')

    parent = interface.Attribute(
        """The effective parent of the IContained.
        Always another IContained, or None (for an IInventoryContents).
        Will raise ParentConflictError if multiple selected parents.""")

    name = interface.Attribute(
        """The effective name of the IContained.
        Always another IContained, or None (for an IInventoryContents).
        Will raise ParentConflictError if multiple selected parents.""")

    def iterSelectedParents():
        '''iterate over all selected parents'''

    def iterParents():
        '''iterate over all parents'''

    object = interface.Attribute(
        """the object to which this IContained's token maps.  The
        vault_contents for the vault's top_token""")

    def copyTo(location, name=None):
        """make a clone of this node and below in location.  Does not copy
        actual object(s): just puts the same object(s) in an additional
        location.

        Location must be an IContained.  Copying to another inventory is
        currently undefined.
        """

    def moveTo(location=None, name=None):
        """move this object's tree to location.

        Location must be an IMutableContained from the same vault_contents.
        Not specifying location indicates the current location (merely a
        rename)."""

    copy_source = interface.Attribute(
        '''the item representing the relationship and inventory from which this
        item's relationship was created.''')

class IInventory(interface.Interface):
    """IMPORTANT: the top token in an IInventory (and IManifest) is always
    zc.vault.keyref.top_token."""

    manifest = interface.Attribute(
        """The IManifest used by this inventory""")

    def iterUpdateConflicts():
        '''iterate over the unresolved items that have update conflicts'''

    def iterUpdateResolutions():
        '''iterate over the resolved items that have update conflicts'''

    def iterOrphanConflicts():
        '''iterate over the current unresolved orphan conflicts'''

    def iterOrphanResolutions():
        '''iterate over the current resolved orphan conflicts'''

    def iterUnchangedOrphans():
        '''iterate over the orphans that do not cause conflicts--the ones that
        were not changed, so are either in the base or a merged inventory.'''

    def iterParentConflicts():
        '''iterate over the items that have multiple parents.
        The only way to resolve these is by deleting the item in one of the
        parents.'''

    def __iter__():
        '''iterates over all selected items, whether or not they are orphans.
        '''

    updating = interface.Attribute(
        '''readonly boolean: whether inventory is updating''')

    merged_sources = interface.Attribute(
        '''a tuple of the merged sources for this item.''')

    update_source = interface.Attribute(
        '''the source currently used for an update, or None if not updating''')

    def beginUpdate(inventory=None, previous=None):
        """begin update.  Fails if already updating.  if inventory is None,
        uses the current vault's most recent checkin.  if previous is None,
        calculates most recent shared base.
        """

    def completeUpdate():
        """complete update, moving update to merged.  Fails if any update,
        orphan, or parent conflicts."""

    def abortUpdate():
        """returns to state before update, discarding all changes made during
        the update."""

    def beginCollectionUpdate(items):
        """start an update based on just a collection of items"""

    def iterChangedItems(source=None):
        '''iterate over items that have changed from source.
        if source is None, use previous.'''

    def getItemFromToken(token, default=None):
        """get an item for the token in this inventory, or return default."""

    previous = interface.Attribute('the previous inventory in the vault')

    next = interface.Attribute('the next inventory in the vault')

class IVault(zope.app.container.interfaces.IContained,
             zope.interface.common.sequence.IFiniteSequence):
    """A read sequence of historical manifests.  The oldest is 0, and the
    most recent is -1."""

    manifest = interface.Attribute(
        """The most recent committed manifest (self[-1])""")

    def getPrevious(relationship):
        '''return the previous version of the relationship (based on token)
        or None'''

    def getNext(relationship):
        '''return the next version of the relationship (based on token)
        or None'''

    def commit(manifest):
        """XXX"""

    def commitFrom(manifest):
        """XXX"""

class IInventoryVault(IVault):
    """commit and commitFrom also take inventories"""

    inventory = interface.Attribute(
        """The most recent committed inventory (self.getInventory(-1))""")

    def getInventory(self, ix):
        """return IInventory for relationship set at index ix"""

class IManifest(interface.Interface):
    """IMPORTANT: the top token in an IManifest (and IInventory) is always
    zc.vault.keyref.top_token."""
    # should manifests know all of the manifests
    # they have generated (working copies)?  Maybe worth keeping track of?

    vault_index = interface.Attribute(
        'the index of the manifest in its vault')

    held = interface.Attribute(
        """Container of any related objects held because they were nowhere
        else.
        """)

    def getBaseSources():
        '''iterate over all bases (per vault)'''

    def getBaseSource(vault):
        '''get the base for the vault'''

    base_source = interface.Attribute('''the base of the set''')

    vault = interface.Attribute('the vault for this relationship set')

    vault_index = interface.Attribute('the index of this set in the vault')

    merged_sources = interface.Attribute(
        '''a tuple of the non-base merged sources, as found in getBase.''')

    update_source = interface.Attribute(
        '''the manifest used for the upate''')

    update_base = interface.Attribute(
        '''the manifest for the shared ancestor that the two manifests share'''
        )

    updating = interface.Attribute(
        '''boolean.  whether in middle of update.''')

    base_source = interface.Attribute(
        """the manifest used as a base for this one.""")

    def addLocal(relationship):
        '''add local copy except during update.  If no other relationship
        exists for the token, select it.  If no relationship already exists
        for the child tokens, disallow, raising ValueError.'''

    def addModified(relationship):
        '''add modified copies during update  If no other relationship
        exists for the token, select it.  If no relationship already exists
        for the child tokens, disallow, raising ValueError.'''

    def addSuggested(relationship):
        '''add suggested copies during update.  Another relationship must
        already exist in the manifest for the relationship's token.'''

    def checkRelationshipChange(relationship):
        """raise errors if the relationship may not be changed.
        UpdateError if the manifest is updating and the relationship is LOCAL;
        TypeError (XXX?) if the relationship is SUGGESTED or UPDATED"""

    def beginUpdate(source=None, base=None):
        '''begin an update.  Calculates update conflicts, tries to resolve.
        If source is None, uses vault's most recent manifest.  If base is None,
        uses the most recent shared base between this manifest and the source,
        if any.

        if already updating, raise UpdateError.

        update conflicts (different changes from the base both locally and in
        the source) are given to an interfaces.IConflictResolver, if an
        adapter to this interface is provided by the vault, to do with as it
        will (typically including making suggestions and resolving).'''

    def beginCollectionUpdate(source):
        '''cherry-pick update interface: CURRENTLY IN FLUX'''

    def completeUpdate():
        '''moves update source to bases; turns off updating; discards unused
        suggested, modified, and local relationships.

        Newer versions of the bases of the update source will replace the
        bases of this manifest. if a BASE or MERGED relationship (see getType
        for definitions) is selected and its source is no longer a part of the
        bases after the bases are replaced, a new (mutable) copy is created as
        a local relationship.'''

    def abortUpdate():
        '''return manifest to state before beginUpdate.'''

    def iterChanges(base=None):
        ''''iterate over all selected relationships that differ from the base.
        if base is not given, uses self.base_source'''

    def reindex(relationship):
        '''reindex the relationship after a change: used by relationships.'''

    def get(token, default=None):
        '''return the currently selected relationship for the token'''

    def getType(relationship):
        '''return type of relationship: one of BASE, LOCAL, UPDATED,
        SUGGESTED, MODIFIED, MERGED (see constants in this file, above).

        BASE relationships are those in the base_source (which is the manifest
        from the current vault on which this manifest was based).  There will
        only be zero or one BASE relationship for any given token in a
        manifest.

        LOCAL relationships are new relationships added (replacing or in
        addition to BASE) when not updating.  They may not be modified while
        the manifest is updating.  There will only be zero or one LOCAL
        relationship for any given token in a manifest.

        UPDATED relationships only are available in this manifest while
        updating, and are relationships changed from the BASE of the same
        token.  They may not be modified, even if they have not been versioned
        (e.g., added via `beginCollectionUpdate`). There will only be zero or
        one UPDATED relationship for any given token in a manifest.

        SUGGESTED relationships only exist while updating, and are intended to
        be relationships that an IConflictResolver created (although the
        resolvers have free reign).  They may not be modified, even if they
        have not been versioned.  There will be zero or more (unbounded)
        SUGGESTED relationships for any given token in a manifest. All
        MODIFIED relationships are discarded after an `abortUpdate`.

        MODIFIED relationships only exist while updating, and are the only
        relationships that may be modified while updating. There will be zero
        or more (unbounded) MODIFIED relationships for any given token in a
        manifest. Unselected MODIFIED relationships are discarded after an
        `completeUpdate`, and all MODIFIED relationships are discarded after
        an `abortUpdate`.

        MERGED relationships are those in the manifests returned by
        `getBaseSources` that are not the `base_source`: that is, typically
        those in manifests that have been merged into this one.  There will
        be zero or more MERGED relationships--no more than
        `len(self.getBaseSources()) -1`--in a manifest for a given token.

        '''

    def isSelected(relationship):
        '''bool whether relationship is selected'''

    def select(relationship):
        '''select the relationship for the given token.  There should always be
        one and only one selected relationship for any given token known about
        by the manifest.'''

    def getBase(token, default=None):
        '''Get the base relationship for the token, or default if None'''

    def getLocal(token, default=None):
        '''Get the local relationship for the token, or default if None'''

    def getUpdated(token, default=None):
        '''Get the updated relationship for the token, or default if None'''

    def iterSuggested(token):
        '''Iterate over suggested relationships for the token.'''

    def iterModified(token):
        '''Iterate over modified relationships for the token.'''

    def iterMerged(token):
        '''Iterate over merged relationships for the token.'''

    def iterSelectedParents(token):
        '''Iterate over selected parent for the token.  If there is more than
        one, it is a parent conflict; if there are none and the token is not
        the zc.vault.keyref.top_token, it is an orphan.'''

    def iterParents(token):
        '''iterate over all possible parents, selected and unselected, for the
        token'''

    def isLinked(token, child):
        '''returns boolean, whether child token is transitively linked
        beneath token using only selected relationships.'''

    def iterUpdateConflicts():
        '''iterate over unresolved update conflicts.'''

    def iterUpdateResolutions():
        '''iterate over resolved update conflicts.'''

    def isUpdateConflict(token):
        '''returns boolean, whether token is an unresolved update conflict.'''

    def resolveUpdateConflict(token):
        '''resolve the update conflict ("stop complaining, and use whatever is
        selected")'''

    def iterOrphanConflicts():
        '''iterate over unresolved orphan conflicts--selected relationships
        changed from the BASE and MERGED relationships.'''

    def iterOrphanResolutions():
        '''iterate over resolved orphan conflicts.'''

    def isOrphan(token):
        '''Whether token is an orphan.'''

    def isOrphanConflict(token):
        '''Whether token is an unresolved orphan token, as found in
        iterOrphanConflicts'''

    def resolveOrphanConflict(token):
        '''resolve the orphan conflict'''

    def undoOrphanConflictResolution(token):
        '''undo orphan conflict resolution'''

    def iterParentConflicts():
        '''iterate over all selected relationships that have more than
        one parent.'''

    def iterAll():
        '''iterate over all relationships known (of all types)'''

    def iterSelections():
        '''iterate over all selected relationships.'''

    def __iter__():
        '''iterate over linked, selected relationships: selected non-orphans.
        '''

    def iterUnchangedOrphans():
        '''iterate over BASE and MERGED orphans (that do not cause conflicts)
        '''

    next = interface.Attribute('the next manifest in the vault')

    previous = interface.Attribute(
        "the previous manifest in the vault, or from a branch's source")

    def isOption(relationship):
        """boolean, whether relationship is known (in iterAll)"""
