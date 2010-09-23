### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for dictionary common page.

$Id: dictionary.py 50545 2008-02-06 09:00:53Z cray $
"""
__author__  = "Andrey Orlov 2006 12 05"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

import zope.component
from zope.app import zapi
from zope.app.catalog.interfaces import ICatalog
from zope.traversing.browser.absoluteurl import absoluteURL
from zc.catalog.interfaces import IIndexValues

class Dictionary(object) :
    
    def __init__(self,context,request) :
        super(Dictionary,self).__init__(context,request)
        

    def words(self) :
        return (x for x in sorted(zapi.getUtility(IIndexValues, 'keyword', context=self.context).values()) if x)
        
    def articlebyword(self,word) :
        return zapi.getUtility(
                    zope.app.catalog.interfaces.ICatalog,
                    name="catalog",context=self.context).searchResults(keyword={'all_of':(word,)})

                    
        
