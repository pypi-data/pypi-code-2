#############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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

from z3c.hashedresource import interfaces
from zope.component import adapts
from zope.interface import implements, implementsOnly, directlyProvides
from zope.traversing.browser.interfaces import IAbsoluteURL
import zope.app.publisher.browser.resource
import zope.publisher.interfaces.browser
import zope.traversing.browser.absoluteurl
try:
    from zope.app.publisher.interfaces import IResource
except ImportError:
    from zope.component.interfaces import IResource


class HashingURL(zope.traversing.browser.absoluteurl.AbsoluteURL):
    """Inserts a hash of the contents into the resource's URL,
    so the URL changes whenever the contents change, thereby forcing
    a browser to update its cache.
    """

    implementsOnly(IAbsoluteURL)
    adapts(IResource, interfaces.IHashedResourceSkin)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        # XXX duplicated from zope.app.publisher.browser.resource.AbsoluteURL
        self.name = self.context.__name__
        if self.name.startswith('++resource++'):
            self.name = self.name[12:]

    def _site_url(self):
        url = zope.app.publisher.browser.resource.AbsoluteURL(
            self.context, self.request)()
        return url.split('/@@/')[0]

    def __str__(self):
        hash = str(interfaces.IResourceContentsHash(self.context))
        return "%s/++noop++%s/@@/%s" % (self._site_url(), hash, self.name)
