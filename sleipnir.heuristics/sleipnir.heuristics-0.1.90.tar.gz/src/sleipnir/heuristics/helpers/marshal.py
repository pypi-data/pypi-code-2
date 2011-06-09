#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Marshal Factories

Helper funtions to allow to intantiate easily IMarshal and IUnMarshal
components
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "21 January 2010"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['MarshalFactory', 'UnMarshalFactory']

# Project dependences
from sleipnir.components.components import Component
from sleipnir.components.entrypoint import ExtensionPoint

# Subpackage dependences
from ..interfaces import marshal


#pylint: disable-msg=R0903
class MarshalFactory(Component):
    """
    A Helper to instantiate 'IMarshal' components which satiasfies a
    condition
    """

    marshals = ExtensionPoint(marshal.IMarshal)

    def __init__(self):
        super(MarshalFactory, self).__init__()

    def create(self, ffilter=lambda x: True, size=None):
        """
        Returns a tuple of 'IMarshal' components

        Keyword arguments:
        ffilter -- A callable to filter available marshals
        size -- Maximum size of the returned tuple. Use None (by
        default) to return all available filters
        """

        return [m for m in self.marshals if ffilter(m)][:size]


#pylint: disable-msg=R0903
class UnMarshalFactory(Component):
    """
    A Helper to instantiate 'IUnMarshal' components which satiasfies a
    condition
    """

    unmarshals = ExtensionPoint(marshal.IUnMarshal)

    def __init__(self):
        super(UnMarshalFactory, self).__init__()

    def create(self, ffilter=lambda x: True, size=None):
        """
        Returns a tuple of 'IUnMarshal' components

        Keyword arguments:
        ffilter -- A callable to filter available unmarshals
        size -- Maximum size of the returned tuple. Use None (by
        default) to return all available filters
        """

        return [m for m in self.unmarshals if ffilter(m)][:size]
