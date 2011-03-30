#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Plugin interfaces to be imported by tests"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "26 January 2010"
__license__ = "See LICENSE file for details"

# Add here required modules

__all__ = ['ISalut']

# Sleipnir dependences
from sleipnir.components.entrypoint import Interface


#pylint: disable-msg=W0232,R0903,E1002
class ISalut(Interface):
    """Hello Interface"""

    def hello(self, name):
        """Show a salut"""
