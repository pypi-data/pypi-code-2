### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for document view viewlet

$Id: body.py 52240 2008-12-29 00:25:58Z cray $
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
    def body(self) :
        return self.ps['body']
        
    def __getattr__(self,name) :
        return getattr(self.ob,name)

class Body(ViewletBase) :
    """ Body """

    def __init__(self,*kv,**kw) :
        super(Body,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
            