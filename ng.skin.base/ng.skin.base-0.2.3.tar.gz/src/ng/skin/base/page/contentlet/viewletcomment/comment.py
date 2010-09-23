### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for content viewlet

$Id: comment.py 52406 2009-01-29 13:37:07Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from ng.lib.viewletbase import ViewletBase
from ng.content.comment.interfaces import ICommentAnnotation
from zope.app.zapi import getUtility
from zope.app.catalog.interfaces import ICatalog

class Comment(ViewletBase) :
    """ Content """

    @property    
    def comments(self) :
        return ICommentAnnotation(self.context)

    def profile(self,author) :
      for profile in getUtility(ICatalog,context=self.context) \
                          .searchResults(
                              profile=( author, author )
                          ) :
          return profile                          
      return None
                