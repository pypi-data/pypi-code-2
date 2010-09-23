### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for productannotation viewlet

$Id: viewletproductannotation.py 52319 2009-01-13 12:34:49Z corbeau $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52319 $"
 
from ng.content.annotation.productannotation.interfaces import IProductAnnotation
from ng.lib.viewletbase import ViewletBase

class ProductAnnotationViewlet(ViewletBase) :
    def __init__(self,*kv,**kw) :
        super(ProductAnnotationViewlet,self).__init__(*kv,**kw)
        self.parent = self.context
        self.context = IProductAnnotation(self.context.ob)
