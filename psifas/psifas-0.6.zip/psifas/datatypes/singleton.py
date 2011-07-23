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

class _singleton_metaclass(type):
    def __new__(mcs, name, bases, namespace):
        """
        instead of returning the new type, it returns a new instance of the new type.
        """
        return type.__new__(mcs, name, bases, namespace)()

class _singleton_main_metaclass(type):
    def __new__(mcs, name, bases, namespace):
        """
        The subclasses of this class will use _singleton_metaclass
        """
        return type.__new__(_singleton_metaclass, name, bases, namespace)

class Singleton(object):
    __metaclass__ = _singleton_main_metaclass

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__,)

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        """
        makes it pickleable
        """
        return self.__class__.__name__
