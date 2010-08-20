#!/usr/bin/env python
# encoding: utf-8
"""
createbox.py

Created by Manabu Terada on 2010-08-11.
Copyright (c) 2010 CMScom. All rights reserved.
"""

from zope.interface import implements, alsoProvides
from zope.component import queryUtility
from Acquisition import aq_base
from DateTime import DateTime

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from zope.viewlet.interfaces import IViewlet
from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import _createObjectByType

from c2.app.shorturl import ShortUrlMessageFactory as _
from c2.app.shorturl.interfaces import IShortUrlConfig

def _get_shorturl(context):
    obj = context
    path = '/'.join(obj.getPhysicalPath())
    catalog = getToolByName(context, 'portal_catalog')
    items = catalog(portal_type='ShortUrl', org_path=path)
    if not items:
        return None
    config = queryUtility(IShortUrlConfig)
    shorturl_baseurl = getattr(config, 'base_url', None)
    shorturl_folder = getattr(config, 'folder_id', None)
    if shorturl_baseurl is not None and shorturl_folder is not None:
        return shorturl_baseurl + '/' + shorturl_folder + '/' + items[0].id
    return "" #TODO

class CreateBox(BrowserView):
    render = ViewPageTemplateFile('createbox.pt')

    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        pass
    
    def navigation_root_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.navigation_root_url()
    
    def is_createbox(self):
        return True
    
    def is_shorturl(self):
        return self.get_shorturl()
    
    def get_shorturl(self):
        return _get_shorturl(self.context)

class CreatePage(BrowserView):
    # template = ViewPageTemplateFile('create_page.pt')

    def __call__(self, *args, **kw):
        context = self.context
        request = self.request
        if not self.is_shorturl():
            self.create_shorturl()
        response = request.response
        view_url = context.absolute_url()
        portal_properties = getToolByName(context, 'portal_properties', None)
        if portal_properties is not None:
            site_properties = getattr(portal_properties, 'site_properties', None)
            portal_type = getattr(context, 'portal_type', None)
            if site_properties is not None and portal_type is not None:
                use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
                if portal_type in use_view_action:
                    view_url = view_url + '/view'
        response.redirect(view_url)
        return None
        # return self.template()

    def is_shorturl(self):
        return self.get_shorturl()

    def get_shorturl(self):
        return _get_shorturl(self.context)
    
    def create_shorturl(self):
        portal_state = getMultiAdapter((self.context, self.request), 
                                        name=u'plone_portal_state')
        portal = portal_state.portal()
        config = queryUtility(IShortUrlConfig)
        shorturl_folder = getattr(config, 'folder_id', None)
        folder_obj = getattr(portal, shorturl_folder, None)
        if not folder_obj:
            return None
        portalpathlen = len(portal.getPhysicalPath())
        physicalpath = self.context.getPhysicalPath()
        suffix_url = '/' + '/'.join(physicalpath[portalpathlen:])
        org_path = '/'.join(self.context.getPhysicalPath())
        id = DateTime().timeTime()
        obj = _createObjectByType('ShortUrl', folder_obj, id, title=suffix_url, 
                        suffix_url=suffix_url, org_path=org_path)
        obj._renameAfterCreation()
        return obj.id #TODO:
