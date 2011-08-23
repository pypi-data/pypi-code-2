from zope.component import getSiteManager, getUtility

from plone.portlets.interfaces import IPortletManager
from plone.portlets.storage import PortletCategoryMapping

from collective.viewportletmanager.config import VIEW_CATEGORY

def setupVarious(context):
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('viewportletmanager_various.txt') is None:
        return

    portal = context.getSite()
    addViewCategoryToPortletManagers(portal)

def addViewCategoryToPortletManagers(portal):
    """Adds view site-wide category to registered portlet managers.
    """
    # get all registered portlet managers
    sm = getSiteManager(portal)
    registered = [r.name for r in sm.registeredUtilities()
        if r.provided.isOrExtends(IPortletManager)]

    # add view category
    for name in registered:
        manager = getUtility(IPortletManager, name)
        if VIEW_CATEGORY not in manager.keys():
            manager[VIEW_CATEGORY] = PortletCategoryMapping()
