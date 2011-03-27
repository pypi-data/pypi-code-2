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

from pytilities.descriptors import RestrictedDescriptor
from .descriptortestbase import DescriptorTestBase

class RestrictedDescriptorTest(DescriptorTestBase):

    def test_all(self):
        for get in True, False:
            for set_ in True, False:
                for delete in True, False:
                    self._test_restricted(get, set_, delete)

    def _test_restricted(self, get, set_, delete):
        self.when_use_descriptor(
            RestrictedDescriptor(self.xprop, get, set_, delete)
        )

        if get:
            self.then_get_works(self.holder)
        else:
            with self.assertRaises(AttributeError):
                self.when_get()

        if set_:
            self.then_set_works(self.holder)
        else:
            with self.assertRaises(AttributeError):
                self.when_set()

        if delete:
            self.then_delete_works(self.holder)
        else:
            with self.assertRaises(AttributeError):
                self.when_delete()

