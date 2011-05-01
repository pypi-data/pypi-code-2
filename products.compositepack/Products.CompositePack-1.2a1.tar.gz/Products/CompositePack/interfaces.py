##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: compositetool.py 18879 2006-02-02 15:27:55Z jladage $
"""
from zope.interface import Interface
from zope.interface import Attribute
#
#   Composite tool interface
#
class ICompositeTool(Interface):
    """ Manage composite properties of the site as a whole.
    """
    id = Attribute('id', 'Must be set to "composite_tool"')


class IPackComposite(Interface):
    pass
