##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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

from zope.traversing import api
from zope.app.component import hooks

from z3c.jsontree.browser import tree


class SiteManagerTreeViewlet(tree.SimpleJSONTreeViewlet):
    """Navigation tree starting at site management."""

    z3cJSONTreeId = u'zamPluginSiteManagerTree'
    z3cJSONTreeName = u'zamPluginSiteManagerTree'

    @property
    def title(self):
        return self.__name__

    def getRoot(self):
        site = hooks.getSite()
        if not self.root:
            self.root = site.getSiteManager()
        return self.root

    def render(self):
        super(SiteManagerTreeViewlet, self).update()
        return self.tree

