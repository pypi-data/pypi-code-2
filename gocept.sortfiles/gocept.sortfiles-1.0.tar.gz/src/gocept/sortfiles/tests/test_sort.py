# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.sortfiles.main import _sort_files as sort_files
import datetime
import os
import shutil
import tempfile
import unittest


class SortTest(unittest.TestCase):

    def setUp(self):
        super(SortTest, self).setUp()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        super(SortTest, self).tearDown()

    def test_filing(self):
        open(os.path.join(self.tmpdir, 'foo'), 'w').close()
        sort_files(self.tmpdir)
        self.assert_(not os.path.exists(os.path.join(self.tmpdir, 'foo')))
        today = datetime.date.today()
        self.assertTrue(os.path.exists(os.path.join(
            self.tmpdir, str(today.year),
            '%02d' % today.month, '%02d' % today.day, 'foo')))

        open(os.path.join(self.tmpdir, 'bar'), 'w').close()
        sort_files(self.tmpdir)
        self.assertFalse(os.path.exists(os.path.join(self.tmpdir, 'bar')))
