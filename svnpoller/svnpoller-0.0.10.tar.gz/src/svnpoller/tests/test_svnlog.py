import os
from base import TestBase
from base import TEST_URL, TEST_REVS, TEST_MAX_REV
from svnpoller import svnlog


class TestSvnlog(TestBase):

    def setUp(self):
        super(TestSvnlog, self).setUp()

    def test_log_class(self):
        target_rev = TEST_REVS[2]
        log = svnlog.Log(TEST_URL, target_rev)
        self.assertEqual(target_rev, log.rev)
        self.assertEqual(TEST_URL, log.url)
        self.assertEqual('http://svn.freia.jp/open', log.root)
        self.assertEqual('/zope2docs/branches', log.subpath)
        self.assertEqual([('M', '/zope2docs/branches/ja/2.12.4/doc/INSTALL-buildout.rst'),
                          ('M', '/zope2docs/branches/ja/2.12.4/doc/operation.rst'),
                         ], log.paths)
        #self.assertEqual('', log.normalized_paths)
        self.assertEqual('taka', log.author)
        self.assertEqual('2010-04-06 13:47:53', log.date.strftime('%Y-%m-%d %H:%M:%S'))
        self.assertEqual(u'update to 2.12.4 release (r110522)\n\n\u548c\u8a33\u5b8c\u4e86', log.msg)
        self.assert_(log.diff)

    def test_get_revisions_ids(self):
        revs = svnlog.get_revisions([TEST_URL])
        self.assertEqual(TEST_REVS, revs)

    def test_get_revisions_by_non_exist_revision(self):
        revs = svnlog.get_revisions([TEST_URL], TEST_MAX_REV+1)
        self.assertEqual([], revs)

    def test_get_logs(self):
        logs = svnlog.get_logs(TEST_URL)
        self.assertEqual(7, len(logs))
        for log in logs:
            self.assert_(log.rev)
            self.assertEqual('http://svn.freia.jp/open', log.root)

    def test_print_copied_information_instead_of_full_diff(self):
        rev = TEST_REVS[0] # copy only commit
        log = svnlog.Log(TEST_URL, rev)

        self.assertEqual(rev, log.rev)
        self.assertEqual(['A'], [x[0] for x in log.paths])
        self.assertFalse('diff' in [x[1] for x in self._cmd_hist], "Not need 'svn diff' when copy only commit")
        self.assertTrue('Copied:', log.diff)

    def test_print_moved_information_instead_of_full_diff(self):
        rev = TEST_REVS[1] # move only commit
        log = svnlog.Log(TEST_URL, rev)

        self.assertEqual(rev, log.rev)
        self.assertEqual(set(['A','D']), set([x[0] for x in log.paths]))
        self.assertFalse('diff' in [x[1] for x in self._cmd_hist], "Not need 'svn diff' when move only commit")
        self.assertTrue('Copied:', log.diff)
        self.assertTrue('Deleted:', log.diff)

