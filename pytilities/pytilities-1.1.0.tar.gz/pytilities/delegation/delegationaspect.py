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

from pytilities.overloading import overloaded, Overload, Param
from pytilities.aop import Aspect
from pytilities import aop

from .profile import Profile

class DelegationAspect(Aspect):

    '''
    Aspect that delegates calls from the aspected to a target object

    The effect of this is that: `source_instance.attr` actually returns
    `target_instance.attr`, same goes for set, and del calls.

    The object could be a class, or an instance.
    '''

    def __init_profile(self, target, profile):
        '''
        Create a `DelegationAspect`.

        :param target: Descriptor of instance to delegate to. It is passed the
        source instance on __get__.
        :type target: descriptor
        :param profile: attribute profile of what attributes to delegate
        :type profile: Profile
        '''
        Aspect.__init__(self)
        self.__target_descriptor = target
        self._advise(*profile.readables, get=self.__get_advice)
        self._advise(*profile.writables, set_=self.__set_advice)
        self._advise(*profile.deletables, delete=self.__del_advice)

    def __init_attributes(self, target, attributes): 
        '''
        Create a `DelegationAspect`.

        :param target: Descriptor of instance to delegate to. It is passed the
        source instance on __get__.
        :type target: descriptor
        :param attributes: Names of attribute to delegate. Use '*' for all.
        :type attributes: iter(str, ...)
        '''
        Aspect.__init__(self)
        self.__target_descriptor = target
        self._advise(*attributes, get=self.__get_advice, set_=self.__set_advice,
                     delete=self.__del_advice)

    @overloaded((
        Overload(__init_profile,
            Param("target"),
            Param("profile", Profile)),
        Overload(__init_attributes,
            Param("target"),
            Param("attributes"))))
    def __init__(self):
        """
        Create a `DelegationAspect`.

        Overloaded:
            - `__init_attributes`
            - `__init_profile`
        """ 
        # TODO: if this way of documenting overloads works, use it everywhere
        pass


    def __get_target(self, obj):
        return self.__target_descriptor.__get__(obj, obj.__class__)

    def __get_advice(self):
        (obj,), kwargs = yield aop.arguments
        (name, _) = yield aop.advised_attribute
        yield aop.return_(getattr(self.__get_target(obj), name))

    def __set_advice(self):
        (obj, value), kwargs = yield aop.arguments
        (name, _) = yield aop.advised_attribute
        setattr(self.__get_target(obj), name, value)

    def __del_advice(self):
        (obj,), kwargs = yield aop.arguments
        (name, _) = yield aop.advised_attribute
        delattr(self.__get_target(obj), name)

