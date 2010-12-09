### -*- coding: utf-8 -*- #############################################
#######################################################################
"""SkinSwitchAnnotationAbleAdapter class for the Zope 3 based
ng.content.annotation.skinswitchannotation package

$Id: skinswitchableadapter.py 54769 2010-12-09 00:44:09Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 54769 $"


from zope.annotation.interfaces import IAnnotations 
from skinswitchannotation import SkinSwitchAnnotation
from interfaces import skinswitchannotationkey
from zope.location.location import LocationProxy 

def SkinSwitchableAdapter(context) :
    annotations = IAnnotations(context)
    try :
        ea = annotations[skinswitchannotationkey]
    except KeyError :
        ea = annotations[skinswitchannotationkey] = SkinSwitchAnnotation()
    return LocationProxy(ea, context, "++annotations++" +  skinswitchannotationkey)
