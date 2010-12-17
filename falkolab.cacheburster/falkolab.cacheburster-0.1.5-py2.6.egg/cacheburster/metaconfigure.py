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
import re
import os.path
import glob
from zope.configuration.exceptions import ConfigurationError
from zope.interface.declarations import implements
from falkolab.cacheburster.interfaces import IRuleFactory,\
    IVersionRule

from zope.component.zcml import handler
from zope.browserresource.interfaces import IResource
from falkolab.cacheburster.rule import CacheBursterRule

class RuleFactory(object):
    implements(IRuleFactory)
    
    def __init__(self, cexpr, replacement, files, manager, name):
        self.__name = name
        self.__cexpr = cexpr
        self.__replacement = replacement
        self.__files = files
        self.__manager = manager

        
    def __call__(self, resource):        
        rule = CacheBursterRule(resource,
                               self.__cexpr, self.__replacement, self.__files, 
                               self.__manager)  
        rule.__name__ = self.__name
       
        return rule

def cacheBurster(_context, from_, to, manager=None, fileset=None):
        
        files = None
        if fileset:
            files=set()
            for path in fileset:                
                files = files | set(glob.glob(path))   
            
            files = [os.path.normcase(os.path.normpath(fileName)) for fileName in files]                    
             
        flags = re.UNICODE 
        
        fsCaseSensetive = os.path.normcase('Aa') == 'Aa'
        if not fsCaseSensetive:
            flags |= re.IGNORECASE       
     
        try:
            cexpr = re.compile(raw(from_), flags)           
        except:
            raise ConfigurationError("Can't compile rule expressions.")
           
        _context.action(
                        discriminator = ('cacheBurster', from_),
        callable = cacheBusterHandler,
        args = (cexpr, raw(to), files, manager, from_, _context.info),
        )        
        
def cacheBusterHandler(cexpr, replacement, files, manager, name, context_info):           
    factory = RuleFactory(cexpr, replacement, files, manager, name)          
    handler('registerAdapter', factory, (IResource,), IVersionRule, \
            name=name, info=context_info)       
     
escape_dict={'\a':r'\a',
           '\b':r'\b',
           '\c':r'\c',
           '\f':r'\f',
           '\n':r'\n',
           '\r':r'\r',
           '\t':r'\t',
           '\v':r'\v',
           '\'':r'\'',
           '\"':r'\"',
           '\0':r'\0',
           '\1':r'\1',
           '\2':r'\2',
           '\3':r'\3',
           '\4':r'\4',
           '\5':r'\5',
           '\6':r'\6',
           '\7':r'\7',
           '\8':r'\8',
           '\9':r'\9'}

def raw(text):
    """Returns a raw string representation of text"""
    return "".join([escape_dict.get(char,char) for char in text])