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

from unittest import TestCase

from pytilities.descriptors import BoundDescriptor
from pytilities.geometry import (
    DiscreteVector, Vector, ImmutableVector, verbose_vector_aspect)
from pytilities.aop.aspects import ImmutableAttributeException

class VectorTestCase(TestCase):
    def setUp(self):
        self.p = Vector(0, 5)
        self.p2 = Vector(2.0, 5.0)

    def test_get_xy(self):
        # V(0, 5)
        self.assertEqual(self.p.x, 0)
        self.assertEqual(self.p.y, 5)
        self.assertEqual(self.p.xy, (0, 5))

    def test_set_x(self):
        self.p.x = 2
        self.assertEqual(self.p.xy, (2, 5))

    def test_set_y(self):
        self.p.y = 4
        self.assertEqual(self.p.xy, (0, 4))

    def test_move_to(self):
        self.p.move_to(4, 7)
        self.assertEqual(self.p.xy, (4, 7))

    def test_move_by(self):
        self.p.move_by(-1, 2)
        self.assertEqual(self.p.xy, (-1, 7))
        
    def test_immutable_operators(self):
        # p = Vector(0, 5)
        p2 = Vector(2.0, 5.0)

        v = -self.p
        self.assert_(isinstance(v, Vector))
        self.assertEqual(v.xy, (0, -5))

        v = self.p + p2
        self.assert_(isinstance(v, Vector))
        self.assertEqual(v.xy, (2, 10))

        v = self.p - p2
        self.assert_(isinstance(v, Vector))
        self.assertEqual(v.xy, (-2, 0))

        v = self.p * 2
        self.assert_(isinstance(v, Vector))
        self.assertEqual(v.xy, (0, 10))

        v = self.p / 2
        self.assert_(isinstance(v, Vector))
        self.assertEqual(v.xy, (0, 2.5))

        v = p2 / 2
        self.assert_(isinstance(v, Vector))
        self.assertEqual(v.xy, (1, 2.5))

    def test_iadd(self):
        self.p += self.p2
        self.assertEqual(self.p.xy, (2, 10))

    def test_isub(self):
        self.p -= self.p2
        self.assertEqual(self.p.xy, (-2, 0))

    def test_imul(self):
        self.p *= 2
        self.assertEqual(self.p.xy, (0, 10))

    def test_itruediv(self):
        self.p /= 2
        self.assertEqual(self.p.xy, (0, 2.5))

    def test_ifloordiv(self):
        self.p //= 2
        self.assertEqual(self.p.xy, (0, 2))

    def test_copy(self):
        clone = self.p.copy()
        self.assertIsNot(self.p, clone)
        self.assertTrue(isinstance(clone, Vector))
        self.assertEqual(clone.xy, self.p.xy)
        self.assertEqual(clone, self.p)

    def test_assign(self):
        v = Vector(2, 7)
        self.p.assign(v)
        self.assertEqual(self.p.xy, (2, 7))
        self.p.assign(1, 6)
        self.assertEqual(self.p.xy, (1, 6))

    def test_comparison(self):
        p3 = self.p.copy()
        self.assert_(self.p == p3)
        self.assertFalse(self.p != p3)
        self.assertFalse(self.p == self.p2)
        self.assert_(self.p != self.p2)

# BoundVector test helper
class VHolder(object):
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

    def __init__(self):
        self.__x = 0
        self.__y = 5
        x = BoundDescriptor(VHolder.x, self)
        y = BoundDescriptor(VHolder.y, self)
        self.p = Vector(x, y)
                        

# Bound vectors should support the same things as regular vectors
class BoundVectorTestCase(VectorTestCase):
    def setUp(self):
        VectorTestCase.setUp(self)

        self.vholder = VHolder()
        self.p = self.vholder.p

    def test_boundness(self):
        # V(0, 5)
        self.p.x = 3
        self.assertEqual(self.p.xy, (3, 5))
        self.assertEqual(self.vholder.x, 3)
        
# test whether 2 bound vectors don't affect each other (this once happened)
class DoubleBoundVectorTestCase(TestCase):
    def test_double_bound_vector(self):
        a = VHolder()
        b = VHolder()

        self.assertFalse(a.p is b.p)
        self.assertEquals(a.p.xy, (0, 5))
        self.assertEquals(b.p.xy, (0, 5))

        b.p.y = 3
        self.assertEquals(a.p.xy, (0, 5))
        self.assertEquals(b.p.xy, (0, 3))

        b.p.assign(Vector(3, 8))
        self.assertEquals(a.p.xy, (0, 5))
        self.assertEquals(b.p.xy, (3, 8))


