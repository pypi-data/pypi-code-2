#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Problem Factory

Helper funtions to allow to intantiate easily components that
implement IProblem interface
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['ProblemFactory']

#Project dependences
from sleipnir.components.components import Component
from sleipnir.components.entrypoint import ExtensionPoint

# Subpackage dependences
from ..interfaces import problem


#pylint: disable-msg=R0903
class AbstractFactory(Component):
    """
    A Helper to instantiate 'IProblem' components which satiasfies a
    condition
    """
    abstract = True

    def __init__(self):
        super(AbstractFactory, self).__init__()

    def create(self, ffilter=lambda x: True, size=None):
        """
        Returns a tuple of 'IProblem' components

        Keyword arguments:
        ffilter -- A callable to filter available problems
        size -- Maximum size of the returned tuple. Use None (by
        default) to return all available filters
        """
        assert self.extension_point
        return [m for m in self.extension_point if ffilter(m)][:size]


#pylint: disable-msg=R0903
class ProblemFactory(AbstractFactory):
    """Helper to build IProblem component instances"""

    abstract = False
    extension_point = ExtensionPoint(problem.IProblem)
