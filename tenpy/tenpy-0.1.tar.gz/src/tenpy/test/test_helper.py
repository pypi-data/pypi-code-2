import sys

import os.path

from os.path import (dirname, abspath)
from unittest import TestCase
from test import support

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
from tenpy.helper import *


class TenpyHelperTest(TestCase):

    def test_include_raises(self):
        with self.assertRaises(IOError):
            include("testfile")

    def test_include(self):
        filename = "/path/to/test/file"
        r = include("testfile")
        self.assertEqual(r.filename, "/path/to/test/testfile")


def test_main():
    support.run_unittest(TenpyHelperTest)

if __name__ == "__main__":
    test_main()
