from logging import getLogger
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from BTrees.IIBTree import IISet, intersection, union
from BTrees.OOBTree import OOBTree
from BTrees.OIBTree import OIBTree

from Products.PluginIndexes.common.util import parseIndexRequest
from Products.PluginIndexes.common import safe_callable
from Products.PluginIndexes.PathIndex.PathIndex import PathIndex

from config import GLOBALS

_marker = []
LOG = getLogger('collective.arboreal.MultiPathIndex')

class MultiPathIndex(PathIndex):
    """ A path index stores multiple paths (/-separated strings) efficiently.
    
    The index then allows one to find objects with partial or whole paths

    """

    meta_type = "MultiPathIndex"
    manage_options= ({'label': 'Settings', 'action': 'manage_main'},)

    def __init__(self, id, extra=None, caller=None):
        """ MultiPathIndex supports indexed_attrs """
        PathIndex.__init__(self, id, caller)

        def get(o, k, default):
            if isinstance(o, dict):
                return o.get(k, default)
            else:
                return getattr(o, k, default)

        attrs = get(extra, 'indexed_attrs', (id,))
        if isinstance(attrs, str):
            attrs = attrs.split(',')
        attrs = filter(None, [a.strip() for a in attrs])

        self.indexed_attrs = tuple(attrs) or (id,)
        
    def _get_object_paths(self, obj, attr):
        try:
            paths = getattr(obj, attr, ())
        except AttributeError:
            return _marker
        if safe_callable(paths):
            paths = paths()
        if isinstance(paths, basestring):
            return (paths,)
        else:
            return paths

    def index_object(self, docid, obj, threshold=None):
        """ hook for (Z)Catalog """
        paths = set()
        indexed_fields = 0
        for attr in self.getIndexSourceNames():
            result = self._get_object_paths(obj, attr)
            if result is not _marker:
                paths.update(result)
                indexed_fields += 1
        if not indexed_fields:
            return 0
        paths = list(paths)

        for i, path in enumerate(paths):
            if isinstance(path, (list, tuple)):
                paths[i] = '/'.join(path)
        paths.sort()
        paths = tuple(paths)

        # Make sure we reindex only when paths change
        if self._unindex.has_key(docid):
            if self._unindex.get(docid) == paths:
                return 1
            self.unindex_object(docid)

        for path in paths:
            if not hasattr(path, 'split'):
                LOG.error(
                    'Error indexing path: %r at index: %s at object: %s',
                    path, self.getId(), '/'.join(obj.getPhysicalPath()))
                continue
            comps = filter(None, path.split('/'))
            for i, comp in enumerate(comps):
                self.insertEntry(comp, docid, i)

        self._unindex[docid] = paths
        self._length.change(1)
        return 1

    def unindex_object(self, docid):
        """ hook for (Z)Catalog """
        if not self._unindex.has_key(docid):
            LOG.debug(
                'Attempt to unindex nonexistent document with id %s', docid)
            return

        def unindex(comp, level, docid=docid):
            try:
                self._index[comp][level].remove(docid)
                if not self._index[comp][level]:
                    del self._index[comp][level]
                if not self._index[comp]:
                    del self._index[comp]
            except KeyError:
                LOG.debug(
                    'Attempt to unindex document with id %s failed', docid)

        paths = self._unindex[docid]
        for path in paths:
            # Do not attempt to unindex anything other than a string
            if not hasattr(path, 'split'):
                continue
            comps = filter(None, path.split('/'))
            for i, comp in enumerate(comps):
                unindex(comp, i)

        self._length.change(-1)
        del self._unindex[docid]

    def getIndexSourceNames(self):
        """ return names of indexed attributes """
        return getattr(self, 'indexed_attrs', [self.id])


    manage = manage_main = PathIndex.manage_main
    manage_main._setName('manage_main')
    

manage_addMultiPathIndexForm = PageTemplateFile('zmi/addMultiPathIndex.zpt', GLOBALS)

def manage_addMultiPathIndex(self, id, extra=None, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a multi-path index"""
    return self.manage_addIndex(id, 'MultiPathIndex', extra=extra,
                REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
