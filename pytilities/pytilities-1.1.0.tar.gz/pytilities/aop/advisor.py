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

import logging
from inspect import isclass

from pytilities.tests import is_public, is_special
from pytilities.functions import get_attr_value_or_none
from . import AOPException
from ._suppressor import _Suppressor
from ._aspectassociations import _AspectAssociations

_logger = logging.getLogger('pytilities.aop.advisor')

class Advisor(object):

    '''
    Manager of all aspects and advice
    '''

    def __init__(self):
        self.__attributes_unsupported_by_aopmeta = set('''
            __add__ __sub__ __mul__ __truediv__ __floordiv__ __mod__ 
            __divmod__ __pow__ __lshift__ __rshift__ __and__ __xor__ __or__
            __radd__ __rsub__ __rmul__ __rtruediv__ __rfloordiv__ 
            __rmod__ __rdivmod__ __rpow__ __rlshift__ __rrshift__ __rand__ 
            __rxor__ __ror__
            __iadd__ __isub__ __imul__ __itruediv__ __ifloordiv__ 
            __imod__ __idivmod__ __ipow__ __ilshift__ __irshift__ __iand__ 
            __ixor__ __ior__
            __neg__ __pos__ __abs__ __invert__
            __complex__ __int__ __float__ __round__
            __index__
            __len__ __getitem__ __setitem__ __delitem__ __iter__ __reversed__ 
            __contains__
            __del__ __repr__ __str__ __format__ __lt__ __le__ __eq__ __ne__
            __gt__ __ge__ __bool__'''.split())
        '''set of attribute names that cant be handled by AOPMeta'''
        # Note: they can't be handled as they looked up directly on the class
        # dict (for performance reasons), bypassing all that AOPMeta can do

        self.unadvisables = {'__class__', '__dict__', '__mro__', '__call__', 
                               '__closure__', '__code__', '__globals__', 
                               '__self__', '__hash__', '__doc__'}
        '''Names of attributes that cannot be advised'''

        self._suppressor = _Suppressor()

        self._aspect_associations = _AspectAssociations(self._on_apply,
                                                        self._suppressor)


    ###############################################
    # Applying/unapplying aspects

    def is_advisable(self, name):
        '''
        See if an attribute with name `name` is advisable.

        Advisable members have a public or special name and aren't part of the
        advisor.unadvisables collection
        '''
        return name not in self.unadvisables and (is_public(name) or
                                                  is_special(name))

    def get_applied_aspects(self, obj):
        '''
        Get aspects applied to `obj`

        When `obj` is a class, gets the aspects applied to all instances of
        that class.

        When `obj` is an instance gets the aspects applied to the instance
        (including aspects applied to all instances of its class)

        :param obj: an object
        :type obj: class or instance
        :return: iterable of aspects ordered from first applied to last applied
        '''
        return self._aspect_associations.get_applied_aspects(obj)

    def unapply_all(self, obj):
        '''
        Unapply all advice given to an object.

        If `obj` is a class, all its instances (and the class itself) have all
        their applied aspects, unapplied.

        If `obj` is an instance, all the aspects that were specifically applied
        to it (as opposed to all instances of its class), are unapplied.

        :param obj: an object
        :type obj: class or instance
        '''
        self._aspect_associations.unapply_all(obj)

    def is_applied(self, aspect, obj):
        ''' Internal function '''
        return self._aspect_associations.is_applied(aspect, obj)

    def apply(self, aspect, obj, members):
        ''' Internal function '''
        self._aspect_associations.apply(aspect, obj, members)

    def _on_apply(self, aspect, obj, members):
        self._raise_if_cannot_apply(aspect, obj, members)

        if isclass(obj):
            aspect.unapply(obj) #unapply instances

        if self._has_aopmeta_as_metaclass(obj):
             members = self._filter_attributes_supported_by_aopmeta(members)

        self.__place_descriptors(obj, members)

    def _filter_attributes_supported_by_aopmeta(self, members):
        '''
        Filter away the attributes supported by AOPMeta
        
        :type members: set of member names
        :return: filtered set
        '''
        if '*' in members:
            return self.__attributes_unsupported_by_aopmeta
        else:
            return members & self.__attributes_unsupported_by_aopmeta

    def _raise_if_cannot_apply(self, aspect, obj, members):
        for member in members:
            if not self.is_advisable(member):
                raise AOPException('Advising "%s" attribute not supported' %
                                   member)

        if '*' in members and not self._has_aopmeta_as_metaclass(obj):
            raise AOPException("Cannot apply * advice to objects that " +
                               "don't have AOPMeta as metaclass")

    def _has_aopmeta_as_metaclass(self, obj):
        '''
        :return: True if 
        '''
        return isinstance(obj.__class__, AOPMeta) or isinstance(obj, AOPMeta)

    def __place_descriptors(self, obj, members):
        '''places aop descriptors on given members of obj'''
        cls = obj if isclass(obj) else obj.__class__
        for member in members:
            value = get_attr_value_or_none(cls, member)
            if not self._is_aop_descriptor(value):
                setattr(cls, member, _AOPDescriptor(value, member))

    def _is_aop_descriptor(self, obj):
        return obj and isinstance(obj, _AOPDescriptor)

    def unapply(self, aspect, obj):
        self._aspect_associations.unapply(aspect, obj)


    #############################################
    # Processing calls

    def process_call(self, obj, member_name, call_advised_function, access, args, kwargs,
                     advised=None):
        '''
        Process a get/set/del/regular call to an attribute.

        Class and instance advice will be applied to the call.

        Internal function.

        :param obj: the object whose advice to use
        :type obj: class, instance
        :type member_name: str
        :param call_advised_function: function that executes the content of the
            advised attribute as it was before it was advised
        :type call_advised_function: callable
        :param access: the type of access being done
        :type access: 'get', 'set', 'delete' or 'call'
        :param args: positional args of the call. Must include the self param,
            if any
        :param kwargs: keyword args of the call
        :param advised: the content of the advised attribute as found in the
            __dict__. If None, value of `call_advised_function` is taken
        :type advised: callable
        :return: return value as specified by advice, ...
        '''
        if advised is None:
            advised = call_advised_function
        advice = self._aspect_associations.get_advice(
            obj, member_name, access, advised, call_advised_function)

        if advice:
            return advice.run(args, kwargs)
        else:
            return call_advised_function(*args, **kwargs)


advisor = Advisor() # singleton instance 
del Advisor

from .aopmeta import AOPMeta
from ._aopdescriptor import _AOPDescriptor

