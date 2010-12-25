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

class AttributeDescriptor(object):

    '''
    A wrapper that makes an attribute look like a descriptor.

    The descriptor supports all access (get, set, del).
    '''

    def __init__(self, attr_name):
        '''
        Construct an AttributeDescriptor.

        :param attr_name: Name of the attribute to get, cannot contain any
        dots. No mangling is done.
        :type attr_name: string
        '''
        self.__attr_name = attr_name

    def __get__(self, obj, objtype = None):
        return getattr(obj, self.__attr_name)

    def __set__(self, obj, value):
        setattr(obj, self.__attr_name, value)

    def __delete__(self, obj):
        delattr(obj, self.__attr_name)


