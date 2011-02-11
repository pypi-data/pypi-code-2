import os.path as osp

from logilab.common.decorators import classproperty

from cubicweb.devtools.testlib import CubicWebTC

from cubes.vcsfile import bridge

def init_vcsrepo(repo, commitevery=1):
    bridge._REPOHDLRS.clear()
    try:
        session = repo.internal_session()
        bridge.import_content(session, commitevery=commitevery)
    finally:
        session.close()

class VCSRepositoryTC(CubicWebTC):
    """base class for test which should import a repository during setup"""
    _repo_path = None
    repo_type = u'mercurial'
    repo_encoding = u'utf-8'
    repo_subpath = None
    repo_import_revision_content = True
    repo_title = None

    commitevery = 3

    @classproperty
    def repo_path(cls):
        assert cls._repo_path, 'you must set repository through _repo_path first'
        return osp.join(cls.datadir, cls._repo_path)

    def _create_repo(self):
        return self.request().create_entity(
            'Repository', type=self.repo_type, path=self.repo_path,
            subpath=self.repo_subpath, encoding=self.repo_encoding,
            title=self.repo_title,
            import_revision_content=self.repo_import_revision_content)

    def setUp(self, init_cw=True):
        bridge._REPOHDLRS.clear()
        if init_cw:
            CubicWebTC.setUp(self)
        self.vcsrepo = self._create_repo()
        self.repoeid = self.vcsrepo.eid
        self.commit()
        init_vcsrepo(self.repo, self.commitevery)

    def grant_write_perm(self, group):
        req = self.request()
        managers = req.execute('CWGroup G WHERE G name %(group)s',
                               {'group': group}).get_entity(0, 0)
        req.create_entity(
            'CWPermission', name=u"write", label=u'repo x write perm',
            reverse_require_permission=self.vcsrepo,
            require_group=managers)
        self.commit()
