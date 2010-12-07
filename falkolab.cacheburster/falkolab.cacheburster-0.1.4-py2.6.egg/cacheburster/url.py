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
from zope.interface.declarations import implementsOnly
from zope.traversing.browser.interfaces import IAbsoluteURL
import zope.component
import falkolab.cacheburster.interfaces
from falkolab.cacheburster.interfaces import IVersionRule
from zope.browserresource.resource import AbsoluteURL
try:
    from zope.app.publisher.interfaces import IResource
except ImportError:
    from zope.component.interfaces import IResource

_rules_map = {}
_name_map = {}

class VersionedURL(AbsoluteURL):
    """Inserts a versioned info (hash, crc32 or versionfile) of the contents into 
    the resource's URL, so the URL changes whenever the contents change, thereby 
    forcing a browser to update its cache.
    """
    implementsOnly(IAbsoluteURL)
    zope.component.adapts(IResource, 
                    falkolab.cacheburster.interfaces.IVersionedResourceLayer)    
    
    def _createUrl(self, baseUrl, name):        
        rule = self._findRule(name)
        
        if rule:                  
            new_name = rule(self.request)                  

            #for correct traverse versioned resources  
            only_name = new_name.split('?')[0]                    
            if name!=only_name:                
                _name_map[only_name.split('/')[-1]] = name.split('/')[-1]
            
            return "%s/@@/%s" % (baseUrl, new_name)  
       
        return super(VersionedURL, self)._createUrl(baseUrl, name)
    
    def _findRule(self, resourceName):
        ruleName = _rules_map.get(resourceName)        
        if ruleName:
            return zope.component.getAdapter(self.context, IVersionRule, ruleName, 
                                      context=self.context)                 
            
        for rulename, rule in zope.component.getAdapters((self.context,), 
                                            IVersionRule, context=self.context):
            if rule.check():
                _rules_map[resourceName] = rule.__name__
                return rule
        return None