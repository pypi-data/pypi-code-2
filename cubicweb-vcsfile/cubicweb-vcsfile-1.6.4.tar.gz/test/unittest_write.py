# -*- coding: utf-8 -*-
from shutil import rmtree, copytree
from os import system, unlink, chdir, getcwd
from os.path import join, split, exists, abspath
import tempfile

from cubicweb import Binary, QueryError, ValidationError, Unauthorized
from cubicweb import devtools # makes cubes importable
from cubes.vcsfile import entities, bridge

from utils import VCSFileTC

REPOBASEPATH = abspath(split(__file__)[0])

class _WriteTC(VCSFileTC):
    _repo_path = u'testrepocopy'
    def setUp(self):
        try:
            copytree(str(self.orig_repo_path), str(self.repo_path))
            VCSFileTC.setUp(self)
            self.copath = join(REPOBASEPATH, self._repo_path)
        except:
            rmtree(str(self.repo_path))
            raise
        self.grant_write_perm('managers')

    def tearDown(self):
        VCSFileTC.tearDown(self)
        rmtree(str(self._repo_path))

    def _test_new_revision(self, entity, vf, rev, revision):
        self.assertEqual(entity.content_for[0].eid, vf.eid)
        self.assertEqual(entity.description, u'add hôp')
        self.assertEqual(entity.author, 'syt')
        self.assertEqual(entity.data.getvalue(), 'hop\nhop\nhop\n')
        self.assertEqual(entity.data_encoding.lower(), self.repo_encoding)
        self.assertEqual(entity.data_format, 'text/plain')
        self.assertEqual(entity.rev.eid, rev.eid)
        self.assertEqual(entity.rev.revision, revision)
        self.assertTrue(entity.rev.parent_revision)
        self.assertTrue(entity.rev.reverse_at_revision)

    def _new_toto_revision(self, data='hop\nhop\nhop\n', branch=entities._MARKER):
        vf = self.execute('VersionedFile X WHERE X name "toto.txt"').get_entity(0, 0)
        rev = self.vcsrepo.make_revision(msg=u'add hôp', author=u'syt', branch=branch)
        vc = self.execute('INSERT VersionContent X: X content_for VF, X from_revision R, '
                           'X data %(data)s WHERE VF eid %(vf)s, R eid %(r)s',
                           {'vf': vf.eid, 'r': rev.eid,
                            'data': Binary(data)}).get_entity(0, 0)
        return vf, rev, vc

    def test_new_revision(self):
        vf, rev, vc = self._new_toto_revision()
        self.commit()
        self._test_new_revision(vc, vf, rev, 8 + self.repo_rev_offset)
        try:
            session = self.repo.internal_session()
            bridge.import_content(session)
        finally:
            session.close()
        self.assertEqual(len(self.execute('Any X WHERE X revision %(r)s', {'r': rev.revision})), 1)

    def test_new_revision_security(self):
        self.execute('DELETE CWPermission X')
        self.commit()
        self.assertRaises(Unauthorized, self._new_toto_revision)

