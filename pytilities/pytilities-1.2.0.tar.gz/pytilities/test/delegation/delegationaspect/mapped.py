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

from .testbase import TestBase

class MappedDelegationTestCase(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self.when_wrap(with_={
            ('get', 'y'):'x',
            ('set', 'y'):'x',
            ('delete', 'y'):'x',
            ('get', 'g'):'f',
            ('set', 'g'):'f',
            ('delete', 'g'):'f'
        })

    def test_get_delegation(self):
        self.then_get_works()

    def test_set_delegation(self):
        self.then_set_works()

    def test_delete_delegation(self):
        self.then_delete_works()

    def when_get_property(self):
        self.wrapper.y

    def when_get_function(self):
        self.wrapper.g()

    def when_set(self):
        self.wrapper.y = 1

    def when_delete(self):
        del self.wrapper.y
