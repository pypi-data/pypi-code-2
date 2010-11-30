## -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


from Acquisition import aq_inner
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.Five import BrowserView
from Products.CMFPlone.browser.interfaces import ISiteMap
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.interfaces import INavigationTabs

from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.LinguaFace.browser.navtree import buildFolderTree
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder, SitemapQueryBuilder

from Products.CMFPlone.browser.navigation import get_view_url

from Products.CMFPlone.utils import base_hasattr




from zope.component import getMultiAdapter
from Acquisition import aq_inner
from plone.app.portlets.portlets.navigation import Renderer as oldNavigationRenderer
from plone.memoize.instance import memoize
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy

class Renderer(oldNavigationRenderer):

    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)

        # Special case - if the root is supposed to be pruned, we need to
        # abort here

        queryBuilder = getMultiAdapter((context, self.data), INavigationQueryBuilder)
        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=queryBuilder(), strategy=strategy)







class CatalogSiteMap(BrowserView):
    implements(ISiteMap)

    def siteMap(self):
        context = aq_inner(self.context)

        queryBuilder = SitemapQueryBuilder(context)
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=query, strategy=strategy)

class PhysicalNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = utils.parent(context)
        portal_languages = getToolByName(context,'portal_languages')
        preferredLanguage = portal_languages.getPreferredLanguage()
        if base_hasattr(context, 'getTranslation') and context.hasTranslation(preferredLanguage):
            context = context.getTranslation(preferredLanguage)

        try:
            name, item_url = get_view_url(context)
        except AttributeError:
            print context
            raise

        if container is None:
            return ({'absolute_url': item_url,
                     'Title': utils.pretty_title_or_id(context, context),
                    },)

        view = getMultiAdapter((container, request), name='breadcrumbs_view')
        base = tuple(view.breadcrumbs())

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation root
        if not utils.isDefaultPage(context, request) and not rootPath.startswith(itemPath):
            base += ({'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context),
                     },)
        return base

class CatalogNavigationTabs(BrowserView):
    implements(INavigationTabs)

    def topLevelTabs(self, actions=None, category='portal_tabs'):
        """
        overriden for drop down menus products
        return canonical-path
        """

        context = aq_inner(self.context)

        portal_catalog = getToolByName(context, 'portal_catalog')
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        site_properties = getattr(portal_properties, 'site_properties')

        # Build result dict
        result = []
        # first the actions
        if actions is not None:
            for actionInfo in actions.get(category, []):
                data = actionInfo.copy()
                data['name'] = data['title']
                result.append(data)

        # check whether we only want actions
        if site_properties.getProperty('disable_folder_sections', False):
            return result

        customQuery = getattr(context, 'getCustomNavQuery', False)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        rootPath = getNavigationRoot(context)
        query['path'] = {'query' : rootPath, 'depth' : 1}

        query['portal_type'] = utils.typesToList(context)

        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute

            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', [])

        query['is_default_page'] = False

        if site_properties.getProperty('disable_nonfolderish_sections', False):
            query['is_folderish'] = True

        # Get ids not to list and make a dict to make the search fast
        idsNotToList = navtree_properties.getProperty('idsNotToList', ())
        excludedIds = {}
        for id in idsNotToList:
            excludedIds[id]=1

        rawresult = portal_catalog.searchResults(**query)

        # now add the content to results
        for item in rawresult:
            if not (excludedIds.has_key(item.getId) or item.exclude_from_nav):
                id, item_url = get_view_url(item)
                if hasattr(item, 'getCanonicalPath'):
                    canonicalPath = item.getCanonicalPath
                else :
                    canonicalPath = item.getPath()
                data = {'name'      : utils.pretty_title_or_id(context, item),
                        'id'         : id,
                        'url'        : item_url,
                        'description': item.Description,
                        'canonical-path' : item.getCanonicalPath }
                result.append(data)
        return result
