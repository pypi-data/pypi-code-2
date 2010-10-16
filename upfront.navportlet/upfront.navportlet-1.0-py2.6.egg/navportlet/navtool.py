from zope.interface import implements
from Products.CMFPlone.CatalogTool import CatalogTool
from interfaces import INavigationCatalogTool

class NavigationCatalog(CatalogTool):
    """ Catalog used by navigation portlet
    """
    implements(INavigationCatalogTool)

    id = 'nav_catalog'
    meta_type = 'Navigation Catalog'
