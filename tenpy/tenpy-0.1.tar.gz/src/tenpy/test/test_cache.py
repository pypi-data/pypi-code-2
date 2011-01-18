import sys

from os.path import (dirname, abspath)
from unittest import TestCase
from test import support

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
from tenpy import cache


class TenpyCacheTest(TestCase):

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


def test_main():
    support.run_unittest(TenpyCacheTest)

if __name__ == "__main__":
    test_main()
