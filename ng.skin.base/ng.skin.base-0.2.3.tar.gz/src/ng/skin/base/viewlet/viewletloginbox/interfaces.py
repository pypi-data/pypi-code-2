### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 52422 2009-01-31 16:30:27Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52422 $"
 
from zope.interface import Interface

class ILoginBoxProvider(Interface) :
    """ Interface for LoginBox provider
    """
