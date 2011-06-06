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

def upgrade000to100(context):
    ''' Upgrade to version 1.0
    '''
    setup = getToolByName(context, 'portal_setup')
    migration = getToolByName(context,'portal_migration')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    qi = getToolByName(context,'portal_quickinstaller')
    
    # Install dependencies for this upgrade
    dependencies = [
                    ('webcouturier.dropdownmenu',0,1,'webcouturier.dropdownmenu:default'),
                   ]
    
    for name,locked,hidden,profile in dependencies:
        qi.installProduct(name, locked=locked, hidden=hidden, profile=profile)

def upgrade100to101(context):
    ''' Upgrade from version 1.0.0 to version 1.0.1
    '''
    setup = getToolByName(context, 'portal_setup')
    migration = getToolByName(context,'portal_migration')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    qi = getToolByName(context,'portal_quickinstaller')
    # 

def upgrade101to102(context):
    ''' Upgrade from version 1.0.1 to version 1.0.2
    '''
    setup = getToolByName(context, 'portal_setup')
    migration = getToolByName(context,'portal_migration')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    qi = getToolByName(context,'portal_quickinstaller')
    # 

def upgrade102to103(context):
    ''' Upgrade from version 1.0.2 to version 1.0.3
    '''
    setup = getToolByName(context, 'portal_setup')
    migration = getToolByName(context,'portal_migration')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    qi = getToolByName(context,'portal_quickinstaller')
    # 

def upgrade103to200(context):
    ''' Upgrade from version 1.0.3 to version 2.0.0
    '''
    setup = getToolByName(context, 'portal_setup')
    migration = getToolByName(context,'portal_migration')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    qi = getToolByName(context,'portal_quickinstaller')
    # 

def upgrade200to300(context):
    ''' Upgrade from version 1.0.3 to version 2.0.0
    '''
    setup = getToolByName(context, 'portal_setup')
    migration = getToolByName(context,'portal_migration')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    qi = getToolByName(context,'portal_quickinstaller')
    # 