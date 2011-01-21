# DjangoDE, a integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import unittest

from djangode.data.autocomplete import AutoCompleter
from djangode.data.autocomplete.builtins import builtins
from djangode.data.autocomplete._class import Instance
from djangode.data.autocomplete.function import Function

class TestAutoCompleter(unittest.TestCase):
    def setUp(self):
        self.autocomplete = AutoCompleter()

    def testParse(self):
        self.assert_(self.autocomplete.process("""
a = 1
""") is not None)

    def testAssignInt(self):
        module = self.autocomplete.process("""
a = 1
""")

        var = module.get_variable("a")
        self.assert_(len(var.type) == 1)
        type = var.type.pop()
        self.assert_(isinstance(type, Instance))
        self.assert_(type.parent_scope is builtins.get_variable("int"))

    def testAssignString(self):
        module = self.autocomplete.process("""
a = 'a'
""")

        var = module.get_variable("a")
        self.assert_(len(var.type) == 1)
        type = var.type.pop()
        self.assert_(isinstance(type, Instance))
        self.assert_(type.parent_scope is builtins.get_variable("str"))

    def testGetStringAttributes(self):
        module = self.autocomplete.process("""
a = 'a'
""")

        var = module.get_variable("a")
        attrs = var.get_attributes()

        self.assert_(len(attrs) > 0)

        lower_func = [attr for attr in attrs if isinstance(attr, Function) and attr.name == "lower"]
        self.assert_(len(lower_func) == 1)
