#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Helper

QML Helper functions
"""

from __future__ import absolute_import

__author__  = "Carlos Martín"
__license__ = "See LICENSE file for details"

# Import here any required modules
import re

from odict import odict
from itertools import ifilter, chain

__all__ = ['ProfileFactory', 'Profiles']

# Project requirements
from sleipnir.core.factory import NamedAbstractFactory
from sleipnir.core.log import log

# local submodule requirements


#pylint: disable-msg=W0232,E0602,R0903
class Actions(enum):
    """Actions enumarator"""
    INSERT, REMOVE = xrange(2)


class Profiles(object):
    """Valid profiles activated for"""
    def __init__(self, profiles=None):
        self._profiles = odict()
        self._proregex = re.compile(r"\+|!")
        self.extend(profiles or ProfileFactory.get_instance().flows())

    def __str__(self):
        return ",".join((profile for profile in self))

    def __contains__(self, value):
        value = self._proregex.sub("", value)
        return value in self._profiles

    def __getitem__(self, value):
        return self._profiles[value]

    def __getattr__(self, value):
        return getattr(self._profiles, value)

    def __iter__(self):
        for key, value in self._profiles.iteritems():
            action = '!' if value == Actions.REMOVE else "+"
            yield("".join((action, key)))

    def __or__(self, other):
        # Order should be self,order. We readd self to override
        # actions broken by other
        return self.__class__(chain(self, other, self))

    def __sub__(self, other):
        instance = self.__class__()
        for key, action in self._profiles.iteritems():
            if key not in other or other[key] != action:
                instance.insert(key, action)
        return instance

    @property
    def profiles(self):
        """Get a sorted dict of profiles"""
        return self._profiles

    def add(self, value):
        """Add profiles defines in value"""
        action = Actions.INSERT
        value = value.strip()
        if value and value.strip()[0] == '!':
            action = Actions.REMOVE
        self._profiles[self._proregex.sub("", value)] = action

    def insert(self, value, action=Actions.INSERT):
        """insert profile value with action"""
        self._profiles[value] = action

    def delete(self, value):
        """Remove profile from available ones"""
        del self._profiles[value]

    def extend(self, values):
        """extend profile with values"""
        # parse comma separated list of values
        if type(values) in (str, unicode):
            values = values.split(',')
        if values is not None:
            [self.add(prof) for prof in \
                 ifilter(lambda x: len(x) > 0, values)]


class ProfileFactory(NamedAbstractFactory):
    """Main Flow(Profiles) factory"""
    def __init__(self, *args, **kwargs):
        NamedAbstractFactory.__init__(self, *args, **kwargs)

    def flows(self):
        """Get a string list of available"""
        backends = self.backends.itervalues()
        return ",".join((backend.PROVIDES for backend in backends))


class MetaProfile(type):
    """Profile Metaclass"""
    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if name != "BaseProfile":
            log.profiles.info("'%s' profile flow registered", mcs.PROVIDES)
            ProfileFactory.get_instance().register(name, mcs)


class BaseProfile(object):
    """Base class to define Profile Flows"""

    __metaclass__ = MetaProfile

    PROVIDES = ""
    REGISTER = []

    def __init__(self, dispatch, profiles):
        self._dispatch = dispatch
        self._profiles = profiles
        # Register actions
        action = self._profiles.get(self.PROVIDES, Actions.INSERT)
        if action != Actions.REMOVE:
            #pylint: disable-msg=W0142
            [self.register(*line) for line in self.REGISTER]

    def register(self, event, state, action, view, where=None, animation=None):
        """Register a flow into Application Controller"""
        dispacher = self._dispatch
        if self._profiles[where] != Actions.REMOVE:
            dispacher.register(event, state, action, view, where, animation)

    #pylint: disable-msg=W0613
    @classmethod
    def can_handle(cls, dispatch, profiles):
        """Verify that this profile should be active"""
        return cls.PROVIDES in profiles

# Now its safe to register all flows with ProfileFactory. Import flows
# MUST be always declared AFTER BaseProfile and ProfileFactory
#pylint: disable-msg=W0611
from .import flows
