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

from pytilities import aop, get_annotations
from pytilities.event import Dispatcher
from pytilities.aop import Aspect
from pytilities.delegation import DelegationAspect
from pytilities.dictionary import FunctionMap

class VerboseVectorAspect(Aspect):
    
    '''
    Aspect that learns a vector to send out change events.
    '''

    def __init__(self):
        Aspect.__init__(self)

        # advice to dispatch when needed
        self._advice_mappings = FunctionMap(self._mapper)
        self._undefined_keys = True

    def _mapper(self, key):
        access, attribute_name = key
        if access in ('call', 'set'):
            return self.watch_xy
        else:
            return None

    def apply(self, obj):
        if not self.is_applied(obj):
            # enough, might clash too easily
            dispatcher = Dispatcher()
            dispatcher.register_events('changed')
            get_annotations(obj)['dispatcher'] = dispatcher

            # make it look dispatchy
            delegation_aspect.apply(obj)

            # continue to apply our advice
            Aspect.apply(self, obj)

    # advice to send change events with
    def watch_xy(self): 
        v = yield aop.advised_instance
        old_tuple = v.xy
        yield aop.proceed
        if old_tuple != v.xy:
            dispatcher = get_annotations(v)['dispatcher']
            dispatcher.dispatch("changed", old_tuple)

delegation_aspect = DelegationAspect(
    property(lambda s: get_annotations(s)['dispatcher']),
    Dispatcher.public_mapping)

verbose_vector_aspect = VerboseVectorAspect()
del VerboseVectorAspect

