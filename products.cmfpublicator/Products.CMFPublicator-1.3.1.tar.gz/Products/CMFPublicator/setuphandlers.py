# -*- coding: utf-8 -*-
from zope import component
import logging
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup import interfaces as gsinterfaces
from Products.GenericSetup.upgrade import listUpgradeSteps

from Products.ZCatalog.ProgressHandler import ZLogHandler

try:
    from Products.CacheSetup import interfaces
    from Products.CacheSetup.enabler import enableCacheFu
    CACHEFU = True
except ImportError:
    CACHEFU = False

_PROJECT = 'Products.CMFPublicator'
_PROFILE_ID = 'Products.CMFPublicator:default'

def doUpgrades(context):
    ''' If exists, run migrations
    '''
    if context.readDataFile('Products.CMFPublicator.txt') is None:
        return
    logger = logging.getLogger(_PROJECT)
    site = context.getSite()
    setup_tool = getToolByName(site,'portal_setup')
    cache = CACHEFU and getToolByName(context,'portal_cache_settings',None)
    version = setup_tool.getLastVersionForProfile(_PROFILE_ID)
    upgradeSteps = listUpgradeSteps(setup_tool,_PROFILE_ID, version)
    sorted(upgradeSteps,key=lambda step:step['sortkey'])

    if cache:
        # Desabilitamos o cache fu para nao termos uma enxurrada
        # de purges
        cache.setEnabled(False)

    for step in upgradeSteps:
        oStep = step.get('step')
        if oStep is not None:
            oStep.doStep(setup_tool)
            msg = "Ran upgrade step %s for profile %s" % (oStep.title,
                                                          _PROFILE_ID)
            setup_tool.setLastVersionForProfile(_PROFILE_ID, oStep.dest)
            logger.info(msg)

    if cache:
        # Novamente habilitamos o cache fu para nao termos uma enxurrada
        # de purges
        cache.setEnabled(True)

def add_publicator_box(portal):
    portal_publicator = getToolByName(portal, 'portal_publicator')
    boxes = portal_publicator.getPublicationBoxes()
    ids_boxes = []
    for box in boxes:
        ids_boxes.append(box.id)

    if 'news' not in ids_boxes:
        portal_publicator.addPublicationBox(id='news',
                                            name='News',
                                            content_type=['News Item'],
                                            n_items=5,
                                            search_states=['published'])

def setupVarious(context):
    if context.readDataFile('Products.CMFPublicator.txt') is None:
        return
    
    portal = context.getSite()
    add_publicator_box(portal)
    