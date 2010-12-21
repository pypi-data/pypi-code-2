##
## test_iowatcher.py
## Login : <uli@pu.smp.net>
## Started on  Wed Nov 17 18:04:20 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
import os
import shutil
import tempfile
import unittest
from ulif.pynotify import ADDED, MODIFIED, DELETED
from odls.client.iowatchdog import ODLSIOWatcher
from odls.client.tests.test_configuration import create_custom_conf

class IOWatchdogTest(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.ini_path = os.path.join(self.workdir, 'custom.ini')
        self.filepath = os.path.join(self.workdir, 'files')
        self.dbpath = os.path.join(self.workdir, 'indexer.db')
        self.singlewatchfile = os.path.join(self.workdir, 'singlefile.txt')
        os.mkdir(self.filepath)
        open(os.path.join(self.filepath, 'sample.txt'), 'wb').write(
            "Some sample file\n")
        open(self.singlewatchfile, 'wb').write(
            "Some single watched samplefile\n")
        create_custom_conf(
            self.ini_path, defaults=dict(
                server_url='http://localhost:8080/echo',
                http_username='test',
                http_username_prefix='',
                http_pw='test',
                http_pw_prefix='',
                watch_folders=self.filepath,
                watch_files=self.singlewatchfile,
                dbfile = self.dbpath,
                )
            )
        self.createFakeApp()
        return

    def tearDown(self):
        shutil.rmtree(self.workdir)
        return

    def createFakeApp(self, argv=None):
        if argv == None:
            argv = ['-c', self.ini_path]
        self.app = object()
        from odls.client.configuration import ODLSConfiguration
        config = ODLSConfiguration(argv=argv)
        class FakeApp(object):
            config = None
            logger = None
        self.app = FakeApp()
        self.app.config = config
        return

    def test_create(self):
        watcher = ODLSIOWatcher(self.app)
        self.assertTrue(watcher.db.endswith('indexer.db'))
        self.assertEqual(watcher.app, self.app)
        return

    def test_stop(self):
        watcher = ODLSIOWatcher(self.app)
        watcher.stop()
        return

    def test_getchanges_nodirectories(self):
        watcher = ODLSIOWatcher(self.app)
        changes = sorted(list(watcher.getChanges()))
        os.mkdir(os.path.join(self.workdir, 'somesampledir'))
        changes = sorted(list(watcher.getChanges()))
        self.assertEqual(len(changes), 0)
        return
        
    def test_getchanges_add_file_in_dir(self):
        watcher = ODLSIOWatcher(self.app)
        changes = sorted(list(watcher.getChanges()))
        change = [x for x in changes if x.basename == 'sample.txt'][0]
        self.assertEqual(ADDED, change.changetype)
        return

    def test_getchanges_add_singlefile(self):
        watcher = ODLSIOWatcher(self.app)
        changes = sorted(list(watcher.getChanges()))
        change = [x for x in changes if x.basename == 'singlefile.txt'][0]
        self.assertEqual(ADDED, change.changetype)
        return

    def test_getchanges_unmodified(self):
        watcher = ODLSIOWatcher(self.app)
        changes = sorted(list(watcher.getChanges()))
        changes = sorted(list(watcher.getChanges()))
        self.assertEqual(len(changes), 0)
        return

    def test_getchanges_respect_blacklist(self):
        self.app.config.options.watch_blacklist = ['sample.txt',]
        watcher = ODLSIOWatcher(self.app)
        changes = sorted(list(watcher.getChanges()))
        self.assertEqual(len(changes), 1)
        return

    def test_blacklist(self):
        watcher = ODLSIOWatcher(self.app)
        result0 = watcher.inBlacklist('/some/path/somefile~')
        result1 = watcher.inBlacklist('/some/path/somefile~withtilde')
        self.assertEqual(result0, True)
        self.assertEqual(result1, False)
        return

    def test_blacklist_simple(self):
        self.app.config.options.watch_blacklist = ['somefile.txt',]
        watcher = ODLSIOWatcher(self.app)
        result0 = watcher.inBlacklist('somefile.txt')
        result1 = watcher.inBlacklist('somefile.pdf')
        self.assertEqual(result0, True)
        self.assertEqual(result1, False)
        return

    def test_blacklist_asterisk(self):
        self.app.config.options.watch_blacklist = ['somefile.*',]
        watcher = ODLSIOWatcher(self.app)
        result0 = watcher.inBlacklist('somefile.txt')
        result1 = watcher.inBlacklist('somefile.pdf')
        result2 = watcher.inBlacklist('thesomefile.pdf')
        self.assertEqual(result0, True)
        self.assertEqual(result1, True)
        self.assertEqual(result2, False)
        return

    def test_blacklist_questionmark(self):
        self.app.config.options.watch_blacklist = ['s?mefile.txt',]
        watcher = ODLSIOWatcher(self.app)
        result0 = watcher.inBlacklist('somefile.txt')
        result1 = watcher.inBlacklist('simefile.txt')
        result2 = watcher.inBlacklist('somefile.pdf')
        self.assertEqual(result0, True)
        self.assertEqual(result1, True)
        self.assertEqual(result2, False)
        return

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(
        IOWatchdogTest)
    return suite

test_suite = suite

if __name__ == '__main__':
    unittest.main(defaultTests='test_suite')
