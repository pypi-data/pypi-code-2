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
$Id: eggs.py 1397 2009-05-19 01:55:08Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL

import z3c.pagelet.browser
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

import mypypi.api

class Eggs(z3c.pagelet.browser.BrowserPagelet):
    """Eggs - flat list of all available eggs"""

    layout = getLayoutTemplate('simple')
    template = getPageTemplate()

    @property
    def links(self):
        rv = []
        for name, pkg in self.context.items():
            if mypypi.api.checkViewPermission(pkg) and pkg.isPublished:
                for rname, rel in pkg.items():
                    if mypypi.api.checkViewPermission(rel) and rel.isPublished:
                        for fname, fle in rel.items():
                            rv.append({'name':fname,
                                       'url': absoluteURL(fle, self.request)})
        return rv

    def render(self):
        return self.template()

class PrivateEggs(Eggs):
    """Flat list of packages, but authorization first
    """