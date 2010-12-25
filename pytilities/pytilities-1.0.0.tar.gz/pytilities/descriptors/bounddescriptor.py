# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

__docformat__ = 'reStructuredText'

class BoundDescriptor(object):

    '''
    A descriptor with an object bound to it.

    It's like bound methods, but more general.

    Instead of using the passed obj, it will use its stored obj as instance for
    the descriptor.
    '''

    def __init__(self, descriptor, instance, special_dereference = False):
        '''
        Construct a BoundDescriptor.

        :param descriptor: The descriptor to bind to
        :type descriptor: descriptor
        :param instance: The instance to bind to. OR a descriptor with get
        access that returns the instance that will be bound to it. This is
        evaluated on each call.
        :type instance: any or descriptor
        :param special_dereference: If True, descriptor is dereferenced
        with obj param first, and then its return is bound to `instance`, this
        dereference happens on every call. See DereferencedDescriptor for an
        explanation of 'dereference'.
        '''
        self.__descriptor = descriptor
        self.__instance = instance
        self.__special_dereference = special_dereference

    def __get_instance(self, obj):
        if hasattr(self.__instance, '__get__'):
            return self.__instance.__get__(obj)
        else:
            return self.__instance

    def __get_descriptor(self, obj):
        if self.__special_dereference:
            return self.__descriptor.__get__(obj)
        else:
            return self.__descriptor

    def __get__(self, obj, objtype = None):
        return self.__get_descriptor(obj).__get__(
            self.__get_instance(obj), objtype)

    def __set__(self, obj, value):
        self.__get_descriptor(obj).__set__(self.__get_instance(obj), value)

    def __delete__(self, obj):
        self.__get_descriptor(obj).__delete__(self.__get_instance(obj))


