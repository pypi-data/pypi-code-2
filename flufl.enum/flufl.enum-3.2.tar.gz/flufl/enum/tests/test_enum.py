# Copyright (C) 2011 Barry A. Warsaw
#
# This file is part of flufl.enum.
#
# flufl.enum is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# flufl.enum is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with flufl.enum.  If not, see <http://www.gnu.org/licenses/>.

"""Additional package tests."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'TestEnum',
    ]


import unittest
import warnings

from flufl.enum import Enum, make_enum



class TestEnum(unittest.TestCase):
    """Additional unit tests."""

    def test_deprecations(self):
        # Enum.enumclass and Enum.enumname are deprecated.
        class Animals(Enum):
            ant = 1
            bee = 2
            cat = 3
        with warnings.catch_warnings(record=True) as seen:
            # Cause all warnings to always be triggered.
            warnings.simplefilter('always')
            Animals.ant.enumclass
        self.assertEqual(len(seen), 1)
        self.assertTrue(issubclass(seen[0].category, DeprecationWarning))
        self.assertEqual(seen[0].message.message,
                         '.enumclass is deprecated; use .enum instead')
        with warnings.catch_warnings(record=True) as seen:
            # Cause all warnings to always be triggered.
            warnings.simplefilter('always')
            Animals.ant.enumname
        self.assertEqual(len(seen), 1)
        self.assertTrue(issubclass(seen[0].category, DeprecationWarning))
        self.assertEqual(seen[0].message.message,
                         '.enumname is deprecated; use .name instead')

    def test_make_enum_identifiers_bug_803570(self):
        # Bug LP: #803570 describes that make_enum() allows non-identifiers as
        # enum value names.
        try:
            make_enum('Foo', '1 2 3')
        except ValueError as exc:
            self.assertEqual(exc.message, 'non-identifiers: 1 2 3')
        else:
            raise AssertionError('Expected a ValueError')
