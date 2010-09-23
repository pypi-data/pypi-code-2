##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.viewlet.interfaces import IViewlet

from z3c.jsontree import interfaces
from z3c.jsontree import base


# simple trees
class SimpleJSONTree(base.TreeBase, base.PythonRenderer, 
    base.IdGenerator):
    """Simple JSON tree using inline methods for rendering elements and
    using traversable path for item lookup.
    """

    zope.interface.implements(interfaces.ISimpleJSONTree)


# simple tree viewlet
class SimpleJSONTreeViewlet(SimpleJSONTree):
    """Simple JSON tree viewlet."""

    zope.interface.implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(SimpleJSONTreeViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.manager = manager


# generic template based tree
class LITagProvider(base.ProviderBase, base.IdGenerator):
    """LI tag content provider."""

    zope.interface.implements(interfaces.ILITagProvider)
    zope.component.adapts(zope.interface.Interface, IHTTPRequest, 
        interfaces.ITemplateRenderer)


class ULTagProvider(base.ProviderBase, base.IdGenerator):
    """UL tag contet provider."""

    zope.interface.implements(interfaces.IULTagProvider)
    zope.component.adapts(zope.interface.Interface, IHTTPRequest, 
        interfaces.ITemplateRenderer)


class TreeProvider(base.ProviderBase, base.IdGenerator):
    """UL tag contet provider."""

    name = u'[top]'

    zope.interface.implements(interfaces.ITreeProvider)
    zope.component.adapts(zope.interface.Interface, IBrowserRequest, 
        interfaces.ITemplateRenderer)


class GenericJSONTree(base.TreeBase, base.TemplateRenderer, 
    base.IdGenerator):
    """Template base tree.
    
    This implementation uses IContentProvider for element tag rendering.
    This content provider are resonsible for represent a node. This allows us 
    to embed html or javascript calls in the html representation in a smart 
    way.
    """

    zope.interface.implements(interfaces.IGenericJSONTree)


# generic tree viewlet
class GenericJSONTreeViewlet(GenericJSONTree):
    """Generic JSON tree viewlet."""

    zope.interface.implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(GenericJSONTreeViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.manager = manager
