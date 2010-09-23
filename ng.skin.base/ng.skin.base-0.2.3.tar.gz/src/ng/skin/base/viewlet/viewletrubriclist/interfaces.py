### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.skin.greenpsy package

$Id: interfaces.py 52494 2009-02-09 23:30:08Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52494 $"
 
from zope.interface import Interface

class IRubricListProvider(Interface) :
    """ Interface for RubricList provider
    """

class IRubricCloudProvider(Interface) :
    """ Interface for RubricCloud provider """
    
class IRubricAllCloudProvider(Interface) :
    """ Interface for RubricAllCloud provider """
    

class IRubricAllCloudAllow(Interface) :
    """ Interface to allow RubricAllCloud content """    