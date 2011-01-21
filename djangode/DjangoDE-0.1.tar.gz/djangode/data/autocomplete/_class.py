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

class Class(Namespace):
    def __init__(self, module, name):
        Namespace.__init__(self, module)

        self.name = name

    def get_instance(self):
        return Instance(self)

    def __repr__(self):
        return "<Class %s>" % (self.name, )

class Instance(Namespace):
    def __init__(self, _class):
        Namespace.__init__(self, _class)

    def get_attributes(self):
        return Namespace.get_attributes(self) + self.parent_scope.get_attributes()

    def __repr__(self):
        return "<Instance %s>" % (repr(self.parent_scope), )
