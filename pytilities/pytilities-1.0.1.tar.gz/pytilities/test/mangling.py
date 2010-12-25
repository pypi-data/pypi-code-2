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

from pytilities import mangle

class A(object):
    __x = 1

class _A(object):
    __x = 2

class __A(object):
    __x = 3

B = __A

class ManglingTestCase(unittest.TestCase):
    def test_mangle(self):
        self.assertEquals(mangle(A, '_nochange'), '_nochange')
        self.assertEquals(mangle(A, '__nochange__'), '__nochange__')
        self.assertEquals(mangle(A, 'nochange'), 'nochange')
        self.assertEquals(mangle(A, '__change'), '_A__change')

        # test instanceness
        a = A()
        self.assertEquals(mangle(a, '_nochange'), '_nochange')
        self.assertEquals(mangle(a, '__nochange__'), '__nochange__')
        self.assertEquals(mangle(a, 'nochange'), 'nochange')
        self.assertEquals(mangle(a, '__change'), '_A__change')

        # test with strings
        self.assertEquals(mangle('A', '_nochange'), '_nochange')
        self.assertEquals(mangle('A', '__nochange__'), '__nochange__')
        self.assertEquals(mangle('A', 'nochange'), 'nochange')
        self.assertEquals(mangle('A', '__change'), '_A__change')

        # test more special class names
        # make sure this is how python works
        self.assertEquals(A._A__x, 1)
        self.assertEquals(_A._A__x, 2)
        self.assertEquals(B._A__x, 3)
        # now see if our mangle does it to
        self.assertEquals(mangle(_A, '__change'), '_A__change')
        self.assertEquals(mangle(B, '__change'), '_A__change')

