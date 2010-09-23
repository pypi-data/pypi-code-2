### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Factories for article class used in wiki

$Id: dictionaryitem.py 50550 2008-02-06 12:54:07Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 50550 $"
 
from zope.interface import implements
from ng.content.article.article.article import  Article
from ng.content.annotation.annotationswitcher.demo.interfaces import IAnnotationSwitcherDict 

from zope.security.proxy import removeSecurityProxy
from zope.interface import alsoProvides

def DictionaryItem(context,*kv,**kw) :
    article = Article(*kv,**kw)
    alsoProvides(article, IAnnotationSwitcherDict)
    return article
    
    
    