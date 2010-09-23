### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for undefined page provide list all references on unknown
documents

$Id: undefined.py 53383 2009-07-06 11:36:15Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 53383 $"
 
from zope.interface import implements
from zc.catalog.interfaces import IIndexValues
from zope.app.catalog.interfaces import ICatalog
from zope.app.zapi import getUtility
from zope.app.intid.interfaces import IIntIds
from ng.adapter.path.interfaces import IPath
from urllib import quote
import re

class UnDefinedByLinks(object) :

    def init(self,backindexname,indexname) : 
        path=IPath(self.context).path
        return (
            getUtility(IIndexValues, context=self.context, name=backindexname),
            getUtility(ICatalog,context=self.context),
            (path,path+u'\xff')
            )

    def undefined(self,backindexname,indexname) :
        index, catalog, urlpath = self.init(backindexname,indexname)
             
        for keyword in sorted(index.values()) :
            qk = re.sub("\s+"," ",keyword.strip())
            query = (qk,qk.lower())

            if len(catalog.searchResults(**{indexname:{'any_of':query}})) == 0 :
                docs = catalog.searchResults(**{backindexname:{'any_of': query}, 'urlpath':urlpath})
                if bool(docs) :
                    yield {
                        'keyword' : keyword, 
                        'document' : docs,
                        'query' : quote(str(keyword))
                        }
    
    @property
    def keyword(self) :
        return self.undefined('backkeyword','keyword')
                    
    @property
    def name(self) :
        return self.undefined('backname','name')            
            

class UnDefinedByDocs(UnDefinedByLinks):
    def undefined(self,backindexname,indexname) :
        index, catalog, urlpath = self.init(backindexname,indexname)
        intid = getUtility(IIntIds,context=self.context)

        for doc_id in catalog.apply({'urlpath':urlpath}) :
            keywords = []
            for keyword in index.values(doc_id=doc_id) :
                qk = re.sub("\s+"," ",keyword.strip())
                query = (qk,qk.lower())
                              
                if len(catalog.searchResults(**{indexname:{'any_of': query}})) == 0 :
                    keywords.append(keyword)

            if keywords :
                yield {
                    'keywords' : [ {'keyword':x, 'query': quote(str(x))} for x in sorted(keywords) ],
                    'document' : intid.getObject(doc_id)
                }                
    