# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from zope.component import getMultiAdapter

from Products.Five import BrowserView

from bda.contentproxy.interfaces import IProxiedContentInfo
from bda.contentproxy.interfaces import IProxiedContent
from bda.contentproxy.interfaces import IContentProxiedRule

from interfaces import IProxyView
from interfaces import IContentProxied

class ProxiedContentView(BrowserView):
    
    implements(IProxyView)
    
    @property
    def content(self):
        info = IProxiedContentInfo(self.request)
        content = IProxiedContent(info)
        return content.content(self.context)

class ATProxiedContentView(BrowserView):
    
    implements(IProxyView)
    
    @property
    def content(self):
        info = IProxiedContentInfo(self.context)
        content = IProxiedContent(info)
        return content.content(self.context)

class ContentProxied(BrowserView):
    
    implements(IContentProxied)
    
    def __call__(self):
        rule = getMultiAdapter((self.context, self.request),
                               IContentProxiedRule)
        return rule()   