#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

from pydenji.config.argwiring import wire
from itertools import chain
try:
    from collections import Mapping as _BaseMappingClass
except ImportError:
    from UserDict import DictMixin as _BaseMappingClass

class NameClashError(Exception):
    pass

# TODO: make this inherit from ABC or from UserDict for 2.5
class PropertyAndContextMergingProxy(_BaseMappingClass):
    def __init__(self, context, mapping):
        self._context = context
        self._mapping = mapping

        self._verify_no_clashes()

    def _verify_no_clashes(self):
        common_keys = set(self._context).intersection(set(self._mapping))
        if common_keys:
            raise NameClashError, "Clashing keys between context and mapping: %s" % (
                ",".join(common_keys))

    def __len__(self):
        return len(self._context) + len(self._mapping)

    def __iter__(self):
        return chain(self._context, self._mapping)

    def __getitem__(self, key):
        if key in self._mapping:
            return self._mapping[key]
        elif key in self._context:
            # TODO: support arguments?
            return self._context.get_object(key)
        raise KeyError, "Could not find '%s' in mapping or context either"
    

class ArgNameContextWirer(object):
    def __init__(self, context, mapping):
        self.mergingproxy = PropertyAndContextMergingProxy(context, mapping)

    def wire(self, callable_obj, *args, **kwargs):
        return wire(callable_obj, self.mergingproxy, *args, **kwargs)