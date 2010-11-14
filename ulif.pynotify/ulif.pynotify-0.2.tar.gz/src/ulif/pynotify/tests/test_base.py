##
## test_base.py
## Login : <uli@pu.smp.net>
## Started on  Sat Jul 31 12:22:17 2010 Uli Fouquet
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
##
"""Tests for ulif.pynotify.base module.
"""
import os
import shutil
import tempfile
import time
import types
import unittest
from ulif.pynotify import (
    NONE, MODIFIED, DELETED, ADDED, FILE_TYPE, DIR_TYPE, UNKNOWN_TYPE
    )
from ulif.pynotify.base import FSWalker, FSChange


class TestBase(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.dbdir = tempfile.mkdtemp()
        self.dbpath = os.path.join(self.dbdir, 'test.db')
        self.samplefilepath = os.path.join(self.workdir, 'samplefile')
        self.treepath = os.path.join(self.workdir, 'sampletree')
        self.treesamplefile = os.path.join(self.treepath, 'treesample')
        open(self.samplefilepath, 'wb').write('foo')
        os.mkdir(self.treepath)
        open(self.treesamplefile, 'wb').write('bar')
        return

    def tearDown(self):
        shutil.rmtree(self.workdir)
        shutil.rmtree(self.dbdir)
        return

    def changeFile(self):
        open(self.treesamplefile, 'ab').write('baz')
        return

    def deleteFile(self):
        os.unlink(self.treesamplefile)
    
class TestFSChange(TestBase):

    def test_fs_change(self):
        change = FSChange(self.samplefilepath)
        self.assertEqual(change.path, self.samplefilepath)
        self.assertEqual(change.basename, 'samplefile')
        self.assertEqual(change.changetype, MODIFIED)
        self.assertEqual(change.filetype, FILE_TYPE)
        return

    def test_fs_change_changetype(self):
        change = FSChange(self.samplefilepath, ADDED)
        self.assertEqual(change.changetype, ADDED)

        change = FSChange(self.samplefilepath, DELETED)
        self.assertEqual(change.changetype, DELETED)
        return

    def test_fs_change_filetype(self):
        change = FSChange(self.samplefilepath)
        self.assertEqual(change.filetype, FILE_TYPE)

        change = FSChange(self.treepath)
        self.assertEqual(change.filetype, DIR_TYPE)

        change = FSChange('not-existent')
        self.assertEqual(change.filetype, UNKNOWN_TYPE)
        return
        
class TestFSWalker(TestBase):
    
    def test_base(self):
        walker = FSWalker()
        timestamp = 0
        result1 = walker.walk(timestamp, self.workdir)
        self.assertTrue(isinstance(result1, types.GeneratorType))
        return

    def test_status(self):
        walker = FSWalker()
        change1 = walker._checkStatus(self.samplefilepath, 0)
        change2 = walker._checkStatus(self.samplefilepath, time.time() + 1)
        mtime = os.stat(self.samplefilepath).st_mtime
        change3 = walker._checkStatus(self.samplefilepath, mtime)
        self.assertTrue(change1 is MODIFIED)
        self.assertTrue(change2 is NONE)
        self.assertTrue(change3 is MODIFIED)

    def test_parse_tree(self):
        walker = FSWalker()
        changes1 = list(walker.walk(self.treepath, 0))
        self.assertEqual(len(changes1), 2)

    def test_ignore_oserror(self):
        walker = FSWalker()
        changed = walker._checkStatus('not-existant-file', 0)
        self.assertEqual(changed, DELETED)
        
def test_suite():
    suite = unittest.TestSuite((
            unittest.makeSuite(TestFSChange),
            unittest.makeSuite(TestFSWalker),
         ))
    return suite

