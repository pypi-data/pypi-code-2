#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""View problem Interfaces"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = ['IView', ]

# Project Dependences
from sleipnir.components.entrypoint import Interface


class IView(Interface):
    """Base interface required by view components"""

    @property
    def item(self):
        """Returs item (view) implemented by component"""
        raise NotImplementedError

    def create(self, window, share_ctx):
        """
        Get a valid item view for window or create one if a
        previous one not exists
        """
        raise NotImplementedError

    def remove(self, item):
        """Make a view item private. Destroy register stuff"""
        raise NotImplementedError
