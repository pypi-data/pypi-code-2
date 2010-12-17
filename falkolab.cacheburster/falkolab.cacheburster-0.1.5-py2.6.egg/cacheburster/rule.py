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
import zope.component
import os.path
from falkolab.cacheburster.interfaces import IVersionManager
from zope.browserresource.file import File


class CacheBursterRule(object):
    __name__ = None
    
    def __init__(self, resource, cexpr, replacement, files, manager):
        self.__resource = resource
        self.__cexpr = cexpr
        self.__replacement = replacement
        self.__files = files
        self.__manager = manager        
                
    def check(self):    
        res = self.__resource    
        if self.__files:
            resourceContext = res.chooseContext()
            if isinstance(resourceContext, File):
                path = resourceContext.path
                if os.path.normcase(os.path.normpath(path)) not in self.__files:                       
                    return False                
                           
        return self.__cexpr.match(self._getName()) != None
    
    def _getName(self):
        name = self.__resource.__name__
        if name.startswith('++resource++'):
            name = name[12:]   
        return  name
    
    def __call__(self, request):        
        vm = zope.component.getMultiAdapter((self.__resource, request), IVersionManager, \
                                       self.__manager)
        
        repl = self.__replacement.format(version=vm())             
        return self.__cexpr.sub(repl, self._getName())
        