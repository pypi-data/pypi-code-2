#!/usr/bin/env python
# encoding: utf-8
"""
listing.py

Created by Manabu Terada on 2011-03-24.
Copyright (c) 2011 CMScom. All rights reserved.
"""
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ListView(BrowserView):
    template = ViewPageTemplateFile('listing.pt')

    def __call__(self):
        return self.template()

    def get_items(self):
        limit = 10
        path = self.context.getPhysicalPath()
        catalog = getToolByName(self, 'portal_catalog')
        query = {}
        # query['portal_type'] = 'Entry'
        query['path'] = {'query':'/'.join(path), 'depth':1}
        query['sort_on'] = 'Date'
        query['sort_order'] = 'reverse'
        query['limit'] = limit
        return catalog(query)[:limit]