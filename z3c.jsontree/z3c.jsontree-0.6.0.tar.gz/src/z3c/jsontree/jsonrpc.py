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
__docformat__ = 'restructuredtext'

from zope.traversing.browser import absoluteURL

from z3c.jsonrpc.publisher import MethodPublisher

from z3c.jsontree.interfaces import JSON_TREE_ID
from z3c.jsontree.interfaces import JSON_TREE_VIEW_NAME
from z3c.jsontree import base
from z3c.jsontree import subitem
from z3c.jsontree import util


class NoneJSONTreeItems(MethodPublisher, base.IdGenerator):
    """Returns no items.
    
    Default JSON adapter for all objects.
    """

    def loadJSONTreeItems(self, id):
        """Returns child information for the object with the given path in a 
        JSON format."""
        return {'treeChilds': {'id':id, 'childs':[]}}


class JSONTreeItems(subitem.SubItemAware, MethodPublisher,
    base.IdGenerator):
    """Returns the data of the childs from the path for the json tree.
    
    This is a simple implementation which uses the traversal concept.
    If you need to lookup items for other conponents then containers,
    e.g. for a widget, you need to implement your own child loader class.
    
    This is the default JSON adapter for IReadContainer.
    """

    viewName = JSON_TREE_VIEW_NAME
    z3cJSONTreeId = JSON_TREE_ID
    linkHandler = ''

    def getIconURL(self, item, request, name='icon'):
        return util.getIconURL(item, request, name=name)

    def loadJSONTreeItems(self, id):
        """Returns child information for the object with the given path in a 
        JSON format."""
        res = {}
        childs = []
        append = childs.append

        for name, subItem, hasSubItems in self.getSubItems(self.context):

            if hasSubItems:
                hasChilds = True
            else:
                hasChilds = False

            info = {}
            url = absoluteURL(subItem, self.request)
            info['id'] = self.getId(subItem)
            info['content'] = name
            info['url'] = url +'/'+ self.viewName
            info['iconURL'] = util.getIconURL(subItem, self.request)
            info['linkHandler'] = self.linkHandler
            info['hasChilds'] = hasChilds
            info['contextURL'] = url
            append(info)
        
        res['treeChilds'] = {'id':id, 'childs':childs}
        
        return res
