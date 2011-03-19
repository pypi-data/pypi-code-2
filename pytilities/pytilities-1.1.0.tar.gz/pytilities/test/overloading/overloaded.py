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

from pytilities.overloading import overloaded, Overload, Param
from pytilities.types import NumberType

class Storage(object):
    """Something with an x and y"""
    x = 1
    y = 1

class A(object):
    """Some class to test with"""

    def __init_xy(self, x, y):
        return "xy", self, x, y

    def __init_storage(self, storage):
        return "storage", self, storage

    @overloaded((
        Overload(__init_xy,
            Param("x", NumberType, default=0),
            Param("y", NumberType, default=0)),
        Overload(__init_storage,
            Param("storage"))))
    def say_ni(self):
        """docstring is docstring"""
        pass

    @overloaded((
        Overload(__init_xy,
            Param("x", NumberType),
            Param("y", NumberType, default=0)),
        Overload(__init_storage,
            Param("storage"))))
    def say_it(self):
        """docstring is docstring"""
        pass


class MethodTestCase(unittest.TestCase):
    '''Test overloading of a method'''
    def setUp(self):
        self.a = A()
        self.s = Storage()

    def test_doc(self):
        '''Test docstring is passed on'''
        self.assertEquals(A.say_ni.__doc__, """docstring is docstring""")

    def test_process_args(self):
        '''Test process_args'''
        args, func = self.a.say_ni.process_args(self.a, kwargs={'y':6})
        self.assertEquals((args, func.__name__),
                          ({'self': self.a, 'x': 0, 'y': 6}, '__init_xy'))

    def test_xy(self):
        """Calls that should end up at xy"""
        self.assertEquals(self.a.say_ni(), ("xy", self.a, 0, 0))
        self.assertEquals(self.a.say_ni(3), ("xy", self.a, 3, 0))
        self.assertEquals(self.a.say_ni(x=3), ("xy", self.a, 3, 0))
        self.assertEquals(self.a.say_ni(3, 6), ("xy", self.a, 3, 6))
        self.assertEquals(self.a.say_ni(x=3, y=6), ("xy", self.a, 3, 6))
        self.assertEquals(self.a.say_ni(y=6), ("xy", self.a, 0, 6))

    def test_storage(self):
        """Calls that should end up at storage"""
        self.assertEquals(self.a.say_ni(self.s), ("storage", self.a, self.s))

    def test_bad(self):
        """Calls that should cause assertion errors"""
        self.assertRaises(AssertionError, lambda: self.a.say_ni(0, self.s))

    def test_confusion(self):
        '''Test that keyword names are well taken into account'''
        # make sure it doesn't take it as an x param
        self.assertEquals(self.a.say_it(storage=6), ("storage", self.a, 6))
        # first overload should fail as not all params would be used 
        self.assertEquals(self.a.say_ni(storage=6), ("storage", self.a, 6))

def __init_xy(x, y):
    return "xy", x, y

def __init_storage(storage):
    return "storage", storage

@overloaded((
    Overload(__init_xy,
        Param("x", NumberType, default=0),
        Param("y", NumberType, default=0)),
    Overload(__init_storage,
        Param("storage"))),
    False)
def say_it(self):
    """docstring is docstring"""
    pass


class FunctionTestCase(unittest.TestCase):
    '''Test overloading of a function'''
    def setUp(self):
        self.s = Storage()

    def test_xy(self):
        """Calls that should end up at xy"""
        self.assertEquals(say_it(), ("xy", 0, 0))
        self.assertEquals(say_it(3), ("xy", 3, 0))
        self.assertEquals(say_it(x=3), ("xy", 3, 0))
        self.assertEquals(say_it(3, 6), ("xy", 3, 6))
        self.assertEquals(say_it(x=3, y=6), ("xy", 3, 6))
        self.assertEquals(say_it(y=6), ("xy", 0, 6))

    def test_storage(self):
        """Calls that should end up at storage"""
        self.assertEquals(say_it(self.s), ("storage", self.s))

    def test_bad(self):
        """Calls that should cause assertion errors"""
        self.assertRaises(AssertionError, lambda: say_it(0, self.s))

# TODO test matcher functions
