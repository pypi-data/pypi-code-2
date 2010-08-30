#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

import unittest
from pydenji.importer import NI

class  TestImporter(unittest.TestCase):
    def test_importer_imports_required_object(self):
        import os
        self.assertTrue(NI("os.unlink") is os.unlink)

if __name__ == '__main__':
    unittest.main()

