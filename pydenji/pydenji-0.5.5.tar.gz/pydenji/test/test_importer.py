#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

import unittest
import sys

from pydenji.importer import NI, import_or_reload, get_by_fqdn

class  TestImporter(unittest.TestCase):
    def test_importer_imports_required_object(self):
        import os
        self.assertTrue(NI("os.unlink") is os.unlink)

class TestImportReload(unittest.TestCase):
    def setUp(self):
        if "pydenji.test.dummymodule" in sys.modules:
            sys.modules.pop("pydenji.test.dummymodule")

    def tearDown(self):
         if "pydenji.test.dummymodule" in sys.modules:
            sys.modules.pop("pydenji.test.dummymodule")

    def test_import_or_reload_imports_unimported_modules(self):
        import_or_reload("pydenji.test.dummymodule")
        self.assertTrue("pydenji.test.dummymodule" in sys.modules)

    def test_import_or_reload_reloads_imported_modules(self):
        import pydenji.test.dummymodule
        pydenji.test.dummymodule.sbirulabba = 1
        import_or_reload("pydenji.test.dummymodule")
        self.assertEquals(0, pydenji.test.dummymodule.sbirulabba)

    def test_import_or_reload_returns_imported_module(self):
        import pydenji.test.dummymodule
        self.assertEquals(pydenji.test.dummymodule, import_or_reload("pydenji.test.dummymodule"))

    def test_get_by_fqdn_fetches_object(self):
        self.assertEquals("0", get_by_fqdn("pydenji.test.dummymodule:sbirulabba.__str__")())
