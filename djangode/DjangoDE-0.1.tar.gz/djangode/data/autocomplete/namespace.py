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

class Namespace(object):
    def __init__(self, parent_scope):
        self.parent_scope = parent_scope

        self.variables = {}

    def set_variable(self, name, value):
        if name in self.variables:
            self.variables[name].type = self.variables[name].type | value.type
        else:
            self.variables[name] = value

        return self.variables[name]

    def get_variable(self, name):
        try:
            return self.variables[name]
        except KeyError:
            if self.parent_scope is not None:
                return self.parent.get_variable(name)
            else:
                raise

    def get_attributes(self):
        return self.variables.values()
