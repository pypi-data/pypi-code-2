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

from pytilities.delegation import mapped, mapped_class
from . import UnsupportedEventError

@mapped_class()
class DispatcherSwitch(object): # DispatcherChain may have been a better name

    """
    Provides a single interface to multiple event dispatchers.

    Events are switched to the the first event dispatcher in a list of
    dispatchers that supports the event, the other dispatchers are ignored for
    that particular event.
    
    This is also how remove_handlers will look for
    handlers, it will only remove the handlers of each event's first found
    dispatcher; the other ones are 'hidden' by this one, for this event.

    Check `Dispatcher` for the documentation of the methods that are left
    undocumented here.

    Instance methods:

        - `append_dispatchers`: Add dispatchers to the list of dispatchers
        - ...
    """

    public_mapping = {}

    def __init__(self):
        self.__dispatchers = []

    def append_dispatchers(self, *dispatchers):
        """
        Add dispatchers to the end of the list of dispatchers.

        Parameters:

            dispatchers :: (Dispatcher...)
                sequence of dispatchers to append
        """
        self.__dispatchers.extend(dispatchers)

    def __get_dispatcher_for_event(self, event_name):
        """
        Get the dispatcher for the given event according to our switching
        rules
        """
        for dispatcher in self.__dispatchers:
            if dispatcher.has_event(event_name):
                return dispatcher
        else:
            raise UnsupportedEventError(event_name)

    @mapped(public_mapping)
    def add_handler(self, event_name, handler, owner = None):
        dispatcher = self.__get_dispatcher_for_event(event_name)
        dispatcher.add_handler(event_name, handler, owner)

    @mapped(public_mapping)
    def remove_handlers(self, event_name=None, owner=None):
        # Run through our supported events, remove all handlers for each
        # supported event on the first dispatcher that supports it
        if event_name:
            dispatcher = self.__get_dispatcher_for_event(event_name)
            dispatcher.remove_handlers(event_name, owner)
        else:
            for event in self.events:
                dispatcher = self.__get_dispatcher_for_event(event)
                dispatcher.remove_handlers(event, owner)

    @mapped(public_mapping)
    def remove_handler(self, event_name, handler, owner = None):
        dispatcher = self.__get_dispatcher_for_event(event_name)
        dispatcher.remove_handler(event_name, handler, owner)

    @mapped(public_mapping)
    def event(self, event_name, owner=None):
        def decorator(handler):
            self.add_handler(event_name, handler, owner)
            return handler

        return decorator

    @mapped(public_mapping)
    def has_event(self, event_name):
        for dispatcher in self.__dispatchers:
            if dispatcher.has_event(event_name):
                return True
        else:
            return False

    @mapped(public_mapping)
    @property
    def events(self):
        events = set()
        events.update(*(d.events for d in self.__dispatchers))
        return events

    def dispatch(self, event_name, *args, **keyword_args):
        dispatcher = self.__get_dispatcher_for_event(event_name)
        dispatcher.dispatch(event_name, *args, **keyword_args)


