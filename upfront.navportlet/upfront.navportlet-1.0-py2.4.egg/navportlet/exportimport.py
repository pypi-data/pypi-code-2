from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects

from Products.CMFCore.utils import getToolByName


def importNavigationCatalog(context):
    """Import navigation catalog.
    """
    site = context.getSite()
    tool = getToolByName(site, 'nav_catalog')

    importObjects(tool, '', context)

def exportNavigationCatalog(context):
    """Export navigation catalog.
    """
    site = context.getSite()
    tool = getToolByName(site, 'nav_catalog', None)
    if tool is None:
        logger = context.getLogger('nav_catalog')
        logger.info('Nothing to export.')
        return

    exportObjects(tool, '', context)
