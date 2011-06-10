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

import copy

from djangode.data.autocomplete.variable import Variable

class Value(object):
    def __init__(self, type=None):
        if isinstance(type, list) or isinstance(type, set):
            types = []
            for t in type:
                types.extend(t.type if isinstance(t, Value) else [t])
        elif isinstance(type, Value):
            types = type.type
        elif type is None:
            types = []
        else:
            types = [type]

        for type in types:
            assert not isinstance(type, Variable)
            assert not isinstance(type, Value)

        self.type = set(types)

    def call(self):
        #TODO: Raise a warning if not all types can be called
        types = [t.call() for t in self.type if hasattr(t, "call")]
        if len(types) == 0:
            raise ValueError, "No types can be called (%s)." % (self.type)
        return Value(types)

    def copy(self):
        return Value(copy.copy(self.type))

    def is_instance_of(self, class_):
        return len([t for t in self.type if class_ in t.type]) > 0

    def get_attributes(self, nested=True):
        attrs = []
        for type in self.type:
            attrs.extend(type.get_attributes(nested=nested))
        return sorted(attrs, key=lambda a: a.name)

    def merge(self, other):
        new_types = copy.copy(self.type)
        for t1 in other.type:
            for t2 in self.type:
                if t1 != t2:
                    new_types.add(t1)
        self.type = new_types

    def __unicode__(self):
        return repr(self)
    def __repr__(self):
        return "<Value %s>" % (self.type, )
