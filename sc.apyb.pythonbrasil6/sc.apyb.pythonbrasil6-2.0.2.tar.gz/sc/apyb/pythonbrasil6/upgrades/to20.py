# -*- coding: utf-8 -*-
from zope import component
import logging
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup import interfaces as gsinterfaces
from Products.GenericSetup.upgrade import listUpgradeSteps
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import alsoProvides


from Products.ZCatalog.ProgressHandler import ZLogHandler

try:
    from Products.CacheSetup import interfaces
    from Products.CacheSetup.enabler import enableCacheFu
    CACHEFU = True
except ImportError:
    CACHEFU = False

logger = logging.getLogger('sc.apyb.pythonbrasil6')
def upgradefrom101(context):
    ''' Upgrade to version 1.0
    '''
    setup = getToolByName(context, 'portal_setup')
    migration = getToolByName(context,'portal_migration')
    portal_url = getToolByName(context,'portal_url')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    qi = getToolByName(context,'portal_quickinstaller')
    portal = portal_url.getPortalObject()
    
    logger.info('Inicia upgrade')
    migration.upgrade()
    dependencies = [
                    ('Products.DataGridField',0,0,'Products.DataGridField:default'),
                   ]
    
    for name,locked,hidden,profile in dependencies:
        qi.installProduct(name, locked=locked, hidden=hidden, profile=profile)
    # Instala profiles para os tipos de conteudo baseados em blob
    profiles = ['profile-sc.apyb.pythonbrasil6:to200',
                'profile-Products.PyConBrasil:to24',
                'profile-beyondskins.pythonbrasil.site:to300',
               ]
    logger.info('Executa profiles')
    for profile in profiles:
        setup.runAllImportStepsFromProfile(profile)
    
    logger.info('Define edicoes como INavigationRoot')
    adicionaNavRootParaEdicoes(portal)
    logger.info('Remove itens da custom')
    removeItensCustom(portal)
    logger.info('Remove items de portal_view_customizations')
    removeItensVC(portal)
    logger.info('Fix layer order')
    fixSkinLayer(portal)
    logger.info('Migra conteudos para blob')
    exportaConteudosParaBlob(portal)
    logger.info('Finaliza upgrade')

def adicionaNavRootParaEdicoes(portal):
    # Consideramos que temos algumas edicoes
    edicoes = ['2005','2006','2007','2008','2009','2010','2011',]
    oIds = portal.objectIds()
    for edicao in edicoes:
        if edicao in oIds:
            alsoProvides(portal[edicao],INavigationRoot)
    
def removeItensCustom(portal):
    # As informacoes do custom foram movidas para produtos
    # portanto eh seguro apaga-las
    portal_skins = portal.portal_skins
    custom = portal_skins.custom
    custom.manage_delObjects(custom.objectIds())

def removeItensVC(portal):
    # As informacoes do custom foram movidas para produtos
    # portanto eh seguro apaga-las
    custom = portal.portal_view_customizations
    custom.manage_delObjects(custom.objectIds())

def fixSkinLayer(portal):
    # Precisamos garantir que as pastas do produto de tema
    # estejam logo apos o custom
    layers = ['beyondskins_pythonbrasil_site_templates',
              'beyondskins_pythonbrasil_site_images',
              'beyondskins_pythonbrasil_site_styles']
    portal_skins = portal.portal_skins
    oIds = portal_skins.objectIds()
    path = portal_skins.getSkinPath('pythonbrasil_site')
    path = path.split(',')
    path = [p for p in path if (p in oIds) and (p not in layers)]
    for layer in layers:
        path.insert(1,layer)
    path = ','.join(path)
    portal_skins.addSkinSelection('pythonbrasil_site',path,test=0)
    
def exportaConteudosParaBlob(portal):
    # Vamos exportar arquivos e imagens para blob
    portal.unrestrictedTraverse('@@blob-file-migration').migration()
    portal.unrestrictedTraverse('@@blob-image-migration').migration()
    