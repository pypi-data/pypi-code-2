### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 54063 2010-06-30 04:09:18Z corbeau $
"""
__author__  = "Yegor Shershnev, 2010"
__license__ = "GPL"
__version__ = "$Revision: 54063 $"
 
from zope.interface import Interface

class ISearchProvider(Interface) :
    """ Interface for Search provider
    """
