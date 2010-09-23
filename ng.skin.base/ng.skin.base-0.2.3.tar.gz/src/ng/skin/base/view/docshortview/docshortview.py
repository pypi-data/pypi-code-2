### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for the IDocShort and IDocBody view

$Id: docshortview.py 50545 2008-02-06 09:00:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.interface import Interface
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from zope.publisher.browser import BrowserView
        
class Proxy(object) :

    def __init__(self,ob) :
        self.ob = ob
        self.ps = IPropertySheet(ob)
                        
    @property
    def abstract(self) :
        return self.ps['abstract'] or self.ps.get('auto',u"")
        
    @property
    def body(self) :
        return self.ps.get('body',u"")
        
    @property
    def title(self) :
        return self.ps['title'] or self.ob.__name__
        
    def __getattr__(self,name) :
        return getattr(self.ob,name)
        
class DocShortView(BrowserView) :
    def __init__(self,*kv,**kw) :
        super(DocShortView,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
