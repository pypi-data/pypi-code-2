# -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb - all rights reserved
## No publication or distribution without authorization.
"""
Generic Setup handlers
"""
import logging

from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.CMFCore.utils import getToolByName

from Products.LinguaFace.config import TOOL_ID, PROJECTNAME
from Products.LinguaFace.interface import ILinguaFaceTool


class ToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """
    XML import/export for PlonePlusTool
    """

    __used_for__ = ILinguaFaceTool

    _LOGGER_ID = PROJECTNAME

    name = 'ploneplus'

    def _exportNode(self):
        """Export the object as a DOM node.
        """

        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())

        self._logger.info('LinguaFaceTool exported.')
        return node


    def _importNode(self, node):
        """Import the object from the DOM node.
        """

        if self.environ.shouldPurge():
            self._purgeProperties()

        self._initProperties(node)

        self._logger.info('LinguaFaceTool imported.')


def importLinguaFaceTool(context):
    """Import linguaface tool settings from an XML file.
    """

    site = context.getSite()
    tool = getToolByName(site, TOOL_ID)
    importObjects(tool, '', context)


def exportLinguaFaceTool(context):
    """Export linguaface tool settings as an XML file.
    """

    site = context.getSite()
    tool = getToolByName(site, TOOL_ID, None)
    if tool is None:
        logger = logging.getLogger(PROJECTNAME)
        logger.info('Nothing to export.')
        return

    exportObjects(tool, '', context)
