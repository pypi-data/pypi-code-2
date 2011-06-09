#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""A Solutions container for Problems"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Add here required modules

__all__ = ['Solutions']

# Local dependences


class Solutions(object):
    """A solutions container"""
    def __init__(self):
        self._solutions = {}
        self._last = None
        self._best = None

    def get(self, **kwargs):
        """
        Retrieve solutions stored for args pased. If kwargs is none,
        best one is retrieved
        """
        if kwargs is None:
            return self._best
        kw_hash = hash(tuple(sorted(kwargs.items())))
        return self._solutions.get(kw_hash, [])

    def add(self, result, **kwargs):
        """Store result as a valid solution for kwargs params"""
        kw_hash = hash(tuple(sorted(kwargs.items())))
        self._solutions.setdefault(kw_hash, []).append(result)
        self._solutions[kw_hash].sort()
        self._last = result
        self._best = self._best if self._best < self._last else self._last
        return result
