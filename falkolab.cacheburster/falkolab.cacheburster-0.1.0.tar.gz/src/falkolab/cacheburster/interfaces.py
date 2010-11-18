#############################################################################
#
# Copyright (c) 2010 Falko Lab and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE. 
#
##############################################################################
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.interface.interface import Interface

class IVersionedResourceLayer(IBrowserRequest):
    """A layer that contains all registrations of this package.
    
    It is intended that someone can just use this layer as a base layer when
    using this package."""

class IVersionManager(Interface):   
    
    def getVersion():
        """Compute version for resource"""
        
    def __call__():
        """Get resource version"""
        

class IRuleFactory(Interface):
    
    def __call__(resource):
        """Return an IVersionRule object"""
        
class IVersionRule(Interface):
    
    def check():
        """Is the rule acceptable"""
        
    def __call__(request):  
        """Process rule"""

