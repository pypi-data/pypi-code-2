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

from pytilities.descriptors import DereferencedBoundDescriptor
from .descriptortestbase import DescriptorTestBase

class DereferencedBoundDescriptorTest(DescriptorTestBase):

    def test_all(self):
        self.when_use_descriptor(DereferencedBoundDescriptor(
            property(lambda s: s.xprop2), 
            property(lambda s: s.a2)))
        self.then_binding_should_work(self.a)

    def when_use_descriptor(self, descriptor):
        DescriptorTestBase.when_use_descriptor(self, descriptor)
        self.holder.xprop2 = self.xprop
        self.holder.a2 = self.a





