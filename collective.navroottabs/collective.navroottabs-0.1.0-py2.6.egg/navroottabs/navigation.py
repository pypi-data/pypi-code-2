# -*- coding: utf-8 -*-

import re

from Acquisition import aq_base
from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.Five import BrowserView

from Products.CMFPlone.browser.interfaces import INavigationTabs
from Products.CMFPlone.browser.navigation import get_view_url

from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.root import getNavigationRoot

idpattern = r"""[^a-zA-Z0-9_]+"""
idnorm = re.compile(idpattern, re.IGNORECASE)

def normalideId(text):
    return idnorm.sub('_', text)

class CatalogNavigationTabs(BrowserView):
    implements(INavigationTabs)

    def topLevelTabs(self, actions=None, category='portal_tabs'):
        context = aq_inner(self.context)
        
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()

        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')
        
        obj = context
        while not INavigationRoot.providedBy(obj) and aq_base(obj) is not aq_base(portal):
            obj = utils.parent(obj)
        inavroot = obj
        if inavroot is not portal:
            # get the new category name from the INavigationRoot id
            rootcategory = "portal_%s_tabs" % normalideId(inavroot.getId())
            actions = context_state.actions(rootcategory) or None
            # check inheritance
            if actions:
                action_category = portal.portal_actions[rootcategory]
                if not action_category.getProperty('block_inherit', False):
                    actions = context_state.actions(category) + actions

        portal_catalog = getToolByName(context, 'portal_catalog')
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        site_properties = getattr(portal_properties, 'site_properties')

        if actions is None:
            actions = context_state.actions(category)

        # Build result dict
        result = []
        # first the actions
        if actions is not None:
            for actionInfo in actions:
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

        blacklist = navtree_properties.getProperty('metaTypesNotToList', ())
        all_types = portal_catalog.uniqueValuesFor('portal_type')
        query['portal_type'] = [t for t in all_types if t not in blacklist]

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

        rawresult = portal_catalog.searchResults(query)

        # now add the content to results
        idsNotToList = navtree_properties.getProperty('idsNotToList', ())
        for item in rawresult:
            if not (item.getId in idsNotToList or item.exclude_from_nav):
                id, item_url = get_view_url(item)
                data = {'name'      : utils.pretty_title_or_id(context, item),
                        'id'         : item.getId,
                        'url'        : item_url,
                        'description': item.Description}
                result.append(data)
        return result