class ImmutableVectorTestCase(VectorTestCase):

    def setUp(self):
        VectorTestCase.setUp(self)
        self.p = ImmutableVector(self.p)

    def test_set_x(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_set_x(self)

    def test_set_y(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_set_y(self)

    def test_move_to(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_move_to(self)

    def test_move_by(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_move_by(self)
        
    def test_iadd(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_iadd(self)

    def test_isub(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_isub(self)

    def test_imul(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_imul(self)

    def test_itruediv(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_itruediv(self)

    def test_ifloordiv(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_ifloordiv(self)

    def test_assign(self):
        with self.assertRaises(ImmutableAttributeException):
            VectorTestCase.test_assign(self)

class VerboseHelper(object):
    def __init__(self, v):
        v.add_handler('changed', self.on_changed)
        self.__got_event = None

    def on_changed(self, old):
        self.__got_event = old

    @property
    def last(self):
        last = self.__got_event
        self.__got_event = None
        return last

class VerboseVectorTestCase(VectorTestCase):
    def setUp(self):
        # p = Vector(0, 5)
        VectorTestCase.setUp(self)
        verbose_vector_aspect.apply(self.p)
        self.h = VerboseHelper(self.p)

    def test_event(self):
        'test for change events'
        self.p.x = 3
        self.assertEquals(self.h.last, (0, 5))
        self.p.x = 3
        self.assertEquals(self.h.last, None)

class DiscreteVectorTestCase(TestCase):
    def setUp(self):
        self.p = DiscreteVector(0, 5)
        self.p2 = DiscreteVector(2, 5)

    def test_get_xy(self):
        # V(0, 5)
        self.assertEqual(self.p.x, 0)
        self.assertEqual(self.p.y, 5)
        self.assertEqual(self.p.xy, (0, 5))

    def test_set_x(self):
        self.p.x = 2
        self.assertEqual(self.p.xy, (2, 5))

    def test_set_y(self):
        self.p.y = 4
        self.assertEqual(self.p.xy, (0, 4))

    def test_move_to(self):
        self.p.move_to(4, 7)
        self.assertEqual(self.p.xy, (4, 7))

    def test_move_by(self):
        self.p.move_by(-1, 2)
        self.assertEqual(self.p.xy, (-1, 7))
        
    def test_immutable_operators(self):
        # V(0, 5)
        p2 = DiscreteVector(2, 5)

        v = -self.p
        self.assert_(isinstance(v, DiscreteVector))
        self.assertEqual(v.xy, (0, -5))

        v = self.p + p2
        self.assert_(isinstance(v, DiscreteVector))
        self.assertEqual(v.xy, (2, 10))

        v = self.p - p2
        self.assert_(isinstance(v, DiscreteVector))
        self.assertEqual(v.xy, (-2, 0))

        v = self.p * 2
        self.assert_(isinstance(v, DiscreteVector))
        self.assertEqual(v.xy, (0, 10))

        v = self.p // 2
        self.assert_(isinstance(v, DiscreteVector))
        self.assertEqual(v.xy, (0, 2))

        v = p2 // 2
        self.assert_(isinstance(v, DiscreteVector))
        self.assertEqual(v.xy, (1, 2))

    def test_iadd(self):
        # V(0, 5)
        self.p += self.p2
        self.assertEqual(self.p.xy, (2, 10))

    def test_isub(self):
        self.p -= self.p2
        self.assertEqual(self.p.xy, (-2, 0))

    def test_imul(self):
        self.p *= 2
        self.assertEqual(self.p.xy, (0, 10))

    def test_ifloordiv(self):
        self.p //= 2
        self.assertEqual(self.p.xy, (0, 2))

    def test_copy(self):
        clone = self.p.copy()
        self.assert_(self.p is not clone)
        self.assert_(isinstance(clone, DiscreteVector))
        self.assertEqual(clone.xy, self.p.xy)
        self.assertEqual(clone, self.p)

    def test_assign(self):
        v = Vector(2, 7)
        self.p.assign(v)
        self.assertEqual(self.p.xy, (2, 7))

    def test_heterogene_ops(self):
        '''test DiscreteVector op Vector, and vice versa'''
        # V(0, 5)
        p2 = Vector(2.0, 2.5)

        v = self.p + p2
        self.assert_(isinstance(v, Vector))
        self.assertEquals(v.xy, (2, 7.5))

        v = p2 + self.p
        self.assert_(isinstance(v, Vector))
        self.assertEquals(v.xy, (2, 7.5))

        v = self.p - p2
        self.assert_(isinstance(v, Vector))
        self.assertEquals(v.xy, (-2, 2.5))

        v = p2 - self.p
        self.assert_(isinstance(v, Vector))
        self.assertEquals(v.xy, (2, -2.5))

    def test_comparison(self):
        p3 = self.p.copy()
        self.assert_(self.p == p3)
        self.assertFalse(self.p != p3)
        self.assertFalse(self.p == self.p2)
        self.assert_(self.p != self.p2)

