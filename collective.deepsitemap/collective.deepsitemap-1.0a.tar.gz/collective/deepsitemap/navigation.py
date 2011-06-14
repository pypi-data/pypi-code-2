
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter

from Products.Five import BrowserView
from Products.CMFPlone.browser.interfaces import ISiteMap
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder, SitemapQueryBuilder
from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree



class QueryBuilder(NavtreeQueryBuilder):
    """Build a folder tree query suitable for a sitemap
    """

    def portal_depth(self):
        """
        Returns the sitemap depth as defined by the global properties. Standard plone behaviour.
        """
        portal_properties = getToolByName(self.context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        return navtree_properties.getProperty('sitemapDepth', 2)

    def request_depth(self):
        """
        Returns the sitemap depth as required by the user in this request. If missing, behaves like standard plone.
        """
        try:
            return int(self.request.form['sitemapDepth'])
        except KeyError:
            return self.portal_depth()


    def __init__(self, context, request):
        NavtreeQueryBuilder.__init__(self, context)
        self.context = context
        self.request = request

        if getSecurityManager().checkPermission('collective.deepsitemap: Use Deep Sitemap', context):
            sitemapDepth = self.request_depth()
            query_path = '/'.join(self.context.getPhysicalPath())
        else:
            sitemapDepth = self.portal_depth()
            query_path = getToolByName(context, 'portal_url').getPortalPath()

        self.query['path'] = {'query': query_path, 'depth': sitemapDepth}



class CatalogSiteMap(BrowserView):
    implements(ISiteMap)

    def siteMap(self):
        context = aq_inner(self.context)

        queryBuilder = QueryBuilder(context, self.request)
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=query, strategy=strategy)

