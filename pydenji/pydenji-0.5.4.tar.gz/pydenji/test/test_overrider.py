#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

import unittest

from pydenji.userproperties.overrider import override_with

class Obj(object):
    pass

class OverridenConfig(object):
    def myobj(self):
        myobj = Obj()
        myobj.property1 = 123
        return myobj

class TestPropertyOverrider(unittest.TestCase):
    def test_property_overriding(self):
        config = override_with(["[myobj]", "property1=456"])(OverridenConfig)()
        self.assertEquals(456, config.myobj().property1)


