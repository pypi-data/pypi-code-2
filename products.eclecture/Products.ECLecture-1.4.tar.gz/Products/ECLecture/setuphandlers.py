# -*- coding: utf-8 -*-
# $Id: setuphandlers.py 1568 2011-06-28 22:31:28Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

import transaction

from Products.CMFCore.utils import getToolByName

from Products.ECLecture import config
from Products.ECLecture import LOG


def isNotECLectureProfile(context):
    return context.readDataFile("ECLecture_marker.txt") is None


def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotECLectureProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotECLectureProfile(context): return

    #site = context.getSite()
    reindexIndexes(context)


def installGSDependencies(context):
    """Install dependend profiles."""
    
    # Has to be refactored as soon as generic setup allows a more 
    # flexible way to handle dependencies.
    
    return


def installQIDependencies(context):
    """Install dependencies"""
    
    if isNotECLectureProfile(context): return

    site = context.getSite()

    portal = getToolByName(site, 'portal_url').getPortalObject()
    quickinstaller = portal.portal_quickinstaller
    for dependency in config.DEPENDENCIES:
        LOG.info('Installing dependency %s:' % dependency)
        quickinstaller.installProduct(dependency)
        transaction.savepoint() 


def reindexIndexes(context):
    """Reindex some indexes.

    Indexes that are added in the catalog.xml file get cleared
    everytime the GenericSetup profile is applied.  So we need to
    reindex them.

    Since we are forced to do that, we might as well make sure that
    these get reindexed in the correct order.
    """
    if isNotECLectureProfile(context): return 

    site = context.getSite()

    pc = getToolByName(site, 'portal_catalog')
    indexes = [
        'getTimePeriod',
        ]

    # Don't reindex an index if it isn't actually in the catalog.
    # Should not happen, but cannot do any harm.
    ids = [id for id in indexes if id in pc.indexes()]
    if ids:
        pc.manage_reindexIndex(ids=ids)
    
    LOG.info('Indexes %s re-indexed' % indexes)
