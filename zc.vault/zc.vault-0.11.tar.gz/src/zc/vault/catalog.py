from BTrees import IOBTree, IFBTree
from zc.vault import interfaces, keyref
from zope import component, interface
import persistent
import zope.app.container.interfaces
import zope.app.intid.interfaces
import zope.component.interfaces
import zope.event
import zope.lifecycleevent
import zope.lifecycleevent.interfaces
import zope.location

# from a site, to get to the default package, the incantation is
# site.getSiteManager()['default']

def addLocalUtility(package, utility, interface=None,
                    name='', name_in_container='', comment=u''):
    chooser = zope.app.container.interfaces.INameChooser(package)
    name_in_container = chooser.chooseName(name_in_container, utility)
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(utility))
    package[name_in_container] = utility
    # really want IComponentRegistry, but that is not set up in Zope 3 ATM
    registry = zope.component.interfaces.IComponentLookup(package)
    registry.registerUtility(utility, interface, name, comment)

HISTORICAL = 'zc.vault.historical'
CURRENT = 'zc.vault.current'
WORKING = 'zc.vault.working'
# the following constant is not API
REVERSE = 'zc.vault.working_reverse'

class IRevisionReferences(interface.Interface):
    historical = interface.Attribute(
        '''an object with a standard mapping get method: stores
        object intid -> set of historical manifest intids''')
    current = interface.Attribute(
        '''an object with a standard mapping get method: stores
        object intid -> set of historical manifest intids''')
    working = interface.Attribute(
        '''an object with a standard mapping get method: stores
        object intid -> set of historical manifest intids''')

class RevisionReferencesMappings(persistent.Persistent):

    def __init__(self):
        self.references = IOBTree.IOBTree()

    def _getrefs(self, key):
        refs = self.references.get(key)
        if refs is None:
            refs = self.references[key] = IFBTree.IFTreeSet()
        return refs

    def add(self, key, value):
        self._getrefs(key).insert(value)

    def update(self, key, values):
        self._getrefs(key).update(values)

    def remove(self, key, value):
        refs = self.references.get(key)
        if refs is not None:
            refs.remove(value) # raises KeyError when we desire
            if not refs:
                del self.references[key]
        else:
            raise KeyError("key and value pair does not exist")

    def discard(self, key, value):
        try:
            self.remove(key, value)
        except KeyError:
            pass

    def contains(self, key, value):
        refs = self.references.get(key)
        if refs is not None:
            return value in refs
        return False

    def set(self, key, values):
        refs = self.references.get(key)
        vals = tuple(values)
        if not vals:
            if refs is not None:
                # del
                del self.references[key]
        else:
            if refs is None:
                refs = self.references[key] = IFBTree.IFTreeSet()
            else:
                refs.clear()
            refs.update(vals)

    def get(self, key):
        return self.references.get(key, ())

class RevisionReferences(persistent.Persistent, zope.location.Location):

    interface.implements(IRevisionReferences)

    __parent__ = __name__ = None

    def __init__(self):
        self.historical = RevisionReferencesMappings()
        self.current = RevisionReferencesMappings()
        self.working = RevisionReferencesMappings()
        self.reverse = RevisionReferencesMappings()

def createRevisionReferences(package):
    utility = RevisionReferences()
    chooser = zope.app.container.interfaces.INameChooser(package)
    name = chooser.chooseName('zc_vault_revision_references', utility)
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(utility))
    package[name] = utility
    # really want IComponentRegistry, but that is not set up in Zope 3 ATM
    registry = zope.component.interfaces.IComponentLookup(package)
    registry.registerUtility(utility, IRevisionReferences, '', '')

@component.adapter(interfaces.IManifestCommitted)
def makeReferences(ev):
    refs = component.getUtility(IRevisionReferences)
    intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
    man = ev.object
    man_id = intids.register(man)
    prev = man.previous
    if prev is not None:
        prev_id = intids.register(prev)
        for rel in prev:
            if rel.token is not man.vault.top_token:
                o_id = intids.register(rel.object)
                refs.current.discard(o_id, prev_id)
                refs.historical.add(o_id, prev_id)
    for o_id in refs.reverse.get(man_id):
        refs.working.remove(o_id, man_id)
    refs.reverse.set(man_id, ())
    for rel in man:
        if rel.token is not man.vault.top_token:
            refs.current.add(intids.register(rel.object), man_id)

@component.adapter(interfaces.IUpdateCompleted)
def updateCompleted(ev):
    refs = component.getUtility(IRevisionReferences)
    intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
    man = ev.object
    man_id = intids.register(man)
    for o_id in refs.reverse.get(man_id):
        refs.working.remove(o_id, man_id)
    refs.reverse.set(man_id, ())
    for rel in man.iterSelections():
        if rel.token is not man.vault.top_token:
            o_id = intids.register(rel.object)
            refs.working.add(o_id, man_id)
            refs.reverse.add(man_id, o_id)

@component.adapter(interfaces.IUpdateAborted)
def updateAborted(ev):
    updateCompleted(ev)

@component.adapter(
    interfaces.IManifest, zope.lifecycleevent.interfaces.IObjectCreatedEvent)
def manifestCreated(man, ev):
    refs = component.getUtility(IRevisionReferences)
    intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
    man = ev.object
    man_id = intids.register(man)
    for rel in man:
        if rel.token is not man.vault.top_token:
            o_id = intids.register(rel.object)
            refs.working.add(o_id, man_id)
            refs.reverse.add(man_id, o_id)

@component.adapter(interfaces.IRelationshipSelected)
def relationshipSelected(ev):
    rel = ev.object
    if rel.token is not rel.__parent__.vault.top_token:
        man = ev.manifest
        refs = component.getUtility(IRevisionReferences)
        intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
        man_id = intids.register(man)
        o_id = intids.register(rel.object)
        refs.working.add(o_id, man_id)
        refs.reverse.add(man_id, o_id)

@component.adapter(interfaces.IRelationshipDeselected)
def relationshipDeselected(ev):
    rel = ev.object
    if rel.token is not rel.__parent__.vault.top_token:
        man = ev.manifest
        for other in man:
            if other.object is rel.object:
                break
        else:
            refs = component.getUtility(IRevisionReferences)
            intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
            man_id = intids.register(man)
            o_id = intids.register(rel.object)
            refs.working.remove(o_id, man_id)
            refs.reverse.remove(man_id, o_id)

@component.adapter(interfaces.IObjectChanged)
def objectChanged(ev):
    rel = ev.object
    if rel.token is not rel.__parent__.vault.top_token:
        man = rel.__parent__
        if man is not None and man.isSelected(rel):
            refs = component.getUtility(IRevisionReferences)
            intids = component.getUtility(zope.app.intid.interfaces.IIntIds)
            man_id = intids.register(man)
            o_id = intids.register(rel.object)
            previous = ev.previous
            if previous is not None:
                for other in man:
                    if other.object is previous:
                        break
                else:
                    p_id = intids.register(previous)
                    refs.working.remove(p_id, man_id)
                    refs.reverse.remove(man_id, p_id)
            refs.working.add(o_id, man_id)
            refs.reverse.add(man_id, o_id)
