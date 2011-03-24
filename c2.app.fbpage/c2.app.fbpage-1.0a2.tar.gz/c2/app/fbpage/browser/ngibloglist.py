#!/usr/bin/env python
# encoding: utf-8
"""
ngibloglist.py

Created by Manabu Terada on 2011-03-24.
Copyright (c) 2011 CMScom. All rights reserved.
"""
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ZCatalog.Catalog import CatalogError


class NgiBlogListView(BrowserView):
    template = ViewPageTemplateFile('ngibloglist.pt')

    def __call__(self):
        return self.template()

    def get_items(self):
        limit = 10
        path = self.context.getPhysicalPath()
        catalog = getToolByName(self, 'portal_catalog')
        query = {}
        query['portal_type'] = 'Entry'
        query['path'] = {'query':'/'.join(path), 'depth':1}
        query['sort_on'] = 'pub_date'
        query['sort_order'] = 'reverse'
        query['limit'] = limit
        try:
            return catalog(query)[:limit]
        except CatalogError:
            query['sort_on'] = 'Date'
            return catalog(query)[:limit]
    
    def trans_pub_date(self, pub_date):
        if not isinstance(pub_date, DateTime):
            pub_date = DateTime(pub_date)
        return pub_date.strftime('%Y-%m-%d')
    