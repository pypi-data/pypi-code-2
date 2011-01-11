import sys

import os.path

from . import remove_caches
from io import StringIO
from os.path import (dirname, abspath)
from unittest import TestCase
from test import support

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
from tenpy import cache
from hashlib import sha1


class TenpyCacheTest(TestCase):

    def setUp(self):
        self.dir = dirname(abspath(__file__))
        remove_caches()

    def tearDown(self):
        self.setUp()

    def test_cachename(self):
        self.assertEqual(cache.cachename("prefix1"),
                "prefix1da39a3ee5e6b4b0d3255bfef95601890afd80709")
        self.assertEqual(cache.cachename("prefix1", "seed1", "seed2"),
                "prefix19ba517dfb98c5a69943c0f41e745c39bfc9718fa")

    def test_codecache(self):
        codecache = cache.CodeCache()
        self.assertEqual(codecache.cachename("funcname"),
                "__tenpy_func_1cf28e7ccb3e89bc5519bfd7011f87093f0b0893")

    def test_nullcodecache(self):
        codecache = cache.NullCodeCache()
        codecache["key1"] = "value1"
        with self.assertRaises(KeyError):
            codecache["key1"]

    def test_pagecache(self):
        pagecache = cache.PageCache()
        keyfile = os.path.join(self.dir, "key1.html")
        pagecache[keyfile] = "value1"
        self.assertTrue(os.path.isfile(os.path.join(self.dir,
            "__tenpy_page_key1.html34e5b897e1ca7d0da65ad441f6584ae0342b9d80")))
        self.assertEqual(pagecache[keyfile], "value1")
        with self.assertRaises(KeyError):
            pagecache["nothing"]

    def test_nullpagecache(self):
        pagecache = cache.NullPageCache()
        pagecache["key1"] = "value1"
        with self.assertRaises(KeyError):
            pagecache["key1"]


def test_main():
    support.run_unittest(TenpyCacheTest)

if __name__ == "__main__":
    test_main()
