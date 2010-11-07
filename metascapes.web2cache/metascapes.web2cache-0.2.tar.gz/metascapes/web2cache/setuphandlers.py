# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2010 by unknown <unknown>
# Generator: ArchGenXML Version 2.5
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('metascapes.web2cache: setuphandlers')
from metascapes.web2cache.config import PROJECTNAME
from metascapes.web2cache.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction

def isNotMetascapesWeb2CacheProfile(context):
    return context.readDataFile("web2cache_marker.txt") is None

def setupHideToolsFromNavigation(context):
    """hide tools"""
    if isNotMetascapesWeb2CacheProfile(context): return 
    # uncatalog tools
    site = context.getSite()
    toolnames = ['portal_web2cache']
    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    if navtreeProperties.hasProperty('idsNotToList'):
        for toolname in toolnames:
            try:
                portal[toolname].unindexObject()
            except:
                pass
            current = list(navtreeProperties.getProperty('idsNotToList') or [])
            if toolname not in current:
                current.append(toolname)
                kwargs = {'idsNotToList': current}
                navtreeProperties.manage_changeProperties(**kwargs)



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotMetascapesWeb2CacheProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMetascapesWeb2CacheProfile(context): return 
    site = context.getSite()
