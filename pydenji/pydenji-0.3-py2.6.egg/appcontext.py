#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from pydenji.config.pythonconfig import is_object_factory, is_eager

class UnconfiguredError(Exception):
    pass

class AppContext(object):
    def __init__(self, configuration):
        self._names_factories = self._get_all_factories(configuration)
        self._start(self._names_factories)

    def get_object(self, name, *args, **kwargs):
        try:
            return self._names_factories[name](*args, **kwargs)
        except KeyError:
            raise UnconfiguredError, "No factory was configured for %s" % name

    def _start(self, names_factories):
        for factory in names_factories.values():
            if is_eager(factory):
                factory()

    @staticmethod
    def _get_all_factories(config):
        # TODO: refactor using a list comprehension/filter expr.
        names_factories = {}
        for attr in dir(config):
            value = getattr(config, attr)
            if is_object_factory(value):
                names_factories[attr] = value
        return names_factories







