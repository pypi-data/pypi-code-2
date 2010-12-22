#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from pydenji.userproperties.codescraper import get_getitem_accesses

class ArbitraryObject(object):
    def somefunc(self):
        return self.attr["somekey"]

    def otherfunc(self):
        p = self.attr["otherkey"]

class MemorizingAttrObject(object):
    def somefunc(self):
        some = self.attr
        return some["somekey"]

class TestCodescraper(unittest.TestCase):

    def test_get_getitem_accesses_returns_used_self_attr_keys(self):
        self.assertEquals(set(["somekey", "otherkey"]), get_getitem_accesses(ArbitraryObject(), "attr"))

    def test_get_getitem_accesses_returns_memorized_used_attr_keys(self):
        self.assertEquals(set(["somekey"]), get_getitem_accesses(MemorizingAttrObject(), "attr"))
        

if __name__ == '__main__':
    unittest.main()

