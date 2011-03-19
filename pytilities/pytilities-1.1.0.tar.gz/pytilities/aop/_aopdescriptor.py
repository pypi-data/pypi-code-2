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

from inspect import getmembers

from .advisor import advisor
from .functions import _wrapped_call

class _AOPDescriptor(object):

    '''
    Allows advice to be given to a descriptor or attribute.

    Follows advice rules as described by `Advisor`
    '''

    # Note on making yield arguments work. The self parameter of functions
    # should be included. In practice this means adding obj to the args of
    # get/set/del, passing direct __call__'s args straight through and wrapped
    # functions have their __self__ added as first arg, if there is no __self__
    # (staticmethod), nothing is added.

    def __init__(self, descriptor, name):
        '''
        Creates an AOPDescriptor

        :param descriptor: the descriptor that's being advised or None
        :type descriptor: descriptor
        :param name: name of the member where the descriptor resides
        :type name: string
        '''
        self.__descriptor = descriptor
        self.__name = name

    def __get_name(self, obj):
        if self.__name is None:
            for name, value in getmembers(obj):
                if value is self:
                    self.__name = name
                    break
            else:
                assert False, 'AOP descriptor should be in getmembers(obj)'

        return self.__name

    def __get__(self, obj, cls = None):
        if self.__descriptor:
            advised = lambda obj: self.__descriptor.__get__(obj, cls)
        else:
            advised = None

        retval = advisor.process_call(
            obj, self.__get_name(obj), 
            advised,
            'get', (obj,), {})

        # must wrap callables, to advice the call
        if hasattr(retval, '__call__'): 
            def g(*args, **kwargs):
                return _wrapped_call(obj, self.__get_name(obj), retval, args, kwargs)

            return g
        else:
            return retval

    def __set__(self, obj, value):
        if self.__descriptor:
            advised = self.__descriptor.__set__
        else:
            advised = None

        retval = advisor.process_call(
            obj, self.__get_name(obj), 
            advised,
            'set', (obj, value), {})
        assert retval is None, 'setter should return None'

    def __delete__(self, obj):
        if self.__descriptor:
            advised = self.__descriptor.__delete__
        else:
            advised = None

        retval = advisor.process_call(
            obj, self.__get_name(obj), 
            advised,
            'delete', (obj,), {})
        assert retval is None, 'deleter should return None'

