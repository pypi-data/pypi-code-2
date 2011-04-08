from zope import interface, component, schema
import zope.app.intid.interfaces
import zope.lifecycleevent.interfaces
import zope.location
import zc.objectlog.interfaces
from zc import objectlog
import zc.freeze.interfaces
from zc.vault.i18n import _
from zc.vault import interfaces

class IManifestChangeset(interface.Interface):
    update_source_intid = schema.Int(
        title=_('Update Source'),
        description=_('Will be None for collection update'),
        required=False)
    update_base_intid = schema.Int(
        title=_('Update Base'),
        description=_('Will be None for collection update'),
        required=False)
    vault_intid = schema.Int(
        title=_('Vault'),
        required=True)

class ManifestChangesetAdapter(object):
    interface.implements(IManifestChangeset)
    component.adapts(interfaces.IManifest)
    def __init__(self, man):
        intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
        self.vault_intid = intids.register(man.vault)
        self.update_source_intid = self.update_base_intid = None
        if interfaces.IManifest.providedBy(man.update_source):
            self.update_source_intid = intids.register(man.update_source)
            if interfaces.IManifest.providedBy(man.update_base):
                self.update_base_intid = intids.register(man.update_base)

class IRelationshipChangeset(interface.Interface):
    items = schema.Tuple(
        title=_('Items'), required=True)
    object_intid = schema.Int(title=_('Object'), required=False)

class RelationshipChangesetAdapter(object):
    interface.implements(IRelationshipChangeset)
    component.adapts(interfaces.IRelationship)
    def __init__(self, relationship):
        self.items = tuple((k, v) for k, v in relationship.containment.items())
        if relationship.object is None:
            self.object_intid = None
        else:
            intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
            self.object_intid = intids.register(relationship.object)

@component.adapter(
    interfaces.IManifest, zope.lifecycleevent.interfaces.IObjectCreatedEvent)
def createManifestLog(man, ev):
    if not zc.objectlog.interfaces.ILogging.providedBy(man):
        man.log = objectlog.Log(IManifestChangeset)
        zope.location.locate(man.log, man, 'log')
        interface.directlyProvides(man, zc.objectlog.interfaces.ILogging)
    man.log(_('Created'))

@component.adapter(
    interfaces.IRelationship,
    zope.lifecycleevent.interfaces.IObjectCreatedEvent)
def createRelationshipLog(rel, ev):
    if not zc.objectlog.interfaces.ILogging.providedBy(rel):
        rel.log = objectlog.Log(IRelationshipChangeset)
        zope.location.locate(rel.log, rel, 'log')
        interface.directlyProvides(rel, zc.objectlog.interfaces.ILogging)
    rel.log(_('Created'))
    rel.log(_('Created (end of transaction)'), defer=True, if_changed=True)

@component.adapter(interfaces.IObjectRemoved)
def logRemoval(ev):
    rel = ev.mapping.__parent__
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        rel.log(_('Child removed'))

@component.adapter(interfaces.IObjectAdded)
def logAddition(ev):
    rel = ev.mapping.__parent__
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        rel.log(_('Child added'))

@component.adapter(interfaces.IOrderChanged)
def logOrderChanged(ev):
    rel = ev.object.__parent__
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        rel.log(_('Child order changed'))

@component.adapter(interfaces.IManifestCommitted)
def logCommit(ev):
    man = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(man):
        man.log(_('Committed'))

@component.adapter(
    interfaces.IRelationship, zc.freeze.interfaces.IObjectFrozenEvent)
def logVersioning(rel, ev):
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        rel.log(_('Versioned'))

@component.adapter(interfaces.ILocalRelationshipAdded)
def logNewLocal(ev):
    rel = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        rel.log(_('Added as local relationship'))

@component.adapter(interfaces.IModifiedRelationshipAdded)
def logNewModified(ev):
    rel = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        rel.log(_('Added as modified relationship'))

@component.adapter(interfaces.ISuggestedRelationshipAdded)
def logNewSuggested(ev):
    rel = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        rel.log(_('Added as suggested relationship'))

@component.adapter(interfaces.IUpdateBegun)
def logUpdateBegun(ev):
    man = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(man):
        man.log(_('Update begun'))

@component.adapter(interfaces.IUpdateAborted)
def logUpdateAborted(ev):
    man = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(man):
        man.log(_('Update aborted'))

@component.adapter(interfaces.IUpdateCompleted)
def logUpdateCompleted(ev):
    man = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(man):
        man.log(_('Update completed'))

@component.adapter(interfaces.IVaultChanged)
def logVaultChanged(ev):
    man = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(man):
        man.log(_('Vault changed'))

# ADDITIONAL_SELECTION = _('Selected in additional manifest (${intid})')
@component.adapter(interfaces.IRelationshipSelected)
def logSelection(ev):
    rel = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        if ev.manifest is rel.__parent__:
            rel.log(_('Selected'))
        # else:
        #     intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
        #     msg = i18n.Message(ADDITIONAL_SELECTION,
        #                        mapping={'intid': intids.register(
        #                            ev.manifest)})
        #     rel.log(msg)

# ADDITIONAL_DESELECTION = _('Deselected from additional manifest (${intid})')
@component.adapter(interfaces.IRelationshipDeselected)
def logDeselection(ev):
    rel = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        if ev.manifest is rel.__parent__:
            rel.log(_('Deselected'))
        # else:
        #     intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
        #     msg = i18n.Message(ADDITIONAL_DESELECTION,
        #                        mapping={'intid': intids.register(
        #                            ev.manifest)})
        #     rel.log(msg)

@component.adapter(interfaces.IObjectChanged)
def logObjectChanged(ev):
    rel = ev.object
    if zc.objectlog.interfaces.ILogging.providedBy(rel):
        rel.log(_('Object changed'))
