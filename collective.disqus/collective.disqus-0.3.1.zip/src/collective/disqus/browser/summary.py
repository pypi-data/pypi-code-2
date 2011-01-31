# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.disqus.browser.configlet import IDisqusSettings


class Summary(BrowserView):
    """ Summary listing (for Folder, Topic) with showing number of comments per
        item in the list.
    """

    @property
    def disqus_id(self):
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        settings = IDisqusSettings(portal)
        return settings.forum_id