# -*- coding: utf-8 -*-
"""The definition of IBlogAble marker interface

$Id: interfaces.py 52408 2009-01-30 11:28:00Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52408 $"

from zope.interface import Interface

class IBlogAble(Interface) :
    """Marker interface to use blog """