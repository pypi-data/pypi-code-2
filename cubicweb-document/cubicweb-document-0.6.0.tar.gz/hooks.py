"""this contains the server-side hooks triggered at entities/relation
creation/modification times

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from os.path import sep, basename

from cubicweb.selectors import is_instance
from cubicweb.server import hook

from cubes.document.entities.folder import lookup_folder_by_path

class AddRepository(hook.Hook):
    __regid__ = 'document.addrepository'
    __select__ = hook.Hook.__select__ & is_instance('Repository')
    events = ('after_add_entity',)

    def __call__(self):
        session = self._cw
        # make a root folder matching this repo and the subpath
        # important assumption : this is a root folder
        reponame = basename(self.entity.path)
        folderrset = session.execute('Folder F WHERE F name %(name)s',
                                     {'name' : reponame})
        if not folderrset:
            repofolder = session.create_entity('Folder', name=reponame)
        else:
            repofolder = folderrset.get_entity(0, 0)
        self.entity.set_relations(root_folder=repofolder)
        if self.entity.subpath:
            subpath = self.entity.subpath.split(sep)
            lastfolder = lookup_folder_by_path(session.execute, repofolder.eid,
                                               subpath, create_missing=True)
            assert lastfolder


class AfterAddVersionedFile(hook.Hook):
    """
    * set VersionedFile filed_under the right Folder automatically
      according to their path in the repository
    * may create a Folder hierarchy matching the correct path if it
      is not already there
    """
    __regid__ = 'document.addversionedfile'
    __select__ = hook.Hook.__select__ & is_instance('VersionedFile')
    events = ('after_add_entity', )

    def __call__(self):
        # folder hierarchy lookup/construction
        dirs = self.entity.directory.split(sep)
        try:
            querier_pending_relations = self.entity.cw_edited.querier_pending_relations
            repoeid = querier_pending_relations[('from_repository', 'subject')]
            repo = self._cw.entity_from_eid(repoeid)
        except KeyError:
            repo = self.entity.from_repository[0]
        foldereid = lookup_folder_by_path(self._cw.execute,
                                          repo.root_folder[0].eid,
                                          self.entity.directory.split(sep),
                                          create_missing=True)
        self._cw.execute('SET X filed_under F WHERE X eid %(x)s, F eid %(f)s',
                         {'x': self.entity.eid, 'f': foldereid})


class AfterNewRevision(hook.Hook):
    __regid__ = 'document.addrevision'
    __select__ = hook.Hook.__select__ & hook.match_rtype('content_for')
    events = ('after_add_relation',)

    def __call__(self):
        """on upload of a new revision, this probably needs to be cleaned up
        XXX (syt) really?
        """
        self._cw.execute('DELETE U might_edit VF WHERE VF eid %(eid)s',
                         {'eid' : self.eidto})


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    # disable the vcsfile.ClassifyVersionedFileHook hook
    from cubes.vcsfile.hooks import ClassifyVersionedFileHook
    vreg.unregister(ClassifyVersionedFileHook)
