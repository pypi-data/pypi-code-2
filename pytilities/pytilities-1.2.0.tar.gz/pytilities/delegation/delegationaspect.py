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

from collections import Mapping
from pytilities.overloading import overloaded, Overload, Param
from pytilities.aop import Aspect
from pytilities import aop
from pytilities.dictionary import FunctionMap

class DelegationAspect(Aspect):

    '''
    Aspect that delegates access on the aspected to a target object

    The effect of this is that: `source_instance.attr` actually returns
    `target_instance.attr`, same goes for set, and del accesses.

    The object could be a class, or an instance.
    '''

    def _init_mappings(self, target, mappings, undefined_keys=False):
        '''
        Create a `DelegationAspect`.


        Mappings should be a mapping of (access, source_attribute_name) to
        target_attribute_name or None; where access can be 'get' for read, 
        'set' for write and 'delete' for delete access.

        :param target: Descriptor of instance to delegate to. It is passed the
            source instance on __get__.
        :type target: descriptor
        :param mappings: mapping of (access, source_attribute_name) to
            target_attribute_name or None
        :type mappings: Mapping
        :param undefined_keys: True, if `mappings` has undefined keys()
        :type undefined_keys: boolean
        '''
        Aspect.__init__(self)
        self._target_descriptor = target
        self._mappings = mappings

        self._access_to_advice = dict(
            zip(_aop_access, 
                (self._get_advice, self._set_advice, self._del_advice))
        )

        if undefined_keys:
            self._advice_mappings = FunctionMap(self._mapper)
            self._undefined_keys = True
        else:
            for access, attr in self._mappings:
                advice = self._access_to_advice[access]
                self._advice_mappings[access, attr] = advice

    def _mapper(self, key):
        access, attribute_name = key
        if access != 'call':
            advice = self._access_to_advice[access]
            if key in self._mappings:
                return advice
        return None

    def _init_attributes(self, target, attributes): 
        '''
        Create a `DelegationAspect`.

        :param target: Descriptor of instance to delegate to. It is passed the
            source instance on __get__.
        :type target: descriptor
        :param attributes: Names of attribute to delegate. Use '*' for all.
        :type attributes: iter(str, ...)
        '''
        if attributes == '*':
            def map_all(key):
                access, source_name = key
                return source_name
            mappings = FunctionMap(map_all)
            self._init_mappings(target, mappings, True)
        else:
            mappings = dict([
                ((access, attr), attr)
                for access in ('get', 'set', 'delete')
                for attr in attributes
            ])
            self._init_mappings(target, mappings)

    @overloaded((
        Overload(_init_mappings,
            Param("target"),
            Param("mappings", Mapping)),
        Overload(_init_attributes,
            Param("target"),
            Param("attributes"))))
    def __init__(self):
        """
        Create a `DelegationAspect`.

        Overloaded:
            - `__init_attributes`
            - `__init_profile`
        """ 
        # TODO: use this way of documenting overloaded beasties everywhere,
        # change the rst files to properly have them link around and such
        pass


    def _get_target(self, obj):
        return self._target_descriptor.__get__(obj, obj.__class__)

    def _get_advice(self):
        (obj,), _ = yield aop.arguments
        (name, _) = yield aop.advised_attribute
        target_attribute_name = self._mappings['get', name]
        yield aop.return_(getattr(self._get_target(obj), 
                                  target_attribute_name))

    def _set_advice(self):
        (obj, value), _ = yield aop.arguments
        (name, _) = yield aop.advised_attribute
        target_attribute_name = self._mappings['set', name]
        setattr(self._get_target(obj), target_attribute_name, value)

    def _del_advice(self):
        (obj,), _ = yield aop.arguments
        (name, _) = yield aop.advised_attribute
        target_attribute_name = self._mappings['delete', name]
        delattr(self._get_target(obj), target_attribute_name)

_delegation_access = 'rwd'
_aop_access = ('get', 'set', 'delete')

