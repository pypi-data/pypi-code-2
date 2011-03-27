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

from pytilities.types import NumberType, NumericType, SequenceType
from pytilities.infinity import infinity

class MainTest(unittest.TestCase):
    def test_number_type(self):
        self.assert_(isinstance(1, NumberType))
        self.assert_(isinstance(1.0, NumberType))
        self.assertFalse(isinstance('1.0', NumberType))
        self.assertFalse(isinstance('1', NumberType))
        self.assert_(isinstance(infinity, NumberType))
        self.assert_(isinstance(-infinity, NumberType))
        self.assert_(issubclass(int, NumberType))
        self.assert_(issubclass(float, NumberType))
        self.assertFalse(issubclass(str, NumberType))
        self.assert_(issubclass(infinity.__class__, NumberType))
        self.assert_(issubclass((-infinity).__class__, NumberType))

    def test_numeric_type(self):
        self.assert_(isinstance(1, NumericType))
        self.assert_(isinstance(1.0, NumericType))
        self.assert_(isinstance('1.0', NumericType))
        self.assert_(isinstance('1', NumericType))
        self.assert_(isinstance(infinity, NumberType))
        self.assert_(isinstance(-infinity, NumberType))
        self.assert_(issubclass(int, NumericType))
        self.assert_(issubclass(float, NumericType))
        self.assertFalse(issubclass(str, NumericType))
        self.assert_(issubclass(infinity.__class__, NumberType))
        self.assert_(issubclass((-infinity).__class__, NumberType))

    def test_sequence_type(self):
        self.assert_(isinstance((), SequenceType))
        self.assert_(isinstance([], SequenceType))
        self.assertFalse(isinstance({}, SequenceType))
        self.assert_(issubclass(tuple, SequenceType))
        self.assert_(issubclass(list, SequenceType))
        self.assertFalse(issubclass(set, SequenceType))
        self.assertFalse(issubclass(dict, SequenceType))

