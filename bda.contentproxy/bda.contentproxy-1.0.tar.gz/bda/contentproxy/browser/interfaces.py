# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import Attribute

class IProxyView(Interface):
    """Interface for the proxy view.
    """
    
    content = Attribute(u"The proxied content")

class IContentProxied(Interface):
    """Interface to check wether the actual content is proxied or not.
    
    It is needed by the kss registry to check wether at.kss should be loaaded.
    """
    
    def __call__():
        """Return flag wether wether the actual content is proxied or not.
        """