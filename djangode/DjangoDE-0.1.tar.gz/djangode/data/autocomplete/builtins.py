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

from djangode.data.autocomplete.namespace import Namespace

class Builtins(Namespace):
    def __init__(self):
        Namespace.__init__(self, None)

builtins = Builtins()

from djangode.data.autocomplete._class import Class
from djangode.data.autocomplete.function import Function

int_class = Class(builtins, "int")
int_class.docstring = int.__doc__
builtins.set_variable("int", int_class)

string_class = Class(builtins, "str")
string_class.docstring = str.__doc__
string_class.set_variable("lower", Function(string_class, "lower"))
string_class.set_variable("upper", Function(string_class, "upper"))
builtins.set_variable("str", string_class)
