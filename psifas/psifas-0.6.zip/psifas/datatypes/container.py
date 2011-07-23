# Copyright 2010 Oren Zomer <oren.zomer@gmail.com>
#
# This file is part of pypsifas.

# pypsifas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pypsifas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pypsifas.  If not, see <http://www.gnu.org/licenses/>.

from datatypes.abstract import BottomClass, Default, Bottom
from imerge import imerge_unwrapped
from datatypes.deque import deque
from recursion_lock import recursion_lock

class Container(BottomClass):
    bottom_hierarchy = 3
    
    def __init__(self, *args, **kw):
        self.__dict__['_Container__fields_order'] = deque()
        super(Container, self).__init__()
        for name, value in args:
            setattr(self, name, value)
        for name, value in sorted(kw.iteritems()):
            setattr(self, name, value)

    def __setattr__(self, name, value):
        if not self.__dict__.has_key(name):
            self.__fields_order.append(name)
        super(Container, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in self.__fields_order:
            self.__fields_order.remove(name)
        super(Container, self).__delattr__(name)

    @recursion_lock(lambda self, other: (self, False))
    def imerge(self, other):
        if not isinstance(other, Container):
            return super(Container, self).imerge(other)
        if self is other:
            return self, False
        change_flag = False
        for field in other.__fields_order:
            sub_value, sub_flag = imerge_unwrapped(getattr(self, field, Bottom),
                                                   getattr(other, field))
            if sub_flag:
                setattr(self, field, sub_value)
                change_flag = True
        return self, change_flag

    def iter_fields(self):
        order = self.__fields_order
        for field in order:
            yield field, getattr(self, field)

    @recursion_lock(lambda self, other: True)
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Container):
            return super(Container, self) == other
        sorted_fields = sorted(self.__fields_order)
        if sorted_fields != sorted(other.__fields_order):
            return False
        return all(getattr(self, field) == getattr(other, field) for field in sorted_fields)

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join({False: '%s = %r', True: '%s = %s'}[isinstance(value, Container)] % (name, value)
                           for name, value in self.iter_fields() if not name.startswith('_')))

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join('%s = %r' % (name, value) for (name, value) in self.iter_fields() if not name.startswith('__')))

class DefaultContainer(Container):
    def __getattr__(self, name):
        return getattr(super(DefaultContainer, self), name, Default)
