# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.publisher.interfaces.http import IHTTPRequest

from Products.CMFPlone.utils import getToolByName

from interfaces import ContentLookupError
from interfaces import IProxiedContentInfo
from interfaces import IProxiedContent
from interfaces import IContentProxiedRule

from content.interfaces import IATProxiedContent

class RequestProxiedContentInfo(object):
    
    implements(IProxiedContentInfo)
    adapts(IHTTPRequest)
    
    def __init__(self, context):
        self.context = context
        self.uid = context.get('uid')

class ATProxiedContentInfo(object):
    
    implements(IProxiedContentInfo)
    adapts(IATProxiedContent)
    
    def __init__(self, context):
        self.context = context
        self.uid = context.getProxyreference()

class ATProxiedContent(object):
    
    implements(IProxiedContent)
    adapts(IProxiedContentInfo)
    
    def __init__(self, context):
        self.context = context
    
    def content(self, context):
        uid = self.context.uid
        catalog = getToolByName(context, 'uid_catalog')
        brains = catalog({'UID': uid})
        if not brains:
            raise ContentLookupError(u'Content lookup failed for uid %s' % uid)
        return brains[0].getObject()

class BaseContentProxiedRule(object):
    """Provides some base functionality useful for rules.
    """
    
    implements(IContentProxiedRule)
    adapts(Interface, IHTTPRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._ploneview = False
    
    def __call__(self):
        raise NotImplementedError(u"Subclass must implement this function")
    
    @property
    def ploneview(self):
        if self._ploneview is False:
            self._ploneview = getMultiAdapter((self.context, self.request),
                                              name=u'plone')
        return self._ploneview
    
    @property
    def portaltype(self):
        return self.context.portal_type
    
    @property
    def template(self):
        return self.ploneview.getViewTemplateId()
    
    @property
    def currenturl(self):
        return self.ploneview.getCurrentUrl()

class DefaultContentProxiedRule(BaseContentProxiedRule):
    """Provide the default expression logic if content is proxied or not.
    """
    
    def __call__(self):
        if self.portaltype == 'ATProxiedContent' \
          or self.currenturl.find('@@proxy') != -1:
            return True
        return False