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

from . import UnsupportedEventError

# Note: could have done this with an aspect as well
class RestrictedDispatcher(object):

    """
    A restricted view of a `Dispatcher`
    
    The list of supported events is filtered.

    Check `Dispatcher` for the documentation of the methods that are left
    undocumented here.
    """

    def __init__(self, dispatcher, allow = None, disallow = None):
        """
        Construct a restricted dispatcher.

        `disallow` and `allow` are mutually exclusive.

        Parameters:

            dispatcher :: Dispatcher
                the dispatcher to wrap around

            allow :: iter(string...):
                events that are allowed through

            disallow :: iter(string...)
                events that are hidden/blocked
        """

        assert dispatcher, "dispatcher musn't be None"
        assert not (allow and disallow), \
                'disallow and allow are mutually exclusive'

        self.__dispatcher = dispatcher
        self.__allowed_events = set(allow or disallow or ())
        self.__complement = not allow
        '''True, if allowed_events contains the complement of allowed events'''

    def add_handler(self, event_name, handler, owner = None):
        if not self.has_event(event_name):
            raise UnsupportedEventError(event_name)

        self.__dispatcher.add_handler(event_name, handler, owner)

    def remove_handlers(self, event_name=None, owner=None):
        # pass on the call, making sure we don't remove handlers for events we
        # don't support
        if event_name:
            if not self.has_event(event_name):
                raise UnsupportedEventError(event_name)

            self.__dispatcher.remove_handlers(event_name, owner)
        else:
            for event in self.events:
                self.__dispatcher.remove_handlers(event, owner)

    def remove_handler(self, event_name, handler, owner = None):
        if not self.has_event(event_name):
            raise UnsupportedEventError(event_name)

        self.__dispatcher.remove_handler(event_name, handler, owner)

    def dispatch(self, event_name, *args, **keyword_args):
        if not self.has_event(event_name):
            raise UnsupportedEventError(event_name)

        self.__dispatcher.dispatch(event_name, *args, **keyword_args)

    def event(self, event_name, owner=None):
        def decorator(handler):
            self.add_handler(event_name, handler, owner)
            return handler

        return decorator

    @property
    def events(self):
        if self.__complement:
            return self.__dispatcher.events - self.__allowed_events
        else:
            return self.__dispatcher.events & self.__allowed_events

    def has_event(self, event_name):
        return (((event_name in self.__allowed_events) ^ self.__complement)
                and self.__dispatcher.has_event(event_name))

