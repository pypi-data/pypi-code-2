##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Viewlet and layout interfaces.

$Id: __init__.py 238387 2011-04-30 19:58:15Z hathawsh $
"""
from zope.interface import Attribute
from zope.interface import Interface

class ILayout(Interface):
    """Interface of Layouts that can be applied to an object.
    """

    def __call__():
        """Returns the template associated with the layout.
        """

class IViewlet(Interface):
    """Interface of Viewlets that can be applied to an object.
    """

    def __call__():
        """Returns the template associated with the viewlet.
        """
