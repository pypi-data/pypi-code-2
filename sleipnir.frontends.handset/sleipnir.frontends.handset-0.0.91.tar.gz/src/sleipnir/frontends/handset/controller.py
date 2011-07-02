#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Application Controller

Main Application Component Manager
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
from odict import odict

__all__ = ['QApplicationController']

# Project requirements
from sleipnir.core.log import log

# local submodule requirements
from .profiles import ProfileFactory, Profiles
from .view import Views


class QApplicationController(object):
    """
    A flow navigation controller. See PEAA03 for details about
    Application Controller Pattern
    """
    #pylint: disable-msg=W0232,R0903,E0602
    class QApplicationStatus(enum):
        """Base states"""
        UNKNOWN, STARTING = xrange(2)

    #pylint: disable-msg=R0903
    class State(object):
        """Memento object"""
        def __init__(self, event, status):
            self.event = event
            self.state = status

    def __init__(self, profiles=None):
        self._history = []
        self._dispatchers = odict()
        factory = ProfileFactory.get_instance()
        factory.create(self, Profiles(profiles))

    def register(self, event, state, action, view, where=None, animation=None):
        """Stores a flow for a profile(where)"""
        dispatcher = self._dispatchers.setdefault(where, {})
        dispatcher = dispatcher.setdefault(event, {})
        if state in dispatcher:
            log.warning("Rewrited flow: (%s, %s, %s)" % (where, event, state))
        dispatcher[state] = (action, view, animation)

    def next(self, event, status):
        """Dispatch an event and saves state in history"""
        self._history.append(self.State(event, status))
        return self.dispatch(event, status)

    def prev(self):
        """
        Discards current event and dispatch previous one. Like a
        back dispatch
        """
        if len(self._history) > 1:
            self._history.pop(-1)
            state = self._history[-1]
            return self.dispatch(state.event, state.status)
        raise EOFError

    def dispatch(self, event, status):
        """Peeks action and command and animation for event and status"""
        log.controller.info("Dispatch (%s,%s)" % (event, status))
        for dispatcher in self._dispatchers.iterkeys():
            dispatcher = self._dispatchers[dispatcher][event]
            state = dispatcher[status]
            if state is not None:
                action, view, animation = state
                if action and not callable(action):
                    raise NotImplementedError
                if type(view) in (str, unicode,):
                    view = Views.get_instance().get(view)
                    dispatcher[status] = (action, view, animation)
                return action, view, animation
        return (None, None, None)

    def clear(self, event=None, status="UNKNOWN"):
        "reset history to event and status"
        self._history = [self.State(event, status)]
