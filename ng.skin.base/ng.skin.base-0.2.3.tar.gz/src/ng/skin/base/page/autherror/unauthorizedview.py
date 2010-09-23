### -*- coding: utf-8 -*- #############################################
#######################################################################
"""UnauthorizedView - special view to enter credentials

$Id: unauthorizedview.py 52225 2008-12-27 19:02:19Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49544 $"

from ng.skin.base.page.exception.errorview import ErrorView

class UnauthorizedView(ErrorView):
    """Class for errorpage view"""
    def __init__(self,context,request) :
        super(UnauthorizedView,self).__init__(context,request)
        if request.has_key('dologin') :
          request.response.setStatus(401)
          request.response.addHeader("WWW-Authenticate",'basic realm="Zope"')
            