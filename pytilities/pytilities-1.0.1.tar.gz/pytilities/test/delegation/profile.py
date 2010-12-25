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

from pytilities.delegation import Profile

class MainTestCase(unittest.TestCase):
    def test_public(self):
        # these should conflict
        a = Profile()
        b = Profile()
        a.add_mappings('rw', *'a b c'.split(), d='d')
        b.add_mappings('rw', *'a b'.split(), d='e')

        # care about conflict
        self.assertRaises(AssertionError, lambda: a | b)
        self.assertRaises(AssertionError, lambda: a & b)

        # don't care, shouldn't raise
        c = a - b
        c = a ^ b

        # these shouldn't conflict either
        a = Profile()
        b = Profile()
        a.add_mappings('rw', 'a', c='d')
        a.add_mappings('w', 'b')
        b.add_mappings('rw', 'a', d='e')
        b.add_mappings('r', 'b')

        c = a | b
        self.assert_(c.has_readable('a'))
        self.assert_(c.has_readable('b'))
        self.assert_(c.has_readable('c'))
        self.assert_(c.has_readable('d'))
        self.assert_(c.has_writable('a'))
        self.assert_(c.has_writable('b'))
        self.assert_(c.has_writable('c'))
        self.assert_(c.has_writable('d'))

        c = a & b
        self.assert_(c.has_readable('a'))
        self.assert_(c.has_writable('a'))

        c = a - b
        self.assert_(c.has_readable('c'))
        self.assert_(c.has_writable('b'))
        self.assert_(c.has_writable('c'))

        c = a ^ b
        self.assert_(c.has_readable('b'))
        self.assert_(c.has_readable('c'))
        self.assert_(c.has_readable('d'))
        self.assert_(c.has_writable('b'))
        self.assert_(c.has_writable('c'))
        self.assert_(c.has_writable('d'))

        # check for existance of other operators
        c = a.copy()
        c |= b

        c = a.copy()
        c &= b

        c = a.copy()
        c -= b

        c = a.copy()
        c ^= b

