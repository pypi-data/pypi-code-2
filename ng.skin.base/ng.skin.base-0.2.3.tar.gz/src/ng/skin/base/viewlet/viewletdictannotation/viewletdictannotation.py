### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for dictannotation viewlet

$Id: viewletdictannotation.py 52317 2009-01-13 12:02:30Z corbeau $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52317 $"
 
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation
from ng.lib.viewletbase import ViewletBase

class DictAnnotationViewlet(ViewletBase) :
    def __init__(self,*kv,**kw) :
        super(DictAnnotationViewlet,self).__init__(*kv,**kw)
        self.parent = self.context
        self.context = IDictAnnotation(self.context.ob)
