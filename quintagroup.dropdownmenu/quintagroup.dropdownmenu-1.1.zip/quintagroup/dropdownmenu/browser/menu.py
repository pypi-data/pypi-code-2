# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.component import getUtility

from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from Products.CMFPlone.browser.navtree import DefaultNavtreeStrategy

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder

from quintagroup.dropdownmenu.interfaces import IDropDownMenuSettings
from quintagroup.dropdownmenu.util import getDropDownMenuSettings


class DropDownMenuQueryBuilder(SitemapQueryBuilder):

    implements(INavigationQueryBuilder)

    def __init__(self, context):
        super(DropDownMenuQueryBuilder, self).__init__(context)
        self.context = context

        # customize depth according to dropdown menu settings
        if self._settings.content_tabs_level > 0:
            self.query['path']['depth'] = self._settings.content_tabs_level
        elif self.query['path'].has_key('depth'):
            del self.query['path']['depth']

        # constrain non-folderish objects if required
        if not self._settings.show_nonfolderish_tabs:
            self.query['is_folderish'] = True

    @property
    def _settings(self):
        """Fetch dropdown menu settings registry"""
        return getDropDownMenuSettings(self.context)


class DropDownMenuStrategy(DefaultNavtreeStrategy):

    implements(INavtreeStrategy)

    def __init__(self, context, view=None):
        super(DropDownMenuStrategy, self).__init__(context, view)
        self.bottomLevel = self._settings.content_tabs_level

    @property
    def _settings(self):
        """Fetch dropdown menu settings registry"""
        return getDropDownMenuSettings(self.context)
