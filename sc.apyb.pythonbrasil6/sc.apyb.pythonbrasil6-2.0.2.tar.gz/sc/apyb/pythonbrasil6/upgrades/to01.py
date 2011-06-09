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

def upgrade0to1(context):
    ''' Upgrade to version 1.0
    '''
    setup = getToolByName(context, 'portal_setup')
    migration = getToolByName(context,'portal_migration')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    qi = getToolByName(context,'portal_quickinstaller')
    
    logger = logging.getLogger('sc.apyb.pythonbrasil6')
    logger.info('Inicia upgrade')
    migration.upgrade()
    
    # Install dependencies for this upgrade
    dependencies = [
                    ('Products.ATGoogleVideo',0,0,'Products.ATGoogleVideo:default'),
                    ('Products.PyConBrasil',0,0,'Products.PyConBrasil:default'),
                    ('Products.LinguaPlone',0,0,'Products.LinguaPlone:LinguaPlone'),
                    ('Products.CMFContentPanels',0,0,'Products.CMFContentPanels:default'),
                    ('Products.PloneFormGen',0,0,'Products.PloneFormGen:default'),
                    ('Products.RedirectionTool',0,0,'Products.RedirectionTool:default'),
                    ('collective.easyslider',0,0,'collective.easyslider:default'),
                    ('beyondskins.pythonbrasil.site',0,1,'beyondskins.pythonbrasil.site:default'),
                   ]
    
    for name,locked,hidden,profile in dependencies:
        qi.installProduct(name, locked=locked, hidden=hidden, profile=profile)
    
    # Instala profiles para os tipos de conteudo baseados em blob
    profiles = ['profile-plone.app.blob:file-replacement',
                'profile-plone.app.blob:image-replacement',
               ]
    for profile in profiles:
        setup.runAllImportStepsFromProfile(profile)


def upgrade1to101(context):
    ''' Upgrade to version 1.0.1
    '''
    setup = getToolByName(context, 'portal_setup')
    
    logger = logging.getLogger('sc.apyb.pythonbrasil6')
    logger.info('Inicia upgrade')
    
    # Instala profiles para os tipos de conteudo baseados em blob
    profiles = ['profile-sc.apyb.pythonbrasil6:to101',
               ]
    for profile in profiles:
        setup.runAllImportStepsFromProfile(profile)
