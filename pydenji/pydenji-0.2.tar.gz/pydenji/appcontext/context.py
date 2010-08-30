#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from pydenji.config.pythonconfig import is_object_factory, is_eager
from pydenji.appcontext.aware import is_appcontext_aware
from pydenji.config.composite import CompositeConfig

class UnconfiguredError(Exception):
    pass

class AppContext(object):
    def __init__(self, *configurations):
        conf = CompositeConfig(configurations)
        self._names_factories = self._get_all_factories(conf)
        conf.set_app_context(self)
        self._start(self._names_factories)

    def get_object(self, name, *args, **kwargs):
        try:
            factory = self._names_factories[name]
        except KeyError:
            raise UnconfiguredError, "No factory was configured for '%s'" % name
        return self._get_instance(factory, *args, **kwargs)
    
    def _start(self, names_factories):
        for factory in names_factories.values():
            if is_eager(factory):
                self._get_instance(factory)

    def _get_instance(self, factory, *args, **kwargs):
        # this way the set_app_context() method will be called multiple times,
        # even though the object is a singleton. While it should make no harm,
        # we should think about it, might it do any harm?
        obj = factory(*args, **kwargs)
        if is_appcontext_aware(obj):
            obj.set_app_context(self)
        return obj

    @staticmethod
    def _get_all_factories(config):
        # TODO: refactor using a list comprehension/filter expr.
        names_factories = {}
        for attr in dir(config):
            value = getattr(config, attr)
            if is_object_factory(value):
                names_factories[attr] = value
        return names_factories







