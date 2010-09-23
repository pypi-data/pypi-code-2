### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for abstract viewlet

$Id: abstract.py 52240 2008-12-29 00:25:58Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 52240 $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.lib.viewletbase import ViewletBase

class Proxy(object) :
    def __init__(self,ob) :
        self.ob = ob
        self.ps = IPropertySheet(ob)
                        
    @property
    def abstract(self) :
        return self.ps['abstract'] or self.ps.get('auto',u"")
        
    @property
    def title(self) :
        return self.ps['title'] or self.ob.__name__
        
    def __getattr__(self,name) :
        return getattr(self.ob,name)



class Abstract(ViewletBase) :
    """ Abstract """

    def __init__(self,*kv,**kw) :
        super(Abstract,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
        