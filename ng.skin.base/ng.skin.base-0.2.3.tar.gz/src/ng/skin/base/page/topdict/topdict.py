### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for toplological sorted dictionary view

$Id: topdict.py 50545 2008-02-06 09:00:53Z cray $
"""
__author__  = "Andrey Orlov 2006 12 05"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

import zope.component
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog
from ng.content.annotation.dictannotation.interfaces import IDictAnnotation
from pd.lib.topsort import TopSortFuzzy
from zope.security.proxy import removeSecurityProxy
from zope.app.intid.interfaces import IIntIds

class TopSortFuzzyContainer(TopSortFuzzy) :
    def __call__(self,context) :
        intids = getUtility(IIntIds)         
        search = getUtility(ICatalog, name="catalog",context=context).searchResults
        oids = dict([(intids.getId(ob),ob) for ob in  context.values()])
        
        return (
            oids[oid] for oid in 
                super(TopSortFuzzyContainer,self).__call__([
                    (
                        oid,
                        [uid for uid in
                           search(backkeyword={'any_of':IDictAnnotation(ob).keyword}).uids
                           if uid in oids
                        ]
                    ) for oid,ob in oids.iteritems()
                ])
        )

class TopDict(object) :
    def __init__(self,context,request) :
        super(TopDict,self).__init__(context,request)

    def items(self) :
        return TopSortFuzzyContainer()(self.context)
                                                    
    def updateOrder(self,*kv,**kw) :
        self.context.updateOrder([x.__name__ for x in TopSortFuzzyContainer()(self.context)])
        return getattr(self,'index.html')(*kv,**kw)
        
                    
        
