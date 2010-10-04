from logging import getLogger
import pkg_resources

from Products.CMFCore.utils import getToolByName

from slc.clicksearch.config import ClickSearchConfiguration
from slc.clicksearch.interfaces import IClickSearchConfiguration
from slc.clicksearch.vocabulary import FilteredIndexVocabulary

logger = getLogger("slc.clicksearch")

def setup_site(context):
    """ Install Click Search control panel configlet
    """
    portal = context.getSite()
    sm = portal.getSiteManager()

    if not sm.queryUtility(IClickSearchConfiguration, name='clicksearch_config'):
       sm.registerUtility(ClickSearchConfiguration(),
                       IClickSearchConfiguration,
                       'clicksearch_config')

       add_default_config_settings(portal)


def add_default_config_settings(portal):
    """ Set the default searchable metadata on the config utility
    """
    search_metadata = [
                'Type',
                'is_folderish',
                'meta_type',
                'review_state',
                'portal_type',
                'allowedRolesAndUsers',
                'object_provides',
                'getEventType',
                'Creator',
                'sortable_title',
                'getRawRelatedItems',
                'Subject']

    try:
        pkg_resources.get_distribution('Products.ATContentTypes>=2.0a2')
        # We have a very new ATContnetTypes, getEventType does not exist
        # any longer
        search_metadata.pop(search_metadata.index('getEventType'))
    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
        pass

    sort_indexes = [
                'sortable_title',
                'modified',
                ]

    sm = portal.getSiteManager()
    cf = sm.queryUtility(IClickSearchConfiguration, name='clicksearch_config')
    try:
        cf.search_metadata = search_metadata
    except Exception, e:
        logger.exception("One or more search_metadata entries can not be used"
                         " for search. Check if some search_metadata fields"
                         " are missing an index")
        raise
    cf.sort_indexes = sort_indexes
