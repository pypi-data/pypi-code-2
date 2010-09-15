import logging
from zope.component import getSiteManager
from zope.component import getGlobalSiteManager
from Products.CMFCore.utils import getToolByName
from quintagroup.plonegooglesitemaps.content.newsextender import NewsExtender

logger = logging.getLogger('quintagroup.plonegooglesitemaps')

def unregisterSchemaExtenderAdapters(site):
    """ Unregister news schema extender adapters
        from local component registry.
    """
    lsm = getSiteManager(site)
    gsm = getGlobalSiteManager()
    if lsm == gsm:
        logger.warning("Not found local component registry")
        return

    unregistered = []
    registrations = tuple(lsm.registeredAdapters())
    for registration in registrations:
        factory = registration.factory
        if factory == NewsExtender:
            required = registration.required
            provided = registration.provided
            name = registration.name
            lsm.unregisterAdapter(factory=factory,
                required=required, provided=provided, name=name)
            unregistered.append(str(required))
    logger.info("Unregistered news schema extender adapters for: %s" % unregistered)

def removeConfiglet(site):
    """ Remove configlet.
    """
    conf_id = 'GoogleSitemaps'
    controlpanel_tool = getToolByName(site, 'portal_controlpanel')
    if controlpanel_tool:
        controlpanel_tool.unregisterConfiglet(conf_id)
        logger.log(logging.INFO, "Unregistered \"%s\" configlet." % conf_id)


def uninstall(context):
    """ Do customized uninstallation.
    """
    if context.readDataFile('gsm_uninstall.txt') is None:
        return
    site = context.getSite()
    unregisterSchemaExtenderAdapters(site)
    removeConfiglet(site)
