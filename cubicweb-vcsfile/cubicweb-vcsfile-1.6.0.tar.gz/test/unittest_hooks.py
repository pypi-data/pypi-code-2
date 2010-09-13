from utils import VCSFileTC

class HooksTC(VCSFileTC):

    def setup_database(self):
        self.request().create_entity('Tag', name=u'dir1')
        self.request().create_entity('Folder', name=u'dir1')

    def test_auto_classification(self):
        toto = self.execute('Any X WHERE X name "toto.txt"').get_entity(0, 0)
        self.failIf(toto.reverse_tags)
        self.failIf(toto.filed_under)
        tutu = self.execute('Any X WHERE X name "tutu.txt"').get_entity(0, 0)
        self.failUnless(tutu.reverse_tags)
        self.failUnless(tutu.filed_under)


class AtRevisionHooksTC(VCSFileTC):
    _repo_path = u'testrepohg_branches'
    repo_type = u'mercurial'

    def test_at_revision_is_set(self):
        self.failUnless(self.execute('Any X WHERE X at_revision Y'))
        def files(revnum):
            rev = self.execute('Revision X WHERE X revision %(rev)s', {'rev': revnum}).get_entity(0, 0)
            return sorted((x.file.name, x.revision) for x in rev.reverse_at_revision)
        self.assertEquals(files(0), [(u'README', 0), (u'file.txt', 0)])
        self.assertEquals(files(1), [(u'README', 1), (u'file.txt', 0)])
        self.assertEquals(files(2), [(u'README', 1), (u'file.txt', 2)])
        self.assertEquals(files(3), [(u'README', 1), (u'file.txt', 2), (u'otherfile.txt', 3)])
        self.assertEquals(files(4), [(u'README', 1), (u'file.txt', 4), (u'otherfile.txt', 4)])

    def test_vf_creation_date(self):
        vf = self.vcsrepo.versioned_file('', 'file.txt')
        self.failIf(vf.creation_date == vf.modification_date)
        rev = vf.branch_head().rev
        self.assertEquals(vf.modification_date, rev.creation_date)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

