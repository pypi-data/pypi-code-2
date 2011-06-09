#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Exceptions for Sleipnir TSP problems"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['PartialStop', ]


#pylint: disable-msg=R0903,W0232
class PartialStop(Exception):
    """
    Raised by solver implementations when a partial break point is
    reached
    """
