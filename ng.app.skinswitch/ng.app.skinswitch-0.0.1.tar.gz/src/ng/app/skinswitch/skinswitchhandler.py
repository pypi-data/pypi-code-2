### -*- coding: utf-8 -*- #############################################
#######################################################################
"""
SkinSwitch traverser for the Zope 3

$Id: skinswitchhandler.py 54770 2010-12-09 01:35:34Z cray $
"""
__author__  = "Andrey Orlov, 2010"
__license__ = "GPL"
__version__ = "$Revision: 54770 $"


from zope.publisher.interfaces import NotFound 
from zope.app import zapi 
from zope.app.container.traversal import ContainerTraverser 
from interfaces import ISkinSwitchable, ISkinSwitchAnnotation
from zope.interface import providedBy, directlyProvides, directlyProvidedBy
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.browser import applySkin


def handleBeforeTraverse(ob,event) :
    skinswitch = ISkinSwitchAnnotation(ob)
    
    if skinswitch.skin :
        try:
            skin = getUtility(IBrowserSkinType, skinswitch.skin)
        except ComponentLookupError:
            raise TraversalError("Traverse set skin %s error" % name)

        print "set",skin
        applySkin(event.request,skin) 

    for skin in skinswitch.skinon :
        try:
            skin = getUtility(IBrowserSkinType, skin)
        except ComponentLookupError:
            raise TraversalError("Traverse set skin %s error" % name)

        print "set",skin
        directlyProvides(event.request, *(list(directlyProvidedBy(event.request)) + [skin]))                                                
    

