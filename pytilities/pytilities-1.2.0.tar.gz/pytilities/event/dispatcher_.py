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

# Note: named this module with _ suffix so that it doesn't clash in __init__.py
# with the dispatcher decorator

__docformat__ = 'reStructuredText'

from pytilities.delegation import (
    mapped_class, mapped)

class UnsupportedEventError(Exception):
    """Tried to access an unregistered event"""

    def __init__(self, event_name):
        Exception.__init__(self, "Unsupported event: %s" % event_name)

@mapped_class
class Dispatcher(object):

    """
    Utility class for dispatching events to handlers.

    Events have to be registered before they can be dispatched or have handlers
    added to them.

    Handlers can have an owner associated with them, usually you'll use the
    reference of the listener. This allows you to remove all the handlers of a
    specific owner, which should save you some work.

    :Class invariants: - For every (owner, event), there can be only 0 or 1 handlers
    """

    # inspired by pyglet.event.EventDispatcher, yay pyglet

    public_mapping = {}
    default_mapping = {}

    def __init__(self):
        # dict of handlers: event_name -> set((handler, owner))
        self.__handlers = {}
        self.__registered_events = set()

    @mapped(public_mapping)
    def add_handler(self, event_name, handler, owner = None):
        """
        Add handler for an event, optionally with an owner.

        :param event_name: name of the event to add the handler to
        :type event_name: string

        :param handler: the handler to call when the event is dispatched
        :type handler: callable

        :param owner: owner of the handler. Use this reference to easily remove all
            your handlers from the dispatcher (e.g. remove all handlers
            with the same owner). Default: `None`

        :raise UnsupportedEventError: when `event_name` doesn't exist
        """

        if not self.has_event(event_name):
            raise UnsupportedEventError(event_name)

        assert handler, "handler argument musn't be None"

        assert (handler, owner) not in self.__handlers, (
            "You cannot add the same handler for the same owner and event " +
            "more than once.")

        self.__handlers.setdefault(event_name, set())
        self.__handlers[event_name].add((handler, owner))

    @mapped(public_mapping)
    def remove_handlers(self, event_name=None, owner=None):
        """
        Remove all or some handlers of the dispatcher.
        
        `event_name` and `owner` act as filters of what to remove.

        If no handler matched the criterea, the method will return silently.

        :param event_name: the event of which to remove the handlers. `None`
            means any. Default: `None`
        :type event_name: string

        :param owner: the owner of which to remove the handlers. `None` means
            any. Default: `None`
        """

        if event_name:
            self.__remove_handlers(event_name, owner)
        else:
            for event in self.__registered_events:
                self.__remove_handlers(event, owner)

    def __remove_handlers(self, event, owner):
        """Remove handlers of single event, optionally with particular owner """
        handlers = self.__handlers[event]
        handlers -= set((handler, o) for (handler, o) in handlers 
                        if o is owner)

    @mapped(public_mapping)
    def remove_handler(self, event_name, handler, owner = None):
        """
        Remove a handler from an event. It is an error to try to remove a
        handler from an event that doesn't have this handler attached to it.

        :param event_name: name of the event to which the handler belongs
        :type event_name: string

        :param handler: the handler that is attached to the event
        :type event_name: callable

        :param owner: owner of the handler. Default: `None`

        :Preconditions: 1. `handler` is attached to `event_name`

        :raise UnsupportedEventError: when `event_name` doesn't exist
        """

        if not self.has_event(event_name):
            raise UnsupportedEventError(event_name)

        assert handler, "handler argument musn't be None"

        self.__handlers[event_name].remove((handler, owner))

    @mapped(default_mapping)
    def dispatch(self, event_name, *args, **keyword_args):
        """
        Dispatch an event to its handlers. 
        
        The handlers are executed in a random order.
        
        :param event_name: name of the event to dispatch
        :type event_name: string

        :param args: arguments to pass to the handlers

        :param keyword_args: keyword arguments to pass to the handlers

        :raise UnsupportedEventError: if `event_name` doesn't exist
        """

        if not self.has_event(event_name):
            raise UnsupportedEventError(event_name)

        for handler in self.__handlers.get(event_name, ()):
            handler[0](*args, **keyword_args)

    @mapped(public_mapping)
    def event(self, event_name, owner = None):
        """
        Register the decorated as a handler of `event_name`

        :param event_name: name of the event
        :type event_name: string

        :param owner:
            owner of the handler. Use this reference to easily remove all
            your handlers from the dispatcher (e.g. remove all handlers
            with the same owner). Default: `None`
        """

        def decorator(handler):
            self.add_handler(event_name, handler, owner)
            return handler

        return decorator

    @mapped(default_mapping)
    def register_events(self, *event_names):
        """
        Register events.
        
        :param event_names: names of events to support
        :type event_names: (string...)
        """
        # this allows us to have methods like has event, which allow for better
        # duck typing (if I see something that sends out quack events, then I
        # call that a duck)
        self.__registered_events.update(event_names)

    @mapped(public_mapping)
    def has_event(self, event_name):
        """
        Checks if `event_name` is supported

        :param event_name: name of the event
        :type event_name: string

        :return: True if the dispatcher has the event
        """
        return event_name in self.__registered_events

    @mapped(public_mapping)
    @property
    def events(self):
        """
        Read-only, set of all supported events

        :rtype: frozenset(string...)
        """
        return frozenset(self.__registered_events)

Dispatcher.default_mapping.update(Dispatcher.public_mapping)
