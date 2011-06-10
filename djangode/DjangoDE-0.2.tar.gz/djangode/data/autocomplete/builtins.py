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

from djangode.data.autocomplete.namespace import Namespace

class Builtins(Namespace):
    def __init__(self):
        Namespace.__init__(self, None)

builtins = Builtins()

from djangode.data.autocomplete._class import Class
from djangode.data.autocomplete.function import Function
from djangode.data.autocomplete.value import Value

type_class = Class(builtins, "type", type=True)
type_class.type = set([type_class])
builtins.set_variable("type", Value(type_class))

func_type = Class(builtins, "callable", type=type_class)
func_type.docstring = callable.__doc__
builtins.set_variable("callable", Value(func_type))

classobj_type = Class(builtins, "classobj", type=type_class)
builtins.set_variable("classobj", Value(classobj_type))

int_class = Class(builtins, "int", type=type_class)
int_class.docstring = int.__doc__
builtins.set_variable("int", Value(int_class))

string_class = Class(builtins, "str", type=type_class)
string_class.docstring = str.__doc__
string_class.set_variable("lower", Value(Function(string_class, "lower")))
string_class.set_variable("upper", Value(Function(string_class, "upper")))
builtins.set_variable("str", Value(string_class))

tuple_class = Class(builtins, "tuple", type=type_class)
tuple_class.docstring = tuple.__doc__
builtins.set_variable("tuple", Value(tuple_class))
