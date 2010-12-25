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

class Aspect(object):

    '''
    Handy base class for aspects.

    You don't have to use this base class for your aspects, but you'll probably
    find it helpful to do so.

    Aspects should adhere to this interface.

    Aspects can be applied at most once to the same object.
    '''

    def __init__(self):
        '''
        Create the aspect
        '''

        self.__disabled_objects = set()
        '''set of objects for which this advice is disabled'''

        self.__advice = defaultdict(list)
        '''
        All advice given by the aspect
        {member, advice: [most_inner_advice...most_outer_advice]}
        '''

        self.__members = set()
        '''
        set of all advised members
        '''

    def apply(self, obj):
        '''
        Apply the advice to the object
        
        If already applied, do nothing

        :param obj: the object to advise
        :type obj: class, instance or module
        '''
        advisor.apply(self, obj, self.__members)

    def unapply(self, obj):
        '''
        Unapply the advice to the object
        
        If advice wasn't applied, do nothing

        :param obj: the object to advise
        :type obj: class, instance or module
        '''
        advisor.unapply(self, obj)

    def is_applied(self, obj):
        '''
        Get if this aspect is currently applied to an object.

        :param obj: the object to advise
        :type obj: class, instance or module
        :return: True if advice is currently applied to `obj`, False otherwise
        '''
        return advisor.is_applied(self, obj)

    def is_enabled(self, obj):
        '''
        Get if this aspect is enabled for an object.

        An aspect can be applied to an object but currently be disabled.
        Disabled aspects should not be asked for advice on that `obj`.

        :param obj: the object to advise
        :type obj: class, instance or module
        :return: True if advice is currently enabled for `obj`, False otherwise
        '''
        return obj not in self.__disabled_objects

    def get_advice(self, member, access):
        '''
        Get iter of advice for `member` of `obj`.

        Internal function (its interface may change in the future).

        :param member: member name of the object
        :type member: str
        :param access: the type of access being done
        :type access: '__get__', '__set__', '__delete__' or '__call__'
        :return: advice funcs, the left is the first advice to give
            (i.e. the last advice given; the most outer advice)
        :rtype: iter([advice, generator]...)
        '''
        iterators = []

        if ('*', access) in self.__advice:
            iterators.append(reversed(self.__advice['*', access]))

        if (member, access) in self.__advice:
            iterators.append(reversed(self.__advice[member, access]))

        return chain(*iterators) # *outer .. *inner, mouter .. minner

    def _advise(self, *members, get = None, set_ = None, delete = None, call = None):
        '''
        Add advice to give.

        The order in which advise is given is important. Last added advise is
        called first. Put differently, added advise wraps previous advise of
        given members.

        A special member of '*' is allowed as well for advising classes with
        metaclass=AOPMeta. This applies the advice to any member of obj. This
        advice preceeds other advice (though instance * advice is still
        preceded by any class advice).

        * advice precedes all other advice.

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
        for member in members:
            self.__members.add(member)

            if get:
                self.__advice[member, '__get__'].append([get, None])

            if set_:
                self.__advice[member, '__set__'].append([set_, None])

            if delete:
                self.__advice[member, '__delete__'].append([delete, None])

            if call:
                self.__advice[member, '__call__'].append([call, None])

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
        assert self.is_applied(obj)
        self.__disabled_objects.add(obj)

    def enable(self, obj):
        '''
        Enable advice for given object

        Aspect must have been applied to object, before you can enable.

        If `obj` was already enabled, do nothing.

        :param obj: the object to advise
        :type obj: class, instance
        '''
        assert self.is_applied(obj)
        self.__disabled_objects.discard(obj)

