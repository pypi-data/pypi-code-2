### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SkinSwitchAnnotation class

$Id: skinswitchannotation.py 54769 2010-12-09 00:44:09Z cray $
"""
__author__  = "Andrey Orlov, 2010"
__license__ = "GPL"
__version__ = "$Revision: 54769 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from interfaces import ISkinSwitchAnnotation
from persistent import Persistent

                
class SkinSwitchAnnotation(Persistent) :
    implements(ISkinSwitchAnnotation)
    
    skin = ""
    
    skinon = ()
    