# takeaction: content as actions
# Copyright (C) 2007 Jarn AS
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from zope.component import adapts

from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.utils import getToolByName

from interfaces import ITakeActionTool

class TakeActionToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML im- and exporter for TakeActionTool"""
    
    adapts(ITakeActionTool, ISetupEnviron)

    _LOGGER_ID = 'takeaction'

    name = 'takeaction'

    def _exportNode(self):
        """Export the object as a DOM node"""
        
        node = self._getObjectNode('object')
        node.appendChild(self._extractActionItems())

        self._logger.info('TakeAction tool exported.')
        
        return node

    def _importNode(self, node):
        """Import the object from the DOM node"""
        
        if self.environ.shouldPurge():
            self._purgeActionItems()

        self._initActionItems(node)

        self._logger.info('TakeAction tool imported.')
        
    def _extractActionItems(self):
        fragment = self._doc.createDocumentFragment()
        
        for item in self.context._items:
            node = self._doc.createElement('item')
            node.setAttribute('path', item.path)
            node.setAttribute('category', item.category)
            fragment.appendChild(node)
            
        return fragment
    
    def _purgeActionItems(self):
        self.context._items = ()
    
    def _initActionItems(self, node):
        from Products.takeaction.takeaction import TakeActionItem
        items = list(self.context._items)
        indexes = dict(((item.path, item.category), i)
                       for i, item in enumerate(items))
        
        for child in node.childNodes:
            if child.nodeName != 'item':
                continue
            item = TakeActionItem(str(child.getAttribute('path')),
                                  str(child.getAttribute('category')))
            index = indexes.get((item.path, item.category), None)
            if index is None:
                indexes[(item.path, item.category)] = len(items)
                items.append(item)
            else:
                items[index] = item
            
        self.context._items = tuple(items)

def importTakeActionTool(context):
    """Import TakeAction tool settings from an XML file.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_takeaction')

    importObjects(tool, '', context)

def exportTakeActionTool(context):
    """Export TakeAction tool settings as an XML file.
    """
    site = context.getSite()
    tool = getToolByName(site, 'portal_takeaction', None)
    if tool is None:
        logger = context.getLogger('takeaction')
        logger.info('Nothing to export.')
        return

    exportObjects(tool, '', context)

# Patch the actions GS step to allow portal_takeaction in actions.xml as well. 
# Sigh. No longer needed in recent CMFCore versions, luckily.
from Products.CMFCore.exportimport import actions
if hasattr(actions, '_SPECIAL_PROVIDERS'):
    special = set(actions._SPECIAL_PROVIDERS)
    special.add('portal_takeaction')
    actions._SPECIAL_PROVIDERS = tuple(special)

