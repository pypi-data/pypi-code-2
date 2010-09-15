# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import Attribute

class ContentLookupError(Exception): pass

class IProxiedContentInfo(Interface):
    """Interface providing information for proxied content
    """
    
    uid = Attribute(u"The uid of the proxied content")

class IProxiedContent(Interface):
    """Interface providing the content for proxying
    """
    
    def content(context):
        """Return the proxied content.
        
        @param context - the context to look up the catalog.
        @return content - the proxied content
        """

class IContentProxiedRule(Interface):
    """Interface to define a rule if the current displayed context contains
    proxied contents and therefor should avoid to load at.kss. a multi adapter
    for this interface is looked up by the .browser.IContentProxied
    implementation.
    """
    
    def __call__():
        """Return flag wether displayed context contains proxied contents.
        """