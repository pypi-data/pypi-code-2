### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The newspage MixIn to view class.

$Id: linkview.py 51331 2008-07-10 06:23:56Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51331 $"

from ng.app.rubricator.algorithm.base.interfaces import IRubricateAble
from docshortview import Proxy

class LinkView(object):
    
    def __init__(self,context,request) :
        self.request = request
        super(LinkView, self).__init__(context, request)
        self.context = Proxy(IRubricateAble(context))

            