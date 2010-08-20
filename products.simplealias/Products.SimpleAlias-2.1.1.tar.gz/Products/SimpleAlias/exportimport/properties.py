# -*- coding: utf-8 -*-
"""
GenericSetup export/import tool properties
"""
# $Id$

#from zope.component import adapts
from zope.component import queryMultiAdapter

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.utils import getToolByName

from Products.SimpleAlias import config as sa_config


_FILENAME = 'simplealias.xml'

class SimpleAliasPropertiesXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):

    """XML im- and exporter for SimpleAlias properties.
    """
    # adapts(IAliasTool, ISetupEnviron)

    _LOGGER_ID = 'simplealias.properties'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        self._encoding = self.context.getProperty('default_charset', 'utf-8')

        node = self._doc.createElement('site')
        node.appendChild(self._extractProperties())

        self._logger.info('SimpleAlias properties exported.')
        return node


    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        for child in node.childNodes:
            if child.nodeName != 'property':
                continue
            if child.getAttribute('name') != 'default_charset':
                continue
            self._encoding = self._getNodeText(child) or 'utf-8'
            break

        if self.environ.shouldPurge():
            self._purgeProperties()

        self._initProperties(node)

        self._logger.info('SimpleAlias properties imported.')


def importToolProperties(context):
    """Import SimpleAlias properties from an XML file"""

    logger = context.getLogger('simplealias.properties')
    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    site = context.getSite()
    tool = getToolByName(site, sa_config.TOOL_ID)

    importer = queryMultiAdapter((tool, context), IBody)
    if importer is None:
        logger.warning('Import adapter missing.')
        return

    importer.body = body


def exportToolProperties(context):
    """Import SimpleAlias properties from an XML file"""

    site = context.getSite()
    tool = getToolByName(site, sa_config.TOOL_ID, None)
    if tool is None:
        return

    logger = context.getLogger('simplealias.properties')

    exporter = queryMultiAdapter((tool, context), IBody)
    if exporter is None:
        logger.warning('Export adapter missing.')
        return

    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
