### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Next-Previous view adapter class

$Id: nextprev.py 51808 2008-10-02 15:08:14Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51808 $"

from zope.publisher.browser import BrowserView    
from zope.interface import implements,Interface
from interfaces import INextPrev
from ng.adapter.pager.interfaces import  IPagerSource
from ng.content.article.maincontainer.interfaces import IMainPage
from ng.content.article.interfaces import IContentContainer
from zope.app.zapi import absoluteURL,getMultiAdapter

class NextPrev(BrowserView) :
    __doc__ = __doc__
    implements(INextPrev)
    prev = None
    next = None
    
    def __init__(self,*kv,**kw) :
        super(NextPrev,self).__init__(*kv,**kw)
        up = IPagerSource(IContentContainer(self.up))

        keys = up.keys()
        index = keys.index(self.context.__name__)

        if index :
            self.prev = self.up[keys[index-1]]

        if index < len(keys)-1 :
            self.next = self.up[keys[index+1]]

    @property
    def up(self) :
        if not IMainPage.providedBy(self.context) :
            return self.context.__parent__
        return None    
