### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for the IDocShort and IDocBody view

$Id: abstractannotation.py 52410 2009-01-30 11:33:29Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52410 $"

from zope.interface import Interface
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.content.article.interfaces import IDocShort
from zope.location import location         
from zope.security.proxy import removeSecurityProxy        
from ng.lib.viewletbase import ViewletBase

class Proxy(object) :

    def __init__(self,ob) :
        self.ob = ob
        self.doc = IDocShort(ob)
        self.ps = IPropertySheet(self.doc)
                                
    @property
    def abstract(self) :
        return self.ps['abstract'] or self.ps.get('auto',u"")
        
    @property
    def title(self) :
        return self.ps['title'] or self.ob.__name__

    def __getattr__(self,name) :
        try :
          return getattr(self.ob,name)
        except LookupError :
          return getattr(self.doc,name)          
        
class Abstract(ViewletBase) :
    def __init__(self,*kv,**kw) :
        super(Abstract,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
