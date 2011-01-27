###############################################################################
#
# Copyright 2003-2004 by Projekt01 GmbH, CH-Cham
#
###############################################################################
"""
$Id: app.py 165 2006-11-24 13:08:56Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

from zope.viewlet import viewlet
from zope.traversing import api
from z3c.jsontree.browser import tree


ZAMPluginNavigationJavaScriptViewlet = viewlet.JavaScriptViewlet(
    'zamplugin.navigation.js')


class TreeViewlet(tree.SimpleJSONTreeViewlet):
    """Navigation tree starting at the ZODB root as root."""

    z3cJSONTreeId = u'zamPluginTree'
    z3cJSONTreeName = u'zamPluginTree'

    @property
    def title(self):
        return self.__name__

    def getRoot(self):
        if not self.root:
            self.root = api.getRoot(self.context)
        return self.root

    def render(self):
        super(TreeViewlet, self).update()
        return self.tree
