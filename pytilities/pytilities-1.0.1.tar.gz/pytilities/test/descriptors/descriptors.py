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

from pytilities.descriptors import (
    BoundDescriptor, AttributeDescriptor,
    DereferencedDescriptor)

class A(object):
    def __init__(self):
        self.__x = 4
        self.y = 2

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

class DescriptorsTest(unittest.TestCase):
    def setUp(self):
        self.a = A()

    def test_attrib_wrapping(self):
        'test adapting an attribute to a descriptor'
        # Note: this one will fail, if BoundProp doesn't work
        ad = AttributeDescriptor('y')
        a2 = A()

        class B(object):
            v = BoundDescriptor(ad, self.a)
            w = BoundDescriptor(ad, a2)

        b = B()

        self.assertEquals(b.v, 2) # get works?
        self.assertEquals(b.v, b.w) # get works?
        b.v = 3
        self.assertEquals(self.a.y, 3) # set works?
        self.assertEquals(a2.y, 2) # set doesn't affect other a?
        a2.y = 5
        self.assertEquals(a2.y, 5) # get really really works?

    def test_bound_descriptors(self):
        'test bound descriptors'
        class B(object):
            def __init__(s):
                s.target = self.a
                s.prop = A.x

            v = BoundDescriptor(A.x, self.a)

            w = BoundDescriptor(A.x, AttributeDescriptor('target'))

            x = BoundDescriptor(
                    DereferencedDescriptor(
                        BoundDescriptor(
                            AttributeDescriptor('x'), 
                            A)),
                    AttributeDescriptor('target'))

            y = BoundDescriptor(AttributeDescriptor('prop'),
                                AttributeDescriptor('target'),
                               True)

        # v
        b = B()
        self.assertEquals(b.v, 4) # get works?
        b.v = 5
        self.assertEquals(b.v, 5) # set works?
        self.assertEquals(self.a.x, 5) # set works?

        # w
        self.assertEquals(b.w, 5) # get works?
        a2 = A()
        b.target = a2
        self.assertEquals(b.w, 4) # target change works?

        # x
        self.assertEquals(b.x, 4) # get works?

        # y
        self.assertEquals(b.y, 4) # get works?

    def test_regular_dereferencing(self):
        '''test DereferencedDescriptor'''
        # depends on attribute descriptors
        class B(object):
            def __init__(self):
                self._y = 4

            @property
            def y(self):
                return self._y

            @y.setter
            def y(self, value):
                self._y = value

            @property
            def x(self):
                return B.y
            
        B.v = DereferencedDescriptor(B.x)

        b = B()
        self.assertEquals(b.v, 4) # get works?
        b.v = 3
        self.assertEquals(b.v, 3) # set works?

    #def test_all_together(self):
    #    'test all descriptor combinations on an actual class'
        # TODO: 
        # - test an attrib, method, prop, operator. do so for both atd and 
        #   regular instance binding
        # - also include testing inheritance

