# -*- coding: utf-8 -*-

import unittest
import os
import shutil

from import_file import import_file

STUB_NAME = 'stub.py'
STUB_LOC = os.path.join('tools', STUB_NAME)

class TestCase(unittest.TestCase):
    def testImportsHere(self):
        shutil.copy(STUB_LOC, '.')
        try:
            stub = import_file(STUB_NAME)
            self.assertEqual(stub.A_VAR, 123)
        finally:
            os.remove(STUB_NAME)

    def testRelativeImports(self):
        to_import = STUB_LOC
        stub = import_file(to_import)
        self.assertEqual(stub.A_VAR, 123)

    def testAbsoluteImports(self):
        to_import = os.path.abspath(STUB_LOC)
        stub = import_file(to_import)
        self.assertEqual(stub.A_VAR, 123)

if __name__ == '__main__':
    unittest.main()

