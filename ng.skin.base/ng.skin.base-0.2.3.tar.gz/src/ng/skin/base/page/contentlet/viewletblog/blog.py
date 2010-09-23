### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for content viewlet

$Id: blog.py 52408 2009-01-30 11:28:00Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from ng.lib.viewletbase import ViewletBase
from ng.app.objectqueue.interfaces import IObjectQueue
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class Blog(ViewletBase) :
    """ Content """

    template = ViewPageTemplateFile("blog.pt")
    
    def __init__(self,*kv,**kw) :
        super(Blog,self).__init__(*kv,**kw)
        
    def __call__(self) :
        return self.render()

    @property
    def values(self) :
        return IObjectQueue(self.context).values()