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

from pytilities.descriptors import AttributeDescriptor
from .descriptortestbase import DescriptorTestBase

class AttributeDescriptorTest(DescriptorTestBase):

    def test_all(self):
        self.when_use_descriptor(AttributeDescriptor('_x'))

        self.assertEqual(1, self.holder.x)

        self.holder.x = 2
        self.assertEqual(2, self.holder.x)

        del self.holder.x
        self.assertFalse(hasattr(self.holder, '_x'))

    def when_use_descriptor(self, descriptor):
        DescriptorTestBase.when_use_descriptor(self, descriptor)
        self.holder._x = 1
