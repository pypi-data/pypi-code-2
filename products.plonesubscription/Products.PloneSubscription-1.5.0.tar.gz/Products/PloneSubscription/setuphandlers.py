# -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb - all rights reserved
## No publication or distribution without authorization.

import logging
LOG = logging.getLogger('PloneSubscription')

import Globals

from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Products.CMFPlone.utils import getToolByName

from Products.PloneSubscription import config
from Products.PloneSubscription.SubscriptionTool import SubscriptionTool
from Products.PloneSubscription.SubscriptionCatalog import manage_addSubscriptionCatalog
from Products.PloneSubscription.installers.utils import InstallationRunner, InstallationContext
from Products.PloneSubscription.installers.ToolInstaller import ToolInstaller
    

def importFinalSteps(context):
    """
    Final import steps.
    """
    
    if context.readDataFile('plonesubscription.txt') is None:
        return

    site = context.getSite()
    installProducts(site)
    manageMaintenanceTask(site)
    installSubscriptionCatalog(site)
    setupArchetypesCatalogs(site)
    LOG.info("Imported PloneSubscription final steps.")
    
def installProducts(site):
    qi = getToolByName(site, 'portal_quickinstaller')
    for product in config.plone_DEPS :
        try:
            if not qi.isProductInstalled(product):
                if qi.isProductInstallable(product):                    
                    LOG.info('Install on site: %s ... ' % (product,))
                    qi.installProduct(product)
        except Exception, e:
            LOG.error('Install failed: %s ... : %s', (product, str(e)))    

def manageMaintenanceTask(context, action='install'):
    """Add all needed stuff in portal_maintenance"""
    mtool = getToolByName(context, 'portal_maintenance', None)
    if not mtool:
        return
    if action in ('install', 'reinstall'):
        # Plone Catalog update script
        try :
            manage_addExternalMethod(mtool.scripts, config.subscription_script_id,
                                     'Mailing subscriptions',
                                     config.PROJECTNAME + '.MaintenanceToolbox',
                                     'runMailing')
        except :
            # already installed
            pass                             

        try:
            mtool.tasks.manage_addProduct['PloneMaintenance'].addMaintenanceTask(config.subscription_task_id)
        except:
            pass
        subscription_task = mtool.tasks.subscription_task
        subscription_task.setScheduled_minute('0')
        subscription_task.setScript_name(config.subscription_script_id)
    # TODO : report this in a future GenericSetup uninstaller
    else:
        if config.subscription_task_id in mtool.tasks.objectIds():
            mtool.tasks.manage_delObjects(ids=[config.subscription_task_id,])
        if config.subscription_script_id in mtool.scripts.objectIds():
            mtool.scripts.manage_delObjects(ids=[config.subscription_script_id,])            
            

def installSubscriptionCatalog(context):
    """ Install Subscription catalog at site root """

    if 'subscription_catalog' not in context.objectIds() :
        manage_addSubscriptionCatalog(context, 'subscription_catalog', 'Subscription catalog')
    ctool = getToolByName(context, 'subscription_catalog')
    for (index_name, index_type, is_metadata, extra) in config.CATALOG_INDEXES :
        try :
            ctool.addIndex( index_name, index_type, extra )
        except :
            pass    
        if is_metadata:
            try:
                ctool.addColumn(index_name)
            except: 
                pass            
            
    
def setupArchetypesCatalogs(context):
    """ Setup Archetypes Catalogs by meta_type """
    # We don't want subscription specific content to appear in the
    # portal_catalog. We use our own subscription catalog for that."""
    at=getToolByName(context, 'archetype_tool')
    for meta_type in ("KeywordsSubscription",
                      "ContentSubscription",
                      "FolderSubscription",
                      "ExactSearchSubscription",
                      ):
        at.setCatalogsByType(meta_type,('subscription_catalog',))

    # We don't want the subscription_catalog and the subscribers themselves
    # to be cataloged
    for meta_type in ("SubscriptionTemplate",
                      "TemplatesProvider",
                      "SubscriptionProvider",
                      "SubscriptionTool",
                      "UserSubscriber",
                      "AnonymousSubscriber",
                      "GroupSubscriber"):
        at.setCatalogsByType(meta_type,())    



# installed by providers profile
def installProviders(context):
    """Instanciate subscription and template providers in the portal root"""

    portal = context.getSite()
    stool = getToolByName(portal, 'portal_subscription')
    
    # force subscription_provider to be allowed in PloneSite
    # even if portal is filtering types
    ptypes = getToolByName(portal, 'portal_types')
    PloneSiteInfo = getattr(ptypes, 'Plone Site', None)
    if not PloneSiteInfo:
        raise "Type 'Plone Site' not installed! strange situation."
    atypes = list(PloneSiteInfo.getProperty('allowed_content_types'))   
    typestoAdd = ('SubscriptionProvider', 'TemplatesProvider') 
    typestoRemove = []
    for t in typestoAdd :
        if not t in atypes :
            atypes.append(t)
            typestoRemove.append(t)
            PloneSiteInfo._setPropValue('allowed_content_types', tuple(atypes))
    
    if not stool.getProvider():
        ob = None
        if not 'subscription_provider' in portal.objectIds():
            portal.invokeFactory('SubscriptionProvider', id='subscription_provider')
        ob = getattr(portal, 'subscription_provider')
        stool.setProvider(ob.UID())


    template = stool.getTemplates()
    if not template:
        if not 'subscription_templates' in portal.objectIds():
            portal.invokeFactory('TemplatesProvider', id='subscription_templates')
        template = getattr(portal, 'subscription_templates')
        stool.setTemplates(template.UID())

    if not stool.getFolderTemplate():
        if not 'default_template' in template.objectIds():
            template.invokeFactory('SubscriptionTemplate', id='default_template')
        ob = getattr(template, 'default_template')
        stool.setFolderTemplate(ob.UID())

    if not stool.getContentTemplate():
        if not 'default_template' in template.objectIds():
            template.invokeFactory('SubscriptionTemplate', id='default_template')
        ob = getattr(template, 'default_template')
        stool.setContentTemplate(ob.UID())

    if not stool.getKeywordsTemplate():
        if not 'default_template' in template.objectIds():
            template.invokeFactory('SubscriptionTemplate', id='default_template')
        ob = getattr(template, 'default_template')
        stool.setKeywordsTemplate(ob.UID())

    if not stool.getExactSearchTemplate():
        if not 'default_template' in template.objectIds():
            template.invokeFactory('ExactSearchTemplate', id='default_template')
        ob = getattr(template, 'default_template')
        stool.setExactSearchTemplate(ob.UID())
        
    # remove typestoRemove from Plone Site allowed CT
    atypes = list(PloneSiteInfo.getProperty('allowed_content_types'))
    for t in typestoRemove :
        atypes.remove(t)
    PloneSiteInfo._setPropValue('allowed_content_types', tuple(atypes))    


def installTool(context):
    """ install subscription tool (Archetypes Tool) """        
    
    portal = context.getSite()
    ic = InstallationContext(portal, config.GLOBALS)
    installers = []   
    sti = ToolInstaller(SubscriptionTool)
    installers.append(sti)     
    InstallationRunner(*tuple(installers)).install(ic, auto_reorder=True)
