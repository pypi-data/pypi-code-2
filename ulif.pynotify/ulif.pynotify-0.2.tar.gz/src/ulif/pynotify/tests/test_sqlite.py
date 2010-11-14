##
## test_sqlite.py
## Login : <uli@pu.smp.net>
## Started on  Mon Oct 25 15:06:53 2010 Uli Fouquet
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
"""Tests for ulif.pynotify.sqlite module.
"""
import os
import time
import types
import unittest
from datetime import datetime, timedelta
from pysqlite2.dbapi2 import OperationalError
from ulif.pynotify.tests.test_base import TestBase
from ulif.pynotify import (
    NONE, MODIFIED, DELETED, ADDED, FILE_TYPE, DIR_TYPE, UNKNOWN_TYPE
    )
from ulif.pynotify.sqlite import SQLiteFSWalker

class TestSQLiteFSWalker(TestBase):

    def setUp(self):
        super(TestSQLiteFSWalker, self).setUp()
        self.walker = SQLiteFSWalker()

    def tearDown(self):
        del self.walker
        super(TestSQLiteFSWalker, self).tearDown()
        
    def test_sqlite(self):
        walker = self.walker
        timestamp = 0
        result1 = walker.walk(self.workdir)
        self.assertTrue(isinstance(result1, types.GeneratorType))
        return

    def test_status_added(self):
        walker = self.walker
        change = walker._checkStatus(self.samplefilepath)
        self.assertEqual(change[0], ADDED)

    def test_status_unmodified(self):
        walker = self.walker
        conn = walker.conn
        cur = conn.cursor()
        walker.execute(
            cur,
            'replace into filechanges(path, status, ts) values(?, ?, ?)',
            (self.samplefilepath, ADDED, datetime.now())
            )
        change = walker._checkStatus(self.samplefilepath)
        self.assertEqual(change[0], NONE)

    def test_status_modified(self):
        walker = self.walker
        conn = walker.conn
        cur = conn.cursor()
        # Get a timestamp from the past...
        ts = datetime.now() - timedelta(seconds=5)
        walker.execute(
            cur,
            'replace into filechanges(path, status, ts) values(?, ?, ?)',
            (self.samplefilepath, ADDED, ts)
            )
        # Touch testfile to have current timestamp...
        os.utime(self.samplefilepath, None)
        change = walker._checkStatus(self.samplefilepath)
        self.assertEqual(change[0], MODIFIED)

    def test_status_deleted(self):
        walker = self.walker
        change = walker._checkStatus('not-existent')
        self.assertEqual(change[0], DELETED)

    def test_parse_tree(self):
        walker = self.walker
        changes1 = list(walker.walk(self.treepath))
        self.assertEqual(len(changes1), 2)

    def test_ignore_oserror(self):
        walker = self.walker
        changed, timestamp = walker._checkStatus('not-existant-file')
        self.assertEqual(changed, DELETED)

    def test_change(self):
        walker = self.walker
        changes1 = list(walker.walk(self.treepath))
        self.assertEqual(len(changes1), 2)
        self.assertEqual(changes1[0].changetype, ADDED)
        changes2 = list(walker.walk(self.treepath))
        self.assertEqual(len(changes2), 0)

    def test_walk_added(self):
        walker = self.walker
        changes = list(walker.walk(self.treepath))
        self.assertEqual(changes[0].changetype, ADDED)

    def test_walk_unmodified(self):
        walker = self.walker
        # find all files
        changes = list(walker.walk(self.treepath))
        # find them all again (no changes)
        changes = list(walker.walk(self.treepath))
        self.assertEqual(len(changes), 0)

    def test_walk_modified(self):
        walker = self.walker
        changes = list(walker.walk(self.treepath))
        # Touch testfile with slightly increased timestamp...
        mtime = os.stat(self.treesamplefile).st_mtime + 0.1
        os.utime(self.treesamplefile, (mtime, mtime))
        changes = list(walker.walk(self.treepath))
        self.assertTrue(len(changes) > 0)
        self.assertEqual(changes[0].changetype, MODIFIED)

    def test_walk_deleted(self):
        walker = self.walker
        changes = list(walker.walk(self.treepath))
        os.unlink(self.treesamplefile)
        changes = list(walker.walk(self.treepath))
        # Make sure we only have the interesting change in list...
        changes = [x for x in changes if x.path == self.treesamplefile]
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].changetype, DELETED)

    def test_walk_add_after_delete(self):
        # If a file is readded after deletion and the last walk
        # notified the deletion, then the following walk should
        # message 'Added' and not 'modified'
        walker = self.walker
        changes = list(walker.walk(self.treepath))
        os.unlink(self.treesamplefile)
        changes = list(walker.walk(self.treepath))
        open(self.treesamplefile, 'wb').write('test')
        changes = list(walker.walk(self.treepath))
        changes = [x for x in changes if x.path == self.treesamplefile]
        self.assertEqual(changes[0].changetype, ADDED)
        return

    def test_walk_delete_after_2_runs(self):
        # Also to please coverage-detector...
        walker = self.walker
        changes = list(walker.walk(self.treepath))
        os.unlink(self.treesamplefile)
        changes = list(walker.walk(self.treepath))
        changes = list(walker.walk(self.treepath))
        self.assertEqual(len(changes), 0)
        return
        
    def test_sql_executor(self):
        walker = self.walker
        cur = walker.conn.cursor()
        walker.execute(cur, 'drop table filechanges')
        # Provoke an SQL problem...
        self.assertRaises(
            OperationalError, walker.execute, cur, 'select * from filechanges')
        return

def test_suite():
    suite = unittest.TestSuite((
            unittest.makeSuite(TestSQLiteFSWalker),
         ))
    return suite
