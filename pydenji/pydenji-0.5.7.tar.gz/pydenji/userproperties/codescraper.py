#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from byteplay import Code
from byteplay import LOAD_FAST
from byteplay import LOAD_ATTR
from byteplay import LOAD_CONST
from byteplay import BINARY_SUBSCR
from byteplay import STORE_FAST


import inspect

_ANY_VALUE = object()


class _MatchingTuple(tuple):
    def __eq__(self, other):
        for s, o in zip(self, other):
            if (s is not _ANY_VALUE) and (s != o):
                return False
        return True

# variation on stackoverflow #3847386 by Dave Kirby
def _accumulate_contained(small, big):
    accumulator = []
    for i in xrange(len(big) - len(small)+1):
        for j in xrange(len(small)):
            if small[j] == big[i+j]:
                pass
            else:
                break
        else:
            accumulator.append(i)
    return accumulator


def _get_accumulated(func, usage_matcher, target_offset):
    # what should we name this func??
        accumulator = []
        disassembled_code = Code.from_code(func.func_code).code
        contained = _accumulate_contained(usage_matcher, disassembled_code)
        for contained_index in contained:
            accumulator.append(disassembled_code[contained_index + target_offset][1])
        return accumulator

def get_getitem_accesses(obj, attr):
    """
    For whatever member function of obj, return a set containing all the keys
    for which obj.attr is accessed through __getitem__.
    """
    usage_matcher = [(LOAD_FAST, 'self'), (LOAD_ATTR, attr),
        _MatchingTuple((LOAD_CONST, _ANY_VALUE)), (BINARY_SUBSCR, None)]
    funcs = inspect.getmembers(obj, inspect.ismethod)

    used_keys = set()

    # directly accessed self.attr __getitem__
    for name, func in funcs:
        used_keys.update(_get_accumulated(func, usage_matcher, 2))

    # accessed after saving props somewhere
    usage_matcher = [(LOAD_FAST, 'self'), (LOAD_ATTR, attr),
                _MatchingTuple((STORE_FAST, _ANY_VALUE))]
    
    for name, func in funcs:
        stored_attributes = _get_accumulated(func, usage_matcher, 2)
        for stored_attr in stored_attributes:
            attr_usage_matcher = [(LOAD_FAST, stored_attr),
                _MatchingTuple((LOAD_CONST, _ANY_VALUE)), (BINARY_SUBSCR, None)]
            used_keys.update(_get_accumulated(func, attr_usage_matcher, 1))

    return used_keys

    






