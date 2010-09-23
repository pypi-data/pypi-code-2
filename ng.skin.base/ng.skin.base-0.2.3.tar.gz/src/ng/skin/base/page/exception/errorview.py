### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ErrorView - is base class for zope3 errors

$Id: errorview.py 52231 2008-12-27 21:08:17Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 52231 $"

from zope.publisher.browser import BrowserView
from zope.app.exception.systemerror import SystemErrorView
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app import zapi
from zope.app.container.interfaces import IContainer
from ng.adapter.requestcache.interfaces import IRequestCache

class ErrorView(BrowserView,SystemErrorView):
    """Class for errorpage view"""

    def __init__(self,context,request) :
        super(ErrorView,self).__init__(context,request)
        IRequestCache(request).nocache()

    @property
    def mainurl(self) :
        return absoluteURL(zapi.getUtility(
            IContainer,
            name="Main"),self.request)

    @property
    def returnurl(self) :
        url = self.request.form.get('returnurl',self.request.get('HTTP_REFERER',None)) 
        if url :
            return url
        raise KeyError            

class UnauthorizedView(ErrorView):
    """Class for errorpage view"""

    def __init__(self,context,request) :
        super(UnauthorizedView,self).__init__(context,request)
        request.response.setStatus(401)
        request.response.addHeader("WWW-Authenticate",'basic realm="Zope"')
            
class RedirectView(ErrorView) :
    """Class for redirect view """
    def __init__(self,context,request) :
        super(RedirectView,self).__init__(context,request)
        request.response.redirect(context.url)

    def __call__(self,*kv) :
      return "Please, wait"
      