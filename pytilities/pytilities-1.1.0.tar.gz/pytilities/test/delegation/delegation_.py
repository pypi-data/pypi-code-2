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

from pytilities.delegation import DelegationAspect

class Nothing(object):
    def __init__(self, wrapped):
        self._wrapped = wrapped

class Something(object):
    def get_self(self):
        return self

delegation_aspect = DelegationAspect(property(lambda s: s._wrapped),
                                     ('get_self',))
delegation_aspect.apply(Nothing)

class DelegationTestCase(unittest.TestCase):

    def setUp(self):
        self.something = Something()
        self.assertIs(self.something, self.something.get_self())

    def test_single_delegation(self):
        wrapper = Nothing(self.something)
        self.assertIs(self.something, wrapper.get_self())

    def test_dual_delegation(self):
        wrapper = Nothing(self.something)
        self.assertIs(self.something, wrapper.get_self())

