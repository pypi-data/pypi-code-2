### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Rediect to profile mixin class

$Id: home.py 51470 2008-08-02 21:28:54Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51325 $"

from ng.content.comment.interfaces import ICommentAnnotation
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL

class Home(object) :
    
    def __call__(self) :
        for profile in getUtility(ICatalog,context=self.context) \
                          .searchResults(
                              profile=( self.request.principal.id, self.request.principal.id )
                          ) :
            self.request.response.redirect(adaptiveURL(profile,self.request)+"/")
                 
        return "Unknown profile"