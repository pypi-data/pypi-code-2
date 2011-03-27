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


class ManglingTestCase(unittest.TestCase):
    def test_class_params(self):
        class A(object): pass

        self.assertEquals(mangle(A, '_nochange'), '_nochange')
        self.assertEquals(mangle(A, '__nochange__'), '__nochange__')
        self.assertEquals(mangle(A, 'nochange'), 'nochange')
        self.assertEquals(mangle(A, '__change'), '_A__change')

    def test_instance_params(self):
        class A(object): pass
        a = A()

        self.assertEquals(mangle(a, '_nochange'), '_nochange')
        self.assertEquals(mangle(a, '__nochange__'), '__nochange__')
        self.assertEquals(mangle(a, 'nochange'), 'nochange')
        self.assertEquals(mangle(a, '__change'), '_A__change')

    def test_string_params(self):
        self.assertEquals(mangle('A', '_nochange'), '_nochange')
        self.assertEquals(mangle('A', '__nochange__'), '__nochange__')
        self.assertEquals(mangle('A', 'nochange'), 'nochange')
        self.assertEquals(mangle('A', '__change'), '_A__change')

    def test_crazy_class_names(self):
        class _A(object):
            __x = 2

        B = _A

        # sanity checks
        self.assertEqual(_A._A__x, 2)
        self.assertEqual(B._A__x, 2)

        # mangle checks
        self.assertEquals(mangle(_A, '__change'), '_A__change')
        self.assertEquals(mangle(B, '__change'), '_A__change')

