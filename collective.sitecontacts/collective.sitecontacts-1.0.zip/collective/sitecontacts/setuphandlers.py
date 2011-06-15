from logging import getLogger

from Products.CMFCore.utils import getToolByName

from collective.sitecontacts.config import CATALOG_INDEXES, CATALOG_METADATA

log = getLogger('collective.sitecontacts')

def setupCatalog(portal):
    catalog = getToolByName(portal, 'portal_catalog')

    idxs = catalog.indexes()
    mtds = catalog.schema()
    
    for index in CATALOG_INDEXES.keys():
        if index not in idxs:
            catalog.addIndex(index, CATALOG_INDEXES[index])
            log.info('Catalog index "%s" installed.' % index)
    
    for mt in CATALOG_METADATA:
        if mt not in mtds:
            catalog.addColumn(mt)
            log.info('Catalog metadata "%s" installed.' % mt)

def setupVarious(context):
    if context.readDataFile('collective.sitecontacts-install.txt') is None:
        return

    portal = context.getSite()
    
    setupCatalog(portal)