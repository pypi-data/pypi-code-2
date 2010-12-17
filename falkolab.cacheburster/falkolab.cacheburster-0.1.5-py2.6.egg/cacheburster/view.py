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
from zope.browserresource.resources import Resources
from zope.interface.declarations import implements
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces import NotFound
from falkolab.cacheburster.url import _name_map

class VersionedResources(Resources):
    implements(IBrowserPublisher)
    
    def publishTraverse(self, request, name):
        try:
            resource = super(VersionedResources, self).publishTraverse(request, name)
            tStak = request.getTraversalStack()
            request.setTraversalStack([_name_map.get(name,name) for name in tStak])             
        except NotFound:                       
            orig_name = _name_map.get(name)            
            if orig_name is None:
                raise NotFound(self, name)
            
            resource = super(VersionedResources, self).publishTraverse(request, orig_name)       
        return resource