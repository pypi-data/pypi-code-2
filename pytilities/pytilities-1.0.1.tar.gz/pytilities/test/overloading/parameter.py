# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

__docformat__ = 'reStructuredText'

import unittest

# TODO: write more unit tests for the new functionality, same for Composite
from pytilities.overloading import Param

class CtorTestCase(unittest.TestCase):
    def test_ctor(self):
        """Test success and fail cases"""
        p = Param("mir")

        Param("mir", int)
        Param("mir", default=0)
        Param("mir", int, 0)
        Param("mir", int, default=0)
        Param("mir", type_=int, default=0)

        self.assertRaises(AssertionError, Param, "")
        self.assertRaises(AssertionError, Param, None)
        self.assertRaises(AssertionError, Param, "mir", int, default="frr")
        self.assertRaises(AssertionError, Param, "mir", int, 0, default=5)

class ArgPresentTestCase(unittest.TestCase):
    def setUp(self):
        self.kwargs = {"mir":3, "muff":8}

    def test_name(self):
        p = Param("mir")
        self.assert_(p.read_kwargs(self.kwargs))

        d = {}
        p.write(d)
        self.assertEquals(d, {"mir": 3})

    def test_type(self):
        p = Param("mir", int)
        self.assert_(p.read_kwargs(self.kwargs))

        d = {}
        p.write(d)
        self.assertEquals(d, {"mir": 3})

        self.assertFalse(p.read_kwargs({"mir": "stingstring"}))

    def test_default(self):
        p = Param("mir", default=0)
        self.assert_(p.read_kwargs(self.kwargs))

        d = {}
        p.write(d)
        self.assertEquals(d, {"mir": 3})

    def test_type_with_default(self):
        p = Param("mir", int, 0)
        self.assert_(p.read_kwargs(self.kwargs))

        d = {}
        p.write(d)
        self.assertEquals(d, {"mir": 3})

        self.assertFalse(p.read_kwargs({"mir": "stingstring"}))

class ArgMissingTestCase(unittest.TestCase):
    def setUp(self):
        self.kwargs = {"muff": 8}

    def test_name(self):
        p = Param("mir")
        self.assertFalse(p.read_kwargs(self.kwargs))

    def test_type(self):
        p = Param("mir", int)
        self.assertFalse(p.read_kwargs(self.kwargs))

    def test_default(self):
        p = Param("mir", default=0)
        self.assert_(p.read_kwargs(self.kwargs))

        d = {}
        p.write(d)
        self.assertEquals(d, {"mir": 0})

    def test_type_with_default(self):
        p = Param("mir", int, 0)
        self.assert_(p.read_kwargs(self.kwargs))

        d = {}
        p.write(d)
        self.assertEquals(d, {"mir": 0})

        self.assertFalse(p.read_kwargs({"mir": "stingstring"}))

