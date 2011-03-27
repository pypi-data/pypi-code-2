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
from pytilities.delegation import mapped_class, mapped

class MappedTestCase(unittest.TestCase):

    def setUp(self):
        @mapped_class
        class A(object):
            public = {}
            protected = {}

            def __init__(self):
                self.reset()

            def reset(self):
                self._f = self._xw = None
                self._g = self._xr = False

            @mapped(public)
            def f(self, a, b, c): # func with args
                self._f = (a, b , c)

            @mapped(protected)
            def g(self): # func withot args
                self._g = True

            @mapped(protected, 'get', 'call')
            @mapped(public, 'set')
            @property
            def x(self):
                self._xr = True

            @x.setter
            def x(self, value):
                self._xw = value

        A.protected.update(A.public)
        self.A = A

    def test_it(self):
        expectedPublic = {
            ('get', 'f'):'f',
            ('set', 'f'):'f',
            ('delete', 'f'):'f',
            ('set', 'x'):'x'
        }
        self.assertEqual(expectedPublic, self.A.public)

        expectedProtected = {
            ('get', 'f'):'f',
            ('set', 'f'):'f',
            ('delete', 'f'):'f',
            ('get', 'g'):'g',
            ('set', 'g'):'g',
            ('delete', 'g'):'g',
            ('get', 'x'):'x',
            ('call', 'x'):'x',
            ('set', 'x'):'x'
        }
        self.assertEqual(expectedProtected, self.A.protected)

