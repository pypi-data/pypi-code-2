### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for eventannotation viewlet

$Id: viewleteventannotation.py 52317 2009-01-13 12:02:30Z corbeau $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52317 $"

from ng.content.annotation.eventannotation.interfaces import IEventAnnotation
from ng.lib.viewletbase import ViewletBase

class EventAnnotationViewlet(ViewletBase) :
    def __init__(self,*kv,**kw) :
        super(EventAnnotationViewlet,self).__init__(*kv,**kw)
        self.context = IEventAnnotation(self.context.ob)
