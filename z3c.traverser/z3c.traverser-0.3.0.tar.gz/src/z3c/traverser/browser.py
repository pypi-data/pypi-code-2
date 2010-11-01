##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Pluggable Browser Traverser

$Id: browser.py 97974 2009-03-12 09:31:25Z nadako $
"""
__docformat__ = "reStructuredText"
from zope.component import getSiteManager
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements, providedBy
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IBrowserPublisher

from z3c.traverser.traverser import PluggableTraverser

# copy the function from zope.app.publisher not to depend on it
def getDefaultViewName(object, request):
    name = getSiteManager().adapters.lookup(
        (providedBy(object), providedBy(request)), IDefaultViewName)
    if name is not None:
        return name
    raise ComponentLookupError("Couldn't find default view name",
                               object, request)

class PluggableBrowserTraverser(PluggableTraverser):

    implements(IBrowserPublisher)

    def browserDefault(self, request):
        """See zope.publisher.browser.interfaces.IBrowserPublisher"""
        view_name = getDefaultViewName(self.context, request)
        view_uri = "@@%s" % view_name
        return self.context, (view_uri,)
