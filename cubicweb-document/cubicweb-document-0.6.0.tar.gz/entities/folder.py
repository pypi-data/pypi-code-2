"""document specific class for Folder entities

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubes.folder.entities import Folder as BaseFolder


class Folder(BaseFolder):

    @property
    def repository(self):
        adapter = self.cw_adapt_to('ITree')
        return adapter.root().reverse_root_folder[0]

    @property
    def abspath(self):
        """omit the root folder, which is fake and whose purpose is to group (by
        filed_under) relation
        """
        itree = self.cw_adapt_to('ITree')
        parentfolders = list(itree.iterparents())
        parentfolders.insert(0, self)
        parentfolders.pop()
        return u'/'.join(foldr.name for foldr in reversed(parentfolders))

    def vcs_rm(self, rev=None, **kwargs):
        """recursively link DeletedVersionContent to its versioned_(sub)folders
        and versioned files
        """
        if rev is None:
            if not 'msg' in kwargs:
                kwargs['msg'] = self._cw._('deleted %s') % self.dc_title()
            rev = self.repository.make_revision(**kwargs)
        for child in self.reverse_filed_under:
            # children entity types could be folder or VersionedFile
            child.vcs_rm(rev, **kwargs)


def lookup_folder_by_path(executor, rootfoldereid, pathlist, create_missing=False):
    """
    looks up a folder matching a pathname list
    starting from a (root) folder eid
    optionally create a whole (sub)path, a la makedirs
    """
    if not pathlist:
        return

    class FolderFound(Exception): pass
    class FolderNotFound(Exception): pass

    def _lookup_folder(folderseid, pathlist):
        if not pathlist:
            raise FolderFound(folderseid[-1])
        parent = folderseid[-1]
        curpath = pathlist.pop()
        folder = executor('Folder X WHERE X name %(name)s, X filed_under PF, PF eid %(pfeid)s',
                          {'name': curpath, 'pfeid': parent})
        if not folder:
            if not create_missing:
                raise FolderNotFound('/'.join(list(reversed(pathlist))))
            folder = executor('INSERT Folder F: F name %(name)s', {'name' : curpath})
            foldereid = folder.rows[0][0]
            executor('SET F filed_under PF WHERE F eid %(feid)s, PF eid %(pfeid)s',
                     {'feid' : foldereid, 'pfeid' : parent})
        else:
            foldereid = folder.rows[0][0]
        folderseid.append(foldereid)
        _lookup_folder(folderseid, pathlist)

    try:
        _lookup_folder([rootfoldereid], filter(None, reversed(pathlist)))
    except FolderNotFound:
        return
    except FolderFound, ff:
        return ff.args[0]
