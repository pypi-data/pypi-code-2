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

from copy import copy

from djangode.data.autocomplete.builtins import builtins
from djangode.data.autocomplete.namespace import Namespace
from djangode.data.autocomplete.value import Value

class Class(Namespace):
    def __init__(self, module, name, type=None):
        Namespace.__init__(self, module)

        self.name = name
        self.type = set([builtins.get_variable("classobj").value]) if type is None else set([type])

    def call(self):
        return Value(Instance(self))

    def copy(self):
        c = Class(self.parent_scope, self.name)
        c.type = set(list(self.type))
        c.variables = copy(self.variables)
        return c

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "<Class %s>" % (self.name, )

class Instance(Namespace):
    def __init__(self, _class):
        Namespace.__init__(self, _class)

        self.type = set([_class])

    def get_attributes(self, nested=False):
        return Namespace.get_attributes(self, nested=nested) + self.parent_scope.get_attributes(nested=nested)

    def __eq__(self, other):
        return self.type == other.type

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "<Instance %s>" % (repr(self.parent_scope), )
