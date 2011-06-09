#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Interface Marshals

Required by components which performs serialization of it's contents
to a storage media
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

#pylint: disable-msg=W0232,R0903

__all__ = ['IMarshal', 'IUnMarshal']

# Project dependencecs
from sleipnir.components.entrypoint import Interface


class IUnMarshal(Interface):
    """Create or update object contents from media"""

    def load(self, where):
        """Load contents from 'where' location"""


class IMarshal(Interface):
    """Save contents to media"""

    def dump(self, handler, where=None):
        """Store 'handler' instance in 'where'

        'Where' is implementation dependant and could be network,
        database, file, etc
        """
