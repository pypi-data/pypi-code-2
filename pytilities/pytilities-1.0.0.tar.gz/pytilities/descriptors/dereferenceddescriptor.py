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

class DereferencedDescriptor(object):

    '''
    A descriptor that 'dereferences' another descriptor.

    The wrapped descriptor is supposed to describe another descriptor. The
    wrapper will pretend to be that more inner descriptor.

    For each call, wrapped_descriptor is getted with the given obj, and its
    return is used to perform the get, set, del on.
    '''

    def __init__(self, descriptor):
        '''
        Construct a DereferencedDescriptor.

        :param descriptor: The descriptor that will be dereferenced
        :type descriptor: descriptor
        '''
        self.__descriptor = descriptor

    def __get_inner_descriptor(self, obj):
        return self.__descriptor.__get__(obj)

    def __get__(self, obj, objtype = None):
        return self.__get_inner_descriptor(obj).__get__(obj, objtype)

    def __set__(self, obj, value):
        inner =self.__get_inner_descriptor(obj)
        inner.__set__(obj, value)

    def __delete__(self, obj):
        self.__get_inner_descriptor(obj).__delete__(obj)


