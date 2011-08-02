from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.Lazy import LazyMap


def getReferences(self, object, relationship=None, targetObject=None,
                  objects=True):
    """return a collection of reference objects"""
    return self._optimizedReferences(object, relationship=relationship,
        targetObject=targetObject, objects=objects, attribute='sourceUID')


def getBackReferences(self, object, relationship=None, targetObject=None,
                      objects=True):
    """return a collection of reference objects"""
    # Back refs would be anything that target this object
    return self._optimizedReferences(object, relationship=relationship,
        targetObject=targetObject, objects=objects, attribute='targetUID')


def _optimizedReferences(self, object, relationship=None, targetObject=None,
                         objects=True, attribute='sourceUID'):
    sID, sobj = self._uidFor(object)
    if targetObject:
        tID, tobj = self._uidFor(targetObject)
        if attribute == 'sourceUID':
            brains = self._queryFor(sID, tID, relationship)
        else:
            brains = self._queryFor(tID, sID, relationship)
    else:
        brains = self._optimizedQuery(sID, attribute, relationship)

    if objects:
        return self._resolveBrains(brains)
    return brains


def _optimizedQuery(self, uid, indexname, relationship):
    """query reference catalog for object matching the info we are
    given, returns brains
    """
    if not uid: # pragma: no cover
        return []

    _catalog = self._catalog
    indexes = _catalog.indexes

    # First get one or multiple record ids for the source/target uid index
    rids = indexes[indexname]._index.get(uid, None)
    if rids is None:
        return []
    elif isinstance(rids, int):
        rids = [rids]
    else:
        rids = list(rids)

    # As a second step make sure we only get references of the right type
    # The unindex holds data of the type: [(-311870037, 'relatesTo')]
    # The index holds data like: [('relatesTo', -311870037)]
    if relationship is None:
        result_rids = rids
    else:
        rel_unindex_get = indexes['relationship']._unindex.get
        result_rids = set()
        if isinstance(relationship, str):
            relationship = set([relationship])
        for r in rids:
            rels = rel_unindex_get(r, set())
            if isinstance(rels, str):
                rels = set([rels])
            if len(rels.intersection(relationship)) > 0:
                result_rids.add(r)

    # Create brains
    return LazyMap(_catalog.__getitem__,
                   list(result_rids), len(result_rids))


def getSourceObject(self):
    return self._optimizedGetObject(self.sourceUID)


def getTargetObject(self):
    return self._optimizedGetObject(self.targetUID)


def _optimizedGetObject(self, uid):
    tool = getToolByName(self, 'uid_catalog', None)
    if tool is None: # pragma: no cover
        return ''
    tool = aq_inner(tool)
    traverse = aq_parent(tool).unrestrictedTraverse

    _catalog = tool._catalog
    rids = _catalog.indexes['UID']._index.get(uid, ())
    if isinstance(rids, int):
        rids = (rids, )

    for rid in rids:
        path = _catalog.paths[rid]
        obj = traverse(path, default=None)
        if obj is not None:
            return obj


def getRefs(self, relationship=None, targetObject=None):
    """get all the referenced objects for this object"""
    tool = getToolByName(self, 'reference_catalog')
    brains = tool.getReferences(self, relationship, targetObject=targetObject,
                                objects=False)
    if brains:
        return [_optimizedGetObject(self, b.targetUID) for b in brains]
    return []


def getBRefs(self, relationship=None, targetObject=None):
    """get all the back referenced objects for this object"""
    tool = getToolByName(self, 'reference_catalog')
    brains = tool.getBackReferences(self, relationship,
                                    targetObject=targetObject, objects=False)
    if brains:
        return [_optimizedGetObject(self, b.sourceUID) for b in brains]
    return []


def apply():
    from Products.Archetypes.ReferenceEngine import ReferenceCatalog as rc

    rc._old_getReferences = rc.getReferences
    rc.getReferences = getReferences
    rc._old_getBackReferences = rc.getBackReferences
    rc.getBackReferences = getBackReferences
    rc._optimizedReferences = _optimizedReferences
    rc._optimizedQuery = _optimizedQuery

    from Products.Archetypes.ReferenceEngine import Reference as rf

    rf._old_getTargetObject = rf.getTargetObject
    rf.getTargetObject = getTargetObject
    rf._old_getSourceObject = rf.getSourceObject
    rf.getSourceObject = getSourceObject
    rf._optimizedGetObject = _optimizedGetObject

    from Products.Archetypes.Referenceable import Referenceable as ra

    ra._old_getRefs = ra.getRefs
    ra.getRefs = getRefs
    ra.getReferences = getRefs
    ra._old_getBRefs = ra.getBRefs
    ra.getBRefs = getBRefs
    ra.getBackReferences = getBRefs
