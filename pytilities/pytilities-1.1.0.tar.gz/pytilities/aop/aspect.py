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

from collections import defaultdict
from itertools import chain

from .advisor import advisor
from . import AOPException
import pdb

class Aspect(object):

    '''
    Base class for aspects

    Maps advice to members of a set of applied-to objects
    '''

    def __init__(self):
        self.__disabled_objects = set()
        '''set of objects for which this advice is disabled'''

        self.__advice = defaultdict(dict)
        '''
        All advice given by the aspect
        {access : {member: advice}}
        '''

    @property
    def __members(self):
        '''
        set of all advised members
        '''
        return (self.__advice['get'].keys() 
              | self.__advice['set'].keys()
              | self.__advice['delete'].keys()
              | self.__advice['call'].keys())


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
        advisor.apply(self, obj, self.__members)

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

    def get_advice(self, member, access, obj):
        '''
        Get advice for `member` of `obj`.

        Internal function (its interface may change in the future).

        :param member: member name of the object
        :type member: str
        :param access: the type of access being done
        :type access: 'get', 'set', 'delete' or 'call'
        :param obj: the object to advise
        :type obj: class, instance
        :return: advice func or None
        '''
        if not self.is_enabled(obj):
            return None

        advices = self.__advice[access]
        if '*' in advices:
            return advices['*']
        elif member in advices:
            return advices[member]
        else: 
            return None

    def _advise(self, *members, get = None, set_ = None, delete = None, call = None):
        '''
        Associate advice to given members

        You cannot advise the same member twice for the same type of access, 
        this implies that you cannot give advise to the special '*' member 
        and a regular member at the same for the same type of access.

        A special member of '*' is allowed for advising classes with
        metaclass=AOPMeta. This applies the advice to any member the applied
        object may have. 

        Check `Advisor.is_advisable` for further rules on what can be advised.

        :param members: names of members to which to give advice
        :type members: str, ...
        :param get: around advice given to get calls
        :type get: parameterless callable that returns a generator
        :param set_: around advice given to set calls
        :type set_: parameterless callable that returns a generator
        :param delete: around advice given to del calls
        :type delete: parameterless callable that returns a generator
        :param call: around advice given to __call__ calls
        :type call: parameterless callable that returns a generator
        '''
        self.__assert_no_conflicts(set(members), get, set_, delete, call)
        for member in members:
            if get:
                self.__advice['get'][member] = get
            if set_:
                self.__advice['set'][member] = set_
            if delete:
                self.__advice['delete'][member] = delete
            if call:
                self.__advice['call'][member] = call

    def __assert_no_conflicts(self, members, get, set_, delete, call):
        '''
        :param members: set of member names
        '''
        if get:
            self.__assert_no_conflicting_members(members, self.__advice['get'])
        if set_:
            self.__assert_no_conflicting_members(members, self.__advice['set'])
        if delete:
            self.__assert_no_conflicting_members(members, self.__advice['delete'])
        if call:
            self.__assert_no_conflicting_members(members, self.__advice['call'])

    def __assert_no_conflicting_members(self, new_members, current_members):
        current_members = current_members.keys()
        future_members = new_members | current_members
        if '*' in future_members and len(future_members) > 1:
            raise AOPException("Aspect can't advise '*' and other members " +
                               "at the same time, for the same type of access")

        common_members = new_members & current_members
        if common_members:
            raise AOPException('Tried to advise the same member twice, this ' +
                               'is not supported by Aspect')

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

