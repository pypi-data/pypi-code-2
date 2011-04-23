#!/usr/bin/env python
# encoding: utf-8
"""
exportimport.py

Created by Manabu Terada on 2011-04-22.
Copyright (c) 2011 CMScom. All rights reserved.
"""
from zope.component import queryUtility
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase

from c2.app.issuelink.controlpanel.interfaces import IIssuelinkConfig


class ConfigXMLAdapter(XMLAdapterBase):

    _LOGGER_ID = 'c2.app.issuelink'
    name = 'issuelink' # TODO: 本当に必要？

    def _exportNode(self):
        """ export the object as a DOM node """
        node = self._extractProperties()
        self._logger.info('settings exported.')
        return node

    def _importNode(self, node):
        """ import the object from the DOM node """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        self._logger.info('settings imported.')

    def _purgeProperties(self):
        self.context.use_issuelink = False
        self.context.issuetracker_url = ""
        self.context.link_rules = []

    def _initProperties(self, node):
        elems = node.getElementsByTagName('settings')
        if elems:
            assert len(elems) == 1
            settings = elems[0]
            for child in settings.childNodes:
                if child.nodeName == 'use_issuelink':
                    value = bool(int(child.getAttribute('value')))
                    self.context.use_issuelink = value
                elif child.nodeName == 'issuetracker_url':
                    value = str(child.getAttribute('value'))
                    self.context.issuetracker_url = value
                elif child.nodeName == 'link_rules':
                    value = str(child.getAttribute('value'))
                    self.context.link_rules = self._convertToList(value)


    def _createNode(self, name, value):
        node = self._doc.createElement(name)
        node.setAttribute('value', value)
        return node

    def _extractProperties(self):
        node = self._doc.createElement('object')
        node.setAttribute('name', 'spellchecker')
        settings = self._doc.createElement('settings')
        create = self._createNode
        node.appendChild(settings)
        append = settings.appendChild
        append(create('use_issuelink', str(self.context.use_issuelink)))
        append(create('issuetracker_url', str(self.context.issuetracker_url)))
        append(create('link_rules', str(self.context.link_rules)))
        return node

    def _convertToList(self, value):
        assert isinstance(value, basestring)
        if not isinstance(value, unicode):
            value = value.decode('utf-8')
        values = value.split(u",")
        return values

def importSettings(context):
    """ import settings from an XML file """
    site = context.getSite()
    utility = queryUtility(IIssuelinkConfig, context=site)
    if utility is None:
        logger = context.getLogger('c2.app.issuelink')
        logger.info('Nothing to import.')
        return
    importObjects(utility, '', context)


def exportSettings(context):
    """ export settings as an XML file """
    site = context.getSite()
    utility = queryUtility(IIssuelinkConfig, context=site)
    if utility is None:
        logger = context.getLogger('c2.app.issuelink')
        logger.info('Nothing to export.')
        return
    exportObjects(utility, '', context)
