#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Solver Factory

Helper funtions to allow to intantiate easily components that
implement ISolver interface
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['SolverFactory']

# Project dependences
from sleipnir.components.components import Component
from sleipnir.components.entrypoint import ExtensionPoint

# Subpackage dependences
from ..interfaces import solver


#pylint: disable-msg=R0903
class SolverFactory(Component):
    """
    A Helper to instantiate 'ISolver' components which satiasfies a
    condition
    """

    solvers = ExtensionPoint(solver.ISolver)

    def __init__(self):
        super(SolverFactory, self).__init__()

    def create(self, ffilter=lambda x: True, size=None):
        """
        Returns a tuple of 'ISolver' components

        Keyword arguments:
        ffilter -- A callable to filter available solvers
        size -- Maximum size of the returned tuple. Use None (by
        default) to return all available filters
        """

        return [m for m in self.solvers if ffilter(m)][:size]
