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

class DereferencedBoundDescriptor(object):

    '''
    A descriptor with an object bound to it.

    It's like bound methods, but more general (supports all descriptors rather
    than just functions).
    '''

    def __init__(self, descriptor, instance):
        '''
        :param descriptor: A descriptor that returns the descriptor to bind to. 
            This is evaluated on each call.
        :type descriptor: descriptor with __get__
        :param instance: A descriptor that returns the instance that will be 
            bound. This is evaluated on each call.
        :type instance: descriptor with __get__
        '''
        self.__descriptor = descriptor
        self.__instance = instance

    def __get_instance(self, obj):
        return self.__instance.__get__(obj)

    def __get_descriptor(self, obj):
        return self.__descriptor.__get__(obj)

    def __get__(self, obj, objtype = None):
        return self.__get_descriptor(obj).__get__(
            self.__get_instance(obj), objtype)

    def __set__(self, obj, value):
        self.__get_descriptor(obj).__set__(self.__get_instance(obj), value)

    def __delete__(self, obj):
        self.__get_descriptor(obj).__delete__(self.__get_instance(obj))


