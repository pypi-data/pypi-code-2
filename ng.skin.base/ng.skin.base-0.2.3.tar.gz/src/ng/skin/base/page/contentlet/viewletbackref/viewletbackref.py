### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for backreference viewlet.

$Id: viewletbackref.py 53378 2009-07-05 20:46:14Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 53378 $"

from ng.site.content.search.interfaces import ISearch, ISearchName
from zope.app import zapi 
import zope.app.catalog.interfaces
import re
from ng.lib.viewletbase import ViewletBase

class ViewletBackRef(ViewletBase) :
    """ Wiki """

    @property
    def backref(self) :
        try :
            keyword = ISearch(self.context).keyword
        except TypeError,msg :
            pass
        else :  
            for item in zapi.getUtility(
                    zope.app.catalog.interfaces.ICatalog,
                    context=self.context). \
                    searchResults(backkeyword={'any_of': [re.sub("\s+"," ",x.lower().strip()) for x in keyword] }) :
                yield item                    
                    
        for item in zapi.getUtility(
                    zope.app.catalog.interfaces.ICatalog,
                    context=self.context). \
                    searchResults(backname={'any_of':ISearch(self.context).name}) :
            yield item
                                