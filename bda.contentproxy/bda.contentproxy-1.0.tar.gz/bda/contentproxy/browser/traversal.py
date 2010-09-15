# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from zope.component import adapts

from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from ZPublisher.BaseRequest import DefaultPublishTraverse

from interfaces import IProxyView

class UIDTraverser(DefaultPublishTraverse):
    
    implements(IBrowserPublisher)
    adapts(IProxyView, IDefaultBrowserLayer)
    
    def publishTraverse(self, request, name):
        request['uid'] = name
        return self.context