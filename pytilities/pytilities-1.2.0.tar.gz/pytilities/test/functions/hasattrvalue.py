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

from .functiontestcase import FunctionTestCase
from pytilities.functions import has_attr_value

class HasAttrValueTestCase(FunctionTestCase):

    def test_found(self):
        self.assertEqual(True, has_attr_value(self.A, 'confuss'))

    def test_not_found(self):
        self.assertEqual(False, has_attr_value(self.A, 'x'))
