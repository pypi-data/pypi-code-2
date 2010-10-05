##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Some basic traversers for REST

$Id: traverser.py 82207 2007-12-09 04:38:37Z srichter $
"""
import zope.interface
from z3c.rest import interfaces, null
from z3c.traverser import traverser
from z3c.traverser.interfaces import ITraverserPlugin
from zope.app.container.interfaces import IItemContainer
from zope.publisher.interfaces import NotFound


class RESTPluggableTraverser(traverser.BasePluggableTraverser):
    """A simple REST-compliant pluggable traverser."""


class ContainerItemTraverserPlugin(object):
    """A traverser that knows how to look up objects by name in a container."""
    zope.interface.implements(ITraverserPlugin)
    zope.component.adapts(IItemContainer, interfaces.IRESTRequest)

    def __init__(self, container, request):
        self.context = container
        self.request = request

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        try:
            return self.context[name]
        except KeyError:
            return self.nullResource(request, name)

    def nullResource(self, request, name):
        # we traversed to something that doesn't exist.

        # The name must be the last name in the path, so the traversal
        # name stack better be empty:
        if request.getTraversalStack():
            raise NotFound(self.context, name, request)

        # This should only happen for a PUT:
        if request.method != 'PUT':
            raise NotFound(self.context, name, request)

        return null.NullResource(self.context, name)
