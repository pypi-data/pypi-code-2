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

class RestrictedDescriptor(object):

    '''
    A wrapper that hides a combination of set/get/del of a descriptor.
    '''

    def __init__(self, descriptor, get=True, set_=True, delete=True):
        '''
        Construct a RestrictedDescriptor.

        :param descriptor: The descriptor to restrict
        :param get: True to allow get access, False to restrict
        :type get: bool
        :param set_: True to allow set access, False to restrict
        :type set_: bool
        :param delete: True to allow delete access, False to restrict
        :type delete: bool
        '''
        self.__descriptor = descriptor
        self.__get = get
        self.__set = set_
        self.__delete = delete

    def __get__(self, obj, owner = None):
        if not self.__get:
            raise AttributeError()

        return self.__descriptor.__get__(obj, owner)

    def __set__(self, obj, value):
        if not self.__set:
            raise AttributeError()

        self.__descriptor.__set__(obj, value)

    def __delete__(self, obj):
        if not self.__delete:
            raise AttributeError()

        self.__descriptor.__delete__(obj)




