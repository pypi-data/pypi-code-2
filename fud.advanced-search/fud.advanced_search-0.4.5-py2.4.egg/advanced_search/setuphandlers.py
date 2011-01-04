__author__="daggy"
__date__ ="$Dec 16, 2009 7:38:58 AM$"
import logging
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.Catalog import CatalogError
#profile id of the package
PROFILE_ID = 'profile-fud.advanced_search:default'



def add_catalog_indexes(context, logger=None):
    """Adds indexes to the portal_catalog.
    @parameter:
    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.

    """
    if logger is None:
        #Called as upgrade step: define our own logger.
        logger = logging.getLogger('fud.advanced_search')

    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    try:
        catalog.addColumn(name='fundort')
        catalog.addColumn(name='druckort')
    except CatalogError:
        print "The column exists already"
        
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = (('listCreators', 'KeywordIndex'),
              ('fundort','FieldIndex'),
              ('druckort','FieldIndex'),)

    indexables = []
    for name, metatype in wanted:
        if name not in indexes:
            catalog.addIndex(name, metatype)
            indexables.append(name)
            logger.info("Added %s for field %s.", metatype, name)
        if len(indexables) > 0:
            logger.info("Indexing new indexes %s", ', '.join(indexables))
            catalog.manage_reindexIndex(ids=indexables)



def import_various(context):
    """import step for configuration that is not handled in xml files"""

    # Only run step if a flag file is present
    if context.readDataFile('fud.advanced_search-default.txt') is None:
        return
    logger = context.getLogger('fud.advanced_search')
    site = context.getSite()
    add_catalog_indexes(site, logger)

