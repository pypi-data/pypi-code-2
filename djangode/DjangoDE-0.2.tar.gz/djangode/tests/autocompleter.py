# DjangoDE, an integrated development environment for Django
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
from djangode.data.autocomplete.module import Module

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

        var = module.get_variable("a").value
        self.assert_(len(var.type) == 1)
        type = var.type.pop()
        self.assert_(isinstance(type, Instance), type)
        self.assert_(type.parent_scope.name == builtins.get_variable("int").value.type.pop().name, (type.parent_scope, builtins.get_variable("int").value))

    def testAssignString(self):
        module = self.autocomplete.process("""
a = 'a'
""")

        var = module.get_variable("a").value
        self.assert_(len(var.type) == 1)
        type = var.type.pop()
        self.assert_(isinstance(type, Instance))
        self.assert_(type.parent_scope.name == builtins.get_variable("str").value.type.pop().name, (type.parent_scope, builtins.get_variable("str").value))

    def testGetStringAttributes(self):
        module = self.autocomplete.process("""
a = 'a'
""")

        var = module.get_variable("a").value
        attrs = var.get_attributes(nested=False)

        self.assert_(len(attrs) > 0)

        lower_func = [attr for attr in attrs if attr.value.is_instance_of(builtins.get_variable("callable").value.type.pop()) and attr.name == "lower"]
        self.assert_(len(lower_func) == 1, (attrs, lower_func))

    def testGetFunction(self):
        module = self.autocomplete.process("""
def double(x):
    return x * 2
""")

        func = module.get_variable("double").value

        self.assert_(len(func.type) == 1)
        self.assert_(isinstance(func.type.pop(), Function))

    def testImportStmt(self):
        module = self.autocomplete.process("""
import django
""")

        module = module.get_variable("django").value

        self.assert_(len(module.type) == 1)
        self.assert_(isinstance(module.type.pop(), Module))

    def testImportAsStmt(self):
        module = self.autocomplete.process("""
import django as dj
""")

        self.assertRaises(KeyError, module.get_variable, "django")

        module = module.get_variable("dj").value

        self.assert_(len(module.type) == 1)
        self.assert_(isinstance(module.type.pop(), Module))

    def testGetTopLevelModules(self):
        modules = self.autocomplete.get_top_level_modules()
        
        self.assert_("django" in modules)
        
    def testGetDjangoModule(self):
        module = self.autocomplete.get_module("django")
        
        self.assert_(isinstance(module, Module))
        self.assert_(module.filename.endswith("django/__init__.py"), module.filename)
        
    def testGetDjangoSubModules(self):
        module = self.autocomplete.get_module("django")
        submodules = module.get_submodules("c") # Should return at least django.contrib
        
        self.assert_(submodules is not None)
        self.assert_(len(submodules) > 0)

    def testGetDjangoContribSubModule(self):
        module = self.autocomplete.get_module("django")
        submodule = module.get_submodule("contrib")
        
        self.assert_(isinstance(module, Module))
