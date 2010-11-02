##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.publisher.interfaces import NotFound
from zope.traversing.browser import absoluteURL

import z3c.pagelet.browser
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

import mypypi.api


class SimpleIndex(z3c.pagelet.browser.BrowserPagelet):
    """Simple (package links) index."""

    layout = getLayoutTemplate('simple')
    template = getPageTemplate()

    def publishTraverse(self, request, name):
        # make this view traversable, this allows us to traverse to the pkg
        pkg = self.context.get(name)
        if pkg is None:
            if '-' in name:
                name = name.replace('-', '_')
                pkg = self.context.get(name)

                if pkg is None:
                    raise NotFound(self, name, request)
            else:
                raise NotFound(self, name, request)
        # get the index.html view for this package
        view = zope.component.queryMultiAdapter((pkg, request),
            name='simpleDetail')
        if view is None:
            raise NotFound(self, name, request)
        return view

    @property
    def links(self):
        simpleURL = '%s/simple' % absoluteURL(self.context, self.request)
        return [{'name':name, 'url': '%s/%s' % (simpleURL, name)}
                for name, pkg in self.context.items()
                if mypypi.api.checkViewPermission(pkg) and pkg.isPublished]

    def render(self):
        return self.template()

class PrivateIndex(SimpleIndex):
    """Simple (package links) index.
    this one requires authentication while SimpleIndex not"""

    layout = getLayoutTemplate('simple')
    template = getPageTemplate()

class SimpleDetail(z3c.pagelet.browser.BrowserPagelet):
    """Simple (release links) detail page."""

    layout = getLayoutTemplate('simple')
    template = getPageTemplate()

    @property
    def name(self):
        return self.context.__name__

    @property
    def links(self):
        res = []
        for release in self.context.values():
            releaseURL = absoluteURL(release, self.request)
            res += [{'name': rFile.__name__, 'url': '%s/%s' % (
                    releaseURL, rFile.__name__)}
                    for rFile in release.values()
                    if mypypi.api.checkViewPermission(rFile)]
        return res

    def render(self):
        return self.template()