### -*- coding: utf-8 -*- #############################################
#######################################################################
"""View Adapter used to get view with one word random selected
from the index.

$Id: viewword.py 50545 2008-02-06 09:00:53Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.interface import Interface
from ng.app.converter.object2psadapter.interfaces import IPropertySheet
from zope.publisher.browser import BrowserView
from random import choice
from zc.catalog.interfaces import IIndexValues
from zope.app.zapi import getUtility
        
class WordView(BrowserView) :
    def __init__(self,*kv,**kw) :
        super(WordView,self).__init__(*kv,**kw)

    def word(self) :
        try :
            return choice(list(getUtility(IIndexValues, name='keyword',context=self.context).values()))
        except IndexError :
            return ""                
        
        
