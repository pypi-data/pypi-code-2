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

from djangode.data.autocomplete.builtins import builtins
from djangode.data.autocomplete.namespace import Namespace
from djangode.data.autocomplete.value import Value

class Function(Namespace):
    def __init__(self, parent_scope, name, tl=None):
        Namespace.__init__(self, parent_scope)

        self.name = name
        self.type = set(builtins.get_variable("callable").value.type)
        self.tl = tl

    def call(self):
        return Value()
