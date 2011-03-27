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

from .advisor import advisor
from . import AOPException

class Aspect(object):

    '''
    Base class for aspects

    Maps advice to members of a set of applied-to objects
    '''

    def __init__(self):
        self.__disabled_objects = set()
        '''set of objects for which this advice is disabled'''

        self._advice_mappings = {}
        '''
        Mappings of (access, attribute_name) to advice to give or None, where
        access is either 'get', 'set', 'delete' or 'call'.  Default value is 
        {}.

        Check `Advisor.is_advisable` for rules on valid `attribute_name`s
        '''

        self._undefined_keys = False
        '''
        Boolean that indicates whether or not advice mappings has a sensible
        result for keys(). Default is False.

        Some mappings do not support keys because their set of keys is infinite
        or hard to determine. (FunctionMap is an example of such Mappings)

        If set to True, the aspect can only be applied to objects with AOPMeta 
        as metaclass.
        '''

    def get_advice(self, attribute, access, obj):
        '''
        Get advice for `attribute` of `obj`.

        Internal function

        :param attribute: name of attribute to advise
        :type attribute: str
        :param access: the type of access being done
        :type access: 'get', 'set', 'delete' or 'call'
        :param obj: the object to advise
        :type obj: class, instance
        :return: advice func or None
        '''
        if not self.is_enabled(obj):
            return None

        try:
            return self._advice_mappings[access, attribute]
        except KeyError:
            return None


    ##################################################
    # What advice should be given to which attributes
    ##################################################

    @property
    def __advised_members(self):
        '''
        set of all advised members
        '''
        if self._undefined_keys:
            return '*'
        else:
            return set((attr_name for (access, attr_name) in
                        self._advice_mappings.keys()))


    ####################################################
    # To what objects is the aspect applied and enabled
    ####################################################

    def disable(self, obj):
        '''
        Disable advice for given object

        Aspect must have been applied to object, before you can disable.

        When this aspect is unapplied to the object, it is automatically
        reenabled.

        If `obj` was already disabled, do nothing.

        :param obj: the object to advise
        :type obj: class, instance
        '''
        if not self.is_applied(obj):
            raise AOPException('Cannot disable aspect for an unapplied object')

        self.__disabled_objects.add(obj)

    def enable(self, obj):
        '''
        Enable advice for given object

        Aspect must have been applied to object, before you can enable.

        If `obj` was already enabled, do nothing.

        :param obj: the object to advise
        :type obj: class, instance
        '''
        if not self.is_applied(obj):
            raise AOPException('Cannot enable aspect for an unapplied object')

        self.__disabled_objects.discard(obj)

    def apply(self, obj):
        '''
        Apply the advice to the object

        If already applied, do nothing

        When `obj` is a class, the advice is applied to all instances of that
        class (and the class itself, for staticmethods and such)

        Note: Advice given to a single instance always wraps/preceeds advice 
        given to all instances, no matter what the order of applying was

        :param obj: the object to advise. Cannot be a builtin object
        :type obj: class, instance
        '''
        # Note on note: it's probably no issue that advice order is different
        # when given to all instances of a class, than to a single instance.
        # Given what you normally do with it, order doesn't really matter
        advisor.apply(self, obj, self.__advised_members)

    def unapply(self, obj):
        '''
        Unapply the advice to the object
        
        If advice wasn't applied, do nothing

        When `obj` is a class, the aspect is unapplied to all instances of that
        class (and the class itself).

        :param obj: the object to advise
        :type obj: class, instance
        '''
        self.__disabled_objects.discard(obj)
        advisor.unapply(self, obj)

    def is_applied(self, obj):
        '''
        Get if this aspect is currently applied to an object.

        See `advisor.get_applied_aspects`

        :param obj: the object to advise
        :type obj: class, instance
        :return: True if aspect is in set of applied aspects of `obj`, False otherwise
        '''
        return advisor.is_applied(self, obj)

    def is_enabled(self, obj):
        '''
        Get if this aspect is enabled for an object.

        An aspect can be applied to an object but currently be disabled.
        Disabled aspects should not be asked for advice on that `obj`.

        :param obj: the object to advise
        :type obj: class, instance
        :return: True if advice is currently enabled for and applied to `obj`, 
            False otherwise
        '''
        return self.is_applied(obj) and obj not in self.__disabled_objects

