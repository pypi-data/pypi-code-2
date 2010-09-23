### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 52399 2009-01-27 14:36:50Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52399 $"
 
from zope.interface import Interface

class IToolBoxProvider(Interface) :
    """ Interface for ToolBox provider
    """
