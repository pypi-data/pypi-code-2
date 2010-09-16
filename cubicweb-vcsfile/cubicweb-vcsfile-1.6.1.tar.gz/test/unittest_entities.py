from os.path import join, abspath
from logilab.common.decorators import clear_cache
from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC
from utils import VCSFileTC, HERE

class BranchHeadsTC(VCSFileTC):
    _repo_path = u'testrepohg_branches'
    repo_type = u'mercurial'

    def rev(self, file, *args):
        return self.vcsrepo.versioned_file('', file).branch_head(*args).revision

    def test_vcsrm(self):
        self.grant_write_perm('managers')
        # XXX outcome depends on method names (=> execution order)
        vf = self.vcsrepo.versioned_file('', 'README')
        vf.vcs_rm()
        self.commit()
        clear_cache(vf, 'branch_head')
        clear_cache(vf, 'version_content')
        self.assertTrue(vf.deleted_in_branch())
        self.assertTrue(vf.head.rev.parent_revision)
        self.assertEquals(len(vf.head.rev.reverse_at_revision), 3,
                          vf.head.rev.reverse_at_revision)

    def test_branch_head_no_arg(self):
        self.assertEquals(self.rev('README'), 1)
        self.assertEquals(self.rev('file.txt'), 4)
        self.assertEquals(self.rev('otherfile.txt'), 4)

    def test_branch_head_default(self):
        self.assertEquals(self.rev('README', 'default'), 1)
        self.assertEquals(self.rev('file.txt', 'default'), 4)
        self.assertEquals(self.rev('otherfile.txt', 'default'), 4)

    def test_branch_head_branch1(self):
        self.assertEquals(self.rev('README', 'branch1'), 1)
        self.assertEquals(self.rev('file.txt', 'branch1'), 2)
        self.assertEquals(self.rev('otherfile.txt', 'branch1'), 3)


class RepositoryTC(CubicWebTC):
    def test_repo_path_security(self):
        req = self.request()
        path = unicode(abspath(join(HERE, 'whatever')))
        vcsrepo = req.create_entity('Repository',
                                    path=path, type=u'mercurial')
        req.cnx.commit()
        self.assertEquals(vcsrepo.dc_title(),
                          u'mercurial:%s' % path)
        self.login('anon')
        req = self.request()
        vcsrepo = req.execute('Repository X').get_entity(0, 0)
        self.assertEquals(vcsrepo.dc_title(), 'mercurial repository #%s' % vcsrepo.eid)

    def test_unmodifiable_attrs(self):
        req = self.request()
        self.assertRaises(ValidationError, req.create_entity, 'Repository',
                          source_url=u"http://myrepo.ru",
                          type=u'mercurial')
        req.cnx.rollback()
        req = self.request()
        repo = req.create_entity('Repository', type=u'mercurial',
                                 path=unicode(abspath(join(HERE, 'whatever'))))
        req.cnx.commit()
        self.assertRaises(ValidationError, repo.set_attributes, path=u'new')
        self.assertRaises(ValidationError, repo.set_attributes, type=u'mercurial')
        self.assertRaises(ValidationError, repo.set_attributes, source_url=u'http://myrepo.fr')

    def test_source_url_format(self):
        req = self.request()
        self.assertRaises(ValidationError, req.create_entity, 'Repository',
                          path=u'whatever', type=u'mercurial')
        self.assertRaises(ValidationError, req.create_entity, 'Repository',
                          source_url=u'whatever', type=u'mercurial')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
