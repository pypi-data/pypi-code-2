### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for form used to add comment

$Id: addcomment.py 51511 2008-08-22 22:45:59Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50545 $"

from zope.interface import implements
from zope.schema import getFieldNames

from zope.proxy import removeAllProxies
from ng.content.comment.interfaces import IComment, ICommentAnnotation
from ng.content.comment.comment import Comment
from zope.traversing.browser import absoluteURL

class AddComment(object) :
    def getData(self,*kv,**kw) :
        return [ (x,IComment[x].default) for x in  getFieldNames(IComment)]

    def setData(self,d,**kw) :
        comment = Comment()
        container = removeAllProxies(ICommentAnnotation(self.context))        

        if not ICommentAnnotation(container).isallow :
            raise ValueError

        try :
          num = int(container.keys()[-1])
        except (IndexError,TypeError,UnicodeEncodeError) :
          num = 1
        else :                    
          while "%06u" % num in container :
            num += 1
            
        title = "%06u" % num
          
        container[title] = comment
        comment.__name__ = title
        comment.__parent__ = container
        
        for x in getFieldNames(IComment) :
            if x in d :
              setattr(comment,x,d[x])
              
            comment.author = self.request.principal.id
            
        self.request.response.redirect(absoluteURL(self.context,self.request))
        return "Added"

