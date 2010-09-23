### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 51309 2008-07-09 03:54:34Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51309 $"
 
from zope.interface import Interface

class ITopCommunitiesBoxProvider(Interface) :
    """ Interface for TopCommunitiesBox provider
    """