# XXX unable to do this, we need to get the associated VersionedFile in source.add_entity...
#     def test_two_steps_new_revision(self):
#         vf = self.execute('VersionedFile X WHERE X name "toto.txt"')
#         eid = self.execute('INSERT VersionContent X: X description %(msg)s, X author %(author)s, '
#                            'X data %(data)s', {'msg': u'add hôp', 'author': u'syt',
#                                                'data': Binary('hop\nhop\nhop\n')})[0][0]
#         self.execute('SET X content_for VF WHERE X eid %(x)s, VF eid %(vf)s',
#                      {'vf': vf[0][0], 'x': eid}, ('vf', 'x'))
#         self.commit()
#         self._test_new_revision(vf, eid)

    def test_rollback_new_revision(self):
        vf, rev, vc = self._new_toto_revision()
        self.rollback()
        # fail due to a bug in pysqlite, see
        # http://oss.itsystementwicklung.de/trac/pysqlite/ticket/219
        # http://www.sqlite.org/cvstrac/tktview?tn=2765,3
        # http://www.initd.org/pub/software/pysqlite/doc/usage-guide.html#controlling-transactions
        #rset = self.execute('Any X WHERE X eid %(x)s', {'x': rev.eid})
        #self.failIf(rset)
        rset = self.execute('Any X WHERE X eid %(x)s', {'x': vc.eid})
        self.failIf(rset)
        rset = self.execute('VersionContent X WHERE X content_for VF, VF eid %(vf)s', {'vf': vf.eid})
        self.assertEqual(len(rset), 2)
        # XXX check actually not in the repository

    def test_error_new_revision(self):
        # can't specify revision number
        self.assertRaises(QueryError, self.execute,
                          'INSERT Revision X: X from_repository R, '
                           'X description %(msg)s, X author %(author)s, X revision 2 '
                           'WHERE R eid %(r)s',
                           {'r': self.repoeid, 'msg': u'add hôp', 'author': u'syt'})
        # missing from_repository
        self.assertRaises(ValidationError, self.execute,
                          'INSERT Revision X: '
                           'X description %(msg)s, X author %(author)s '
                           'WHERE R eid %(r)s',
                           {'r': self.repoeid, 'msg': u'add hôp', 'author': u'syt'})
        self.rollback()
        # OK
        self.execute('INSERT Revision X: X from_repository R, '
                     'X description %(msg)s, X author %(author)s '
                     'WHERE R eid %(r)s',
                     {'r': self.repoeid, 'msg': u'add hôp', 'author': u'syt'})
        # try to create another revision
        self.assertRaises(QueryError, self.execute,
                          'INSERT Revision X: X from_repository R, '
                          'X description %(msg)s, X author %(author)s '
                          'WHERE R eid %(r)s',
                          {'r': self.repoeid, 'msg': u'add hôp', 'author': u'syt'})
        # commit while nothing changed in the revision
        self.assertRaises(QueryError, self.commit)

    def test_error_new_version_content(self):
        vfeid = self.execute('VersionedFile X WHERE X name "toto.txt"')[0][0]
        badreveid = self.execute('Revision X WHERE X revision 1')[0][0]
        # no revision transaction
        self.assertRaises(QueryError, self.execute,
                          'INSERT VersionContent X: X content_for VF, X from_revision R, '
                           'X data %(data)s WHERE VF eid %(vf)s, R eid %(r)s',
                          {'vf': vfeid, 'r': badreveid,
                           'data': Binary('hop\nhop\nhop\n')})
        # missing content_for relation
        reveid = self.execute('INSERT Revision X: X from_repository R, '
                              'X description %(msg)s, X author %(author)s '
                              'WHERE R eid %(r)s',
                              {'r': self.repoeid, 'msg': u'add hôp', 'author': u'syt'})[0][0]
        self.assertRaises(ValidationError, self.execute,
                          'INSERT VersionContent X: X from_revision R, '
                           'X data %(data)s WHERE R eid %(r)s',
                          {'r': reveid,
                           'data': Binary('hop\nhop\nhop\n')})
        self.rollback()
        # missing data attribute
        self.assertRaises(ValidationError, self.execute,
                          'INSERT VersionContent X: X content_for VF, X from_revision R '
                           'WHERE VF eid %(vf)s, R eid %(r)s',
                          {'vf': vfeid, 'r': badreveid})
        self.rollback()
        # missing from_revision relation
        reveid = self.execute('INSERT Revision X: X from_repository R, '
                              'X description %(msg)s, X author %(author)s '
                              'WHERE R eid %(r)s',
                              {'r': self.repoeid, 'msg': u'add hôp', 'author': u'syt'})[0][0]
        self.execute('INSERT VersionContent X: X content_for VF, '
                     'X data %(data)s WHERE VF eid %(vf)s',
                     {'vf': vfeid, 'data': Binary('hop\nhop\nhop\n')})
        self.assertRaises(ValidationError, self.commit)
        self.rollback()
        # bad from_revision relation
        reveid = self.execute('INSERT Revision X: X from_repository R, '
                              'X description %(msg)s, X author %(author)s '
                              'WHERE R eid %(r)s',
                              {'r': self.repoeid, 'msg': u'add hôp', 'author': u'syt'})[0][0]
        self.execute('INSERT VersionContent X: X content_for VF, X from_revision R, '
                     'X data %(data)s WHERE VF eid %(vf)s, R eid %(r)s',
                     {'vf': vfeid, 'r': badreveid,
                      'data': Binary('hop\nhop\nhop\n')})
        self.assertRaises(QueryError, self.commit)

    def test_new_file(self):
        vfeid = self.execute('INSERT VersionedFile X: X from_repository R, '
                          'X directory %(dir)s, X name %(name)s WHERE R eid %(repo)s',
                          {'repo': self.repoeid, 'dir': u'dir1', 'name': u'tutu.png'})[0][0]
        reveid = self.execute('INSERT Revision X: X from_repository R, '
                              'X description %(msg)s, X author %(author)s '
                              'WHERE R eid %(r)s',
                              {'r': self.repoeid, 'msg': u'new file', 'author': u'syt'})[0][0]
        eid = self.execute('INSERT VersionContent X: X content_for %(vf)s, X from_revision %(r)s, '
                           'X data %(data)s',
                           {'vf': vfeid, 'r': reveid, 'msg': u'new file', 'author': u'syt',
                            'data': Binary('zoubî')})[0][0]
        self.commit()
        entity = self.execute('Any X WHERE X eid %(x)s', {'x': eid}).get_entity(0, 0)
        vf = entity.content_for[0]
        self.assertEqual(vf.from_repository[0].eid, self.repoeid)
        self.assertEqual(vf.directory, 'dir1')
        self.assertEqual(vf.name, 'tutu.png')
        self.assertEqual(entity.description, 'new file')
        self.assertEqual(entity.author, 'syt')
        self.assertEqual(entity.data.getvalue(), 'zoubî')
        self.assertEqual(entity.data_encoding, None)
        self.assertEqual(entity.data_format, 'image/png')

    def test_error_new_file(self):
        self.execute('INSERT VersionedFile X: X directory %(dir)s, X name %(name)s WHERE R eid %(repo)s',
                     {'repo': self.repoeid, 'dir': u'dir1', 'name': u'tutu.txt'})
        self.assertRaises(ValidationError, self.commit)
        self.execute('INSERT VersionedFile X: X directory %(dir)s, X name %(name)s, X from_repository R '
                     'WHERE R eid %(repo)s', {'repo': self.repoeid, 'dir': u'dir1', 'name': u'tutu.txt'})
        self.assertRaises(QueryError, self.commit)

    def test_multiple_changes_and_deletion(self):
        reveid = self.execute('INSERT Revision X: X from_repository R, '
                              'X description %(msg)s, X author %(author)s '
                              'WHERE R eid %(r)s',
                              {'r': self.repoeid, 'msg': u'add hop', 'author': u'syt'})[0][0]
        vf1 = self.execute('VersionedFile X WHERE X name "toto.txt"')
        eid1 = self.execute('INSERT VersionContent X: X content_for %(vf)s, X from_revision %(r)s, '
                            'X data %(data)s',
                            {'vf': vf1[0][0], 'r': reveid,
                             'data': Binary('hop\nhop\nhop\n')})[0][0]
        vf2 = self.execute('INSERT VersionedFile X: X from_repository R, '
                           'X directory %(dir)s, X name %(name)s WHERE R eid %(repo)s',
                           {'repo': self.repoeid, 'dir': u'dir1', 'name': u'tutu.txt'})
        eid2 = self.execute('INSERT VersionContent X: X content_for %(vf)s, X from_revision %(r)s, '
                           'X data %(data)s',
                            {'vf': vf2[0][0], 'r': reveid,
                             'data':Binary('zoubî')})[0][0]
        self.commit()
        self.assertFalse(self.vcsrepo.is_directory_deleted('dir1'))
        entity1 = self.execute('Any X WHERE X eid %(x)s', {'x': eid1}).get_entity(0, 0)
        self.assertEqual(entity1.content_for[0].eid, vf1[0][0])
        self.assertEqual(entity1.description, 'add hop')
        self.assertEqual(entity1.author, 'syt')
        self.assertEqual(entity1.data.getvalue(), 'hop\nhop\nhop\n')
        entity2 = self.execute('Any X WHERE X eid %(x)s', {'x': eid2}).get_entity(0, 0)
        vf2 = entity2.content_for[0]
        self.assertEqual(vf2.from_repository[0].eid, self.repoeid)
        self.assertEqual(vf2.directory, 'dir1')
        self.assertEqual(vf2.name, 'tutu.txt')
        self.assertEqual(entity2.description, 'add hop')
        self.assertEqual(entity2.author, 'syt')
        self.assertEqual(entity2.data.getvalue(), 'zoubî')
        # deletion
        tmpdir = tempfile.mkdtemp()
        try:
            self.checkout(tmpdir)
            self.failUnless(exists(join(tmpdir, 'dir1', 'tutu.txt')))
            self.failUnless(exists(join(tmpdir, 'toto.txt')))
        finally:
            rmtree(tmpdir)
        reveid = self.execute('INSERT Revision X: X from_repository R, '
                              'X description %(msg)s, X author %(author)s '
                              'WHERE R eid %(r)s',
                              {'r': self.repoeid, 'msg': u'kill', 'author': u'auc'})[0][0]
        vf1 = self.execute('VersionedFile X WHERE X name "toto.txt"')
        # let's delete toto by linking its vf to DeletedVersionContent
        eid1 = self.execute('INSERT DeletedVersionContent X: X content_for %(vf)s, X from_revision %(r)s',
                           {'vf': vf1[0][0], 'r': reveid})[0][0]
        self.commit()
        entity1 = self.execute('Any X WHERE X eid %(x)s', {'x': eid1}).get_entity(0, 0)
        self.assertEqual(entity1.content_for[0].eid, vf1[0][0])
        self.assertEqual(entity1.description, 'kill')
        self.assertEqual(entity1.author, 'auc')
        tmpdir = tempfile.mkdtemp()
        try:
            self.checkout(tmpdir)
            self.failUnless(exists(join(tmpdir, 'dir1', 'tutu.txt')))
            self.failIf(exists(join(tmpdir, 'toto.txt')))
            self.failIf(exists(join(tmpdir, 'dir1', 'subdir')))
        finally:
            rmtree(tmpdir)
        oddfile = self.execute('VersionedFile F WHERE F name "__hg_needs_a_file__"').get_entity(0,0)
        content = vf1.get_entity(0,0).reverse_content_for
        self.assertEqual(len(content), 4)
        self.assertIsInstance(content[0], entities.DeletedVersionContent)
        content = oddfile.reverse_content_for
        self.assertEqual(len(content), 2)
        self.assertIsInstance(content[0], entities.DeletedVersionContent)
        self.failUnless(self.vcsrepo.is_directory_deleted('dir1/ghostdir'))


