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
from inspect import isclass

class _AspectAssociations(object):

    '''
    Remembers which object has which aspects applied to it

    Does not actually know how to apply/unapply things, it just remembers
    '''

    def __init__(self, on_apply, suppressor):
        self._on_apply = on_apply
        '''Called when trying to apply, gets all apply() args'''

        self._suppressor = suppressor

        self._applied_aspects = defaultdict(list)
        '''{obj: [aspect, ...]} ordered from first to last applied'''

        self._excluded_aspects = defaultdict(set)
        '''{obj: set(aspect, ...)} ordered from first to last applied'''

    def get_applied_aspects(self, obj):
        if not isclass(obj):
            cls = obj.__class__
            for aspect in self._get_applied_aspects_part(cls, obj):
                yield aspect

        for aspect in self._get_applied_aspects_part(obj, obj):
            yield aspect

    def _get_applied_aspects_part(self, advise_owner, obj):
        '''
        :return: iterable of aspects ordered from first applied to last applied
        '''
        if advise_owner in self._applied_aspects:
            return (aspect 
                    for aspect in self._applied_aspects[advise_owner] 
                    if not self._is_excluded(aspect, obj))
        return ()

    def unapply_all(self, obj):
        for aspect in tuple(self.get_applied_aspects(obj)):
            aspect.unapply(obj)

        if isclass(obj):
            for instance in self._get_instances(obj):
                self.unapply_all(instance)

    def is_applied(self, aspect, obj):
        return aspect in self.get_applied_aspects(obj)

    def _get_instances(self, cls):
        for obj in self._applied_aspects:
            if isinstance(obj, cls):
                yield obj

    def apply(self, aspect, obj, members):
        if self.is_applied(aspect, obj): return

        if self._is_excluded(aspect, obj):
            self._excluded_aspects[obj].discard(aspect)
        else:
            self._on_apply(aspect, obj, members)
            self._applied_aspects[obj].append(aspect)


    def unapply(self, aspect, obj):
        try: 
            self._applied_aspects[obj].remove(aspect)
            if isclass(obj):
                for instance, excludes in self._excluded_aspects.items():
                    if isinstance(instance, obj):
                        excludes.discard(aspect)
        except ValueError:
            if isclass(obj):
                for instance in self._get_instances(obj):
                    aspect.unapply(instance)
            elif self.is_applied(aspect, obj.__class__):
                self._excluded_aspects[obj].add(aspect)

    def get_advice(self, advised_instance, member_name, access, advised,
                     call_advised_function):

        applied_aspects = self.get_applied_aspects(advised_instance)
        next_advice = call_advised_function

        for aspect in applied_aspects:
            advice_function = aspect.get_advice(member_name, access,
                                                advised_instance)

            if self._should_execute(advice_function, aspect, advised_instance):
                next_advice = _Advice(
                    advised_instance, member_name, advised, 
                    aspect, advice_function, next_advice, 
                    self._suppressor
                )

        if next_advice is call_advised_function:
            return None
        else:
            return next_advice

    def _should_execute(self, advice_function, aspect, obj):
        return (advice_function and 
                not self._suppressor.is_suppressed(aspect, obj))

    def _is_excluded(self, aspect, obj):
        return (obj in self._excluded_aspects and
                aspect in self._excluded_aspects[obj])

from ._advice import _Advice
 
