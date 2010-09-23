### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for inbody viewlet 

$Id: inbody.py 52316 2009-01-13 11:53:09Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 52316 $"

from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from ng.lib.viewletbase import ViewletBase

class InBody(ViewletBase) :
    """ Body """
    
    isobject = False
    def __init__(self,*kv,**kw) :
        super(InBody,self).__init__(*kv,**kw)
        items = self.context.values()
            