class SVNSourceWriteTC(_WriteTC):
    orig_repo_path = 'testrepo'
    repo_type = u'subversion'
    repo_rev_offset = 0

    def checkout(self, tmpdir):
        svncmd = 'svn co file://%s %s >/dev/null 2>&1' % (self.copath, tmpdir)
        if system(svncmd):
            raise Exception('can not check out %s' % self.copath)


class HGSourceWriteTC(_WriteTC):
    orig_repo_path = 'testrepohg'
    repo_type = u'mercurial'
    repo_encoding = u'latin1'
    repo_rev_offset = -1

    def checkout(self, tmpdir):
        svncmd = 'hg clone %s %s >/dev/null 2>&1' % (self.copath, join(tmpdir, 'testrepohg'))
        if system(svncmd):
            raise Exception('can not check out %s' % self.copath)
        system('mv %s %s' % (join(tmpdir, 'testrepohg', '*'), tmpdir))
        system('mv %s %s' % (join(tmpdir, 'testrepohg', '.hg'), tmpdir))

    def test_branches_from_app(self):
        vf, rev, vc = self._new_toto_revision(data='branch 1.2.3 content',
                                              branch=u'1.2.3')
        self.commit()
        hgdir = self.copath
        self.assertEqual(file(join(hgdir, 'toto.txt')).read(),
                          'hop\nhop\n\n')
        system('cd %s; hg up 1.2.3 >/dev/null 2>&1' % hgdir)
        self.assertEqual(file(join(hgdir, 'toto.txt')).read(),
                          'branch 1.2.3 content')
        # create new changeset in the default branch
        vf, rev, vc = self._new_toto_revision(data='branch default content')
        self.commit()
        system('cd %s; hg up default >/dev/null 2>&1' % hgdir)
        self.assertEqual(file(join(hgdir, 'toto.txt')).read(),
                          'branch default content')
        # create new changeset in the 1.2.3 branch
        vf, rev, vc = self._new_toto_revision(data='branch 1.2.3 new content',
                                              branch=u'1.2.3')
        self.commit()
        system('cd %s; hg up default >/dev/null 2>&1' % hgdir)
        self.assertEqual(file(join(hgdir, 'toto.txt')).read(),
                          'branch default content')
        # delete file from both branches
        vf.vcs_rm(branch=u'default', author=u'titi')
        self.commit()
        system('cd %s; hg up default >/dev/null 2>&1' % hgdir)
        self.failIf(exists((join(hgdir, 'toto.txt'))))
        vf.vcs_rm(branch=u'1.2.3', author=u'toto')
        self.commit()
        system('cd %s; hg up 1.2.3 >/dev/null 2>&1' % hgdir)
        self.failIf(exists((join(hgdir, 'toto.txt'))))
        vf.clear_all_caches()
        ex = self.assertRaises(QueryError, vf.vcs_rm, branch=u'1.2.3', author=u'toto')
        self.assertEqual(str(ex), 'toto.txt is already deleted from the vcs')

    def test_strip(self):
        self.assertEqual(self.vcsrepo.latest_known_revision(), 6)
        vcrset = self.execute('Any X WHERE X from_revision R, R revision 6')
        system('cd %s; hg --config extensions.hgext.mq= strip 6 2>/dev/null' % self.copath)
        try:
            session = self.repo.internal_session()
            bridge.import_content(session)
        finally:
            session.close()
        self.commit()
        self.assertEqual(self.vcsrepo.latest_known_revision(), 5)
        for eid, in vcrset:
            self.failIf(self.execute('Any X WHERE X eid %(x)s', {'x': eid}))

    def test_branches_from_hg(self):
        self.assertEqual(self.execute('Any COUNT(R) WHERE R is Revision').rows, [[7]])
        hgdir = self.copath
        system('cd %s; hg up default >/dev/null 2>&1' % hgdir)
        system('cd %s; hg branch newbranch >/dev/null 2>&1' % hgdir)
        system('cd %s; hg tag newbranch -m "opening newbranch"' % hgdir)
        try:
            session = self.repo.internal_session()
            bridge.import_content(session)
        finally:
            session.close()
        self.commit()
        hgtags = self.execute('VersionContent V WHERE V content_for VF,  '
                              'VF name ".hgtags"').get_entity(0,0)
        self.assertEqual(hgtags.from_revision[0].branch, u'newbranch')
        self.assertEqual(hgtags.from_revision[0].revision, 7)
        self.assertEqual(self.execute('Any COUNT(R) WHERE R is Revision').rows, [[8]])



if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
