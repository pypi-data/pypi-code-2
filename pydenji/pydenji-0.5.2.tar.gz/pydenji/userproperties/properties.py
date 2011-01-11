#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from copy import deepcopy

# TODO: this is not a FrozenDict. Should we just kill it?
class _FrozenDict(object):
    def __init__(self, d):
        self._d = deepcopy(d)

    def __getitem__(self, item):
        return self._d[item]

    def keys(self):
        return self._d.keys()

    def __contains__(self, key):
        return key in self._d

    def __iter__(self):
        return self._d.iterkeys()

    def __repr__(self):
        return "<FrozenDict(%r)>" % self._d


def UserProperties(property_mapping):
    return _FrozenDict(property_mapping)




