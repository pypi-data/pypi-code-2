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

class VerboseRectangleAspect(Aspect):
    
    '''
    Aspect that learns a vector to send out change events.
    '''

    def __init__(self):
        Aspect.__init__(self)

        # advice to dispatch when needed
        self._advise('*', call=self.watch_size, set_=self.watch_size)

    def apply(self, obj):
        if not self.is_applied(obj):
            dispatcher = Dispatcher()
            dispatcher.register_events('size_changed')
            get_annotations(obj)['dispatcher'] = dispatcher

            # make it look dispatchy
            delegation_aspect.apply(obj)

            # continue to apply our advice
            Aspect.apply(self, obj)

    # advice to send change events with
    def watch_size(self): 
        r = yield aop.advised_instance
        old_size = r.size.copy()
        yield aop.proceed
        if old_size != r.size:
            dispatcher = get_annotations(r)['dispatcher']
            dispatcher.dispatch("size_changed", old_size)

delegation_aspect = DelegationAspect(
    property(lambda s: get_annotations(s)['dispatcher']),
    Dispatcher.attribute_profiles['public'])

verbose_rectangle_aspect = VerboseRectangleAspect()
del VerboseRectangleAspect

