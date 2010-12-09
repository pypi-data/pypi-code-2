### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 54769 2010-12-09 00:44:09Z cray $
"""
__author__  = "Andrey Orlov, 2010"
__license__ = "GPL"
__version__ = "$Revision: 54769 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Tuple, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from ng.lib.utilityvocabulary import UtilityVocabulary       
from zope.publisher.interfaces.browser import IBrowserSkinType
                
class ISkinSwitchable(Interface) :
    """ Interface used to turn on skin switch """
                            
class ISkinSwitchAnnotation(Interface) :
    """ """
    
    skin = Choice(
        title=u"Skin",
        source=UtilityVocabulary(IBrowserSkinType),
        required=False
        )
    
    skinon = Tuple(
        title=u"Skin extensions", 
        value_type=Choice(title=u"Skin",source=UtilityVocabulary(IBrowserSkinType)),default=()
        )
    
skinswitchannotationkey = "ng.app.skinswitch.skinswitchannotation"
