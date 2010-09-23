### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for abstract viewlet for profile

$Id: profileabstract.py 52243 2008-12-29 00:28:16Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.lib.viewletbase import ViewletBase
from ng.content.profile.profileannotation.interfaces import IProfileAnnotation

class Proxy(object) :
    def __init__(self,ob) :
        self.ob = ob
        self.ps = IPropertySheet(ob)
        self.profile = IProfileAnnotation(ob)
                        
    @property
    def abstract(self) :
        return self.ps['abstract'] or self.ps.get('auto',u"")
        
    @property
    def title(self) :
        return self.ps['title'] or self.ob.__name__
        
    def __getattr__(self,name) :
        return getattr(self.ob,name)

class ProfileAbstract(ViewletBase) :
    """ Abstract """

    def __init__(self,*kv,**kw) :
        super(ProfileAbstract,self).__init__(*kv,**kw)
        self.context = Proxy(self.context)
        
        