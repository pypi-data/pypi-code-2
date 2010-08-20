#!/usr/bin/env python
# encoding: utf-8
"""
shorturl_view.py

Created by Manabu Terada on 2010-08-03.
Copyright (c) 2010 CMScom. All rights reserved.
"""

# from Products.CMFCore.utils import getToolByName
# from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ShortUrlView(BrowserView):
    
    # template = ViewPageTemplateFile('shorturl_view.pt')

    def __call__(self, *args, **kw):
        context = self.context
        request = self.request
        response = request.response
        response.redirect(context.get_org_url())
        return None
    
