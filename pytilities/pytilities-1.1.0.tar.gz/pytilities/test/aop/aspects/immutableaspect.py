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
import pdb

from pytilities.aop import AOPMeta
from pytilities.aop.aspects import ImmutableAspect, ImmutableAttributeException

class ImmutableAspectTest(unittest.TestCase):
    def test_all(self):
        a = A()
        self.then_is_mutable(a)  # sanity check

        immutable_x = ImmutableAspect('x')
        immutable_x.apply(a)
        self.then_is_mutable(a, False)

    def then_is_mutable(self, obj, mutable=True):
        self.assertEquals(0, obj.x)
        self.assertEquals(0, obj.y)

        if mutable:
            obj.x = 1
            self.assertEquals(1, obj.x)
            obj.decrease_x_by_one()
            self.assertEquals(0, obj.x)
        else:
            with self.assertRaises(ImmutableAttributeException):
                obj.x = 1
            with self.assertRaises(ImmutableAttributeException):
                obj.decrease_x_by_one()

        # can still mutate other attributes
        obj.y = 1
        self.assertEquals(1, obj.y)

        # note it is okay to set x to its current value, this is not considered
        # a mutation
        obj.x = 0
        obj.y = 0

class A(object, metaclass=AOPMeta):

    def __init__(self):
        self.__x = 0
        self.__y = 0

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value

    def decrease_x_by_one(self):
        self.__x -= 1

