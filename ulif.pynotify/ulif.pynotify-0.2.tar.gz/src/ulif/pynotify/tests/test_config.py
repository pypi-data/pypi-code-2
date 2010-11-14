##
## test_config.py
## Login : <uli@pu.smp.net>
## Started on  Sat Jul 31 10:32:51 2010 Uli Fouquet
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
"""Tests for ulif.pynotify.config module.
"""
import shutil
import tempfile
import unittest
from ulif.pynotify.ui.config import get_config_paths, PyNotifyConfigParser

class TestConfigBase(unittest.TestCase):

    def setUp(self):
        self.userdir = tempfile.mkdtemp()
        self.workdir = tempfile.mkdtemp()
        return

    def tearDown(self):
        shutil.rmtree(self.userdir)
        shutil.rmtree(self.workdir)
        return

class TestConfigParser(TestConfigBase):

    def test_getconfigpaths(self):
        result1 = get_config_paths()
        result2 = get_config_paths(self.workdir)
        self.assertEqual(len(result1), 2)
        self.assertEqual(len(result2), 3)
        self.assertEqual(result2[2], self.workdir)
        return

    def test_paser_base(self):
        parser = PyNotifyConfigParser()
        parser.read()

def test_suite():
    suite = unittest.TestSuite((
        unittest.makeSuite(TestConfigBase),
        unittest.makeSuite(TestConfigParser),
         ))
    return suite
