from Products.ZCatalog.Lazy import LazyMap


def getReferences(self, object, relationship=None, targetObject=None):
    """return a collection of reference objects"""
    sID, sobj = self._uidFor(object)
    if targetObject:
        tID, tobj = self._uidFor(targetObject)
        brains = self._queryFor(sID, tID, relationship)
    else:
        brains = self._optimizedQuery(sID, 'sourceUID', relationship)

    return self._resolveBrains(brains)


def getBackReferences(self, object, relationship=None, targetObject=None):
    """return a collection of reference objects"""
    # Back refs would be anything that target this object
    sID, sobj = self._uidFor(object)
    if targetObject:
        tID, tobj = self._uidFor(targetObject)
        brains = self._queryFor(tID, sID, relationship)
    else:
        brains = self._optimizedQuery(sID, 'targetUID', relationship)

    return self._resolveBrains(brains)


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
            if not rels.isdisjoint(relationship):
                result_rids.add(r)

    # Create brains
    return LazyMap(_catalog.__getitem__,
                   list(result_rids), len(result_rids))


def apply():
    from Products.Archetypes.ReferenceEngine import ReferenceCatalog as rc

    rc._old_getReferences = rc.getReferences
    rc.getReferences = getReferences
    rc._old_getBackReferences = rc.getBackReferences
    rc.getBackReferences = getBackReferences

    rc._optimizedQuery = _optimizedQuery
