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
try:
    import os
    import sys
    # pylint: disable-msg=W0611
    import sleipnir
except ImportError:
    sys.path.insert(0, (os.pardir + os.sep) * 3 + 'src')

__all__ = ['ISalut']

# Sleipnir dependences
from sleipnir.core.components.entrypoint import Interface


#pylint: disable-msg=W0232,R0903,E1002
class ISalut(Interface):
    """Hello Interface"""

    def hello(self, name):
        """Show a salut"""
