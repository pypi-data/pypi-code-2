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

from pytilities.delegation import (
    profile_carrier, in_profile, DelegationAspect)
from pytilities.descriptors import AttributeDescriptor

@profile_carrier()
class A(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self._f = self._xw = None
        self._g = self._xr = False

    @in_profile("public")
    def f(self, a, b, c): # func with args
        self._f = (a, b , c)

    @in_profile()
    def g(self): # func withot args
        self._g = True

    @in_profile(modifiers='w') # only delegate write
    @property
    def x(self):
        self._xr = True

    @x.setter
    def x(self, value):
        self._xw = value

# default extends/includes public
profiles = A.attribute_profiles
profiles['default'] |= profiles['public']

# some beasty that delegates only public
class Public(object):
    def __init__(self, a):
        self.__a = a

delegation_aspect = DelegationAspect(AttributeDescriptor('_Public__a'),
     A.attribute_profiles['public'])
delegation_aspect.apply(Public)

# some beasty that delegates the default
class Default(object):
    def __init__(self, a):
        self.__a = a

    @property
    def x(self):
        return 666

delegation_aspect = DelegationAspect(AttributeDescriptor('_Default__a'),
     A.attribute_profiles['default'])
delegation_aspect.apply(Default)

class MainTestCase(unittest.TestCase):
    def test_public(self):
        a = A()
        p = Public(a)

        # public
        p.f(5, None, 3)
        self.assertEquals(a._f, (5, None, 3))
        a.reset()

        self.assertRaises(AttributeError, lambda: p.g)
        self.assertRaises(AttributeError, lambda: p.x)

        # default
        d = Default(a)
        d.f(5, None, 3)
        self.assertEquals(a._f, (5, None, 3))
        a.reset()

        d.g()
        self.assert_(a._g)
        a.reset()

        d.x = 2
        self.assertEquals(a._xw, 2)
        a.reset()

        self.assertEquals(d.x, 666)

