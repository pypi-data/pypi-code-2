# -*- coding: utf-8 -*-
# $Id: alias.py 123908 2010-08-20 10:27:22Z glenfant $

from zope.interface import Interface

class IAlias(Interface):
    """Marker interface for the type"""
    pass

class IAliasTool(Interface):
    """Marker interface for SimpleAlias tool"""

class IAliasLinkedTo(Interface):
    """
    Marker interface for objects that Alias' link to.
    """
    pass

__all__ = ('IAlias', 'IAliasTool','IAliasLinkedTo')