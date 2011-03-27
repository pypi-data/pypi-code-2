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
from pytilities.dictionary import FunctionMap

class FunctionMapTest(unittest.TestCase):

    def setUp(self):
        def mapper(key):
            return 'a' + str(key)
        self.dict = FunctionMap(mapper)

    def test_it(self):
        self.then_get_works()
        self.then_is_immutable()
        self.then_keys_empty()

    def then_get_works(self):
        self.assertEqual('a1', self.dict[1])

    def then_is_immutable(self):
        with self.assertRaises(Exception):
            self.dict[5] = 'eek'

        with self.assertRaises(Exception):
            del self.dict[5]

        with self.assertRaises(Exception):
            self.dict.update({'hurr':'durr'})

    def then_keys_empty(self):
        self.assertEqual(set(), self.dict.keys())
