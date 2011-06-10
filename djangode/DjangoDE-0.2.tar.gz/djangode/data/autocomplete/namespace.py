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

from djangode.data.autocomplete.variable import Variable

class Namespace(object):
    def __init__(self, parent_scope):
        self.parent_scope = parent_scope

        self.variables = {}

    def set_variable(self, name, value):
        assert hasattr(value, "type") and isinstance(value.type, set), value

        if name in self.variables:
            self.variables[name].value.merge(value)
        else:
            self.variables[name] = Variable(name, value)

        return self.variables[name].copy()

    def get_variable(self, name):
        try:
            return self.variables[name].copy()
        except KeyError:
            if self.parent_scope is not None:
                return self.parent_scope.get_variable(name)
            else:
                raise

    def get_attributes(self, prefix="", nested=True):
        attrs = [self.variables[name] for name in self.variables.keys() if name.startswith(prefix)]
        if nested:
            attrs.extend(self.parent_scope.get_attributes(prefix) if self.parent_scope is not None else [])
        return attrs
