# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common
from DateTime import DateTime

from monet.mapsviewlet.interfaces import IMonetMapsEnabledContent
from monet.mapsviewlet.browser.maps_view import MapsView

from Products.Archetypes.utils import shasattr

class GMapViewlet(common.ViewletBase, MapsView):
    """A viewlet for showing Google Maps on contents"""
    
    def __init__(self, context, request, view, manager):
        common.ViewletBase.__init__(self, context, request, view, manager)
        portal_props = getToolByName(context, 'portal_properties')
        self.properties = getattr(portal_props, 'monet_properties', None)

    render = ViewPageTemplateFile('gmaps.pt')

    def _search_key(self, property_id):
        """Stolen from Products.Maps"""

        if self.properties is None:
            return None
        keys_list = getattr(self.properties, property_id, None)
        if keys_list is None:
            return None
        keys = {}
        for key in keys_list:
            url, key = key.split('|')
            url = url.strip()
            # remove trailing slashes
            url = url.strip('/')
            key = key.strip()
            keys[url] = key
        portal_url_tool = getToolByName(self.context, 'portal_url')
        portal_url = portal_url_tool()
        portal_url = portal_url.split('/')
        while len(portal_url) > 2:
            url = '/'.join(portal_url)
            if keys.has_key(url):
                return keys[url]
            portal_url = portal_url[:-1]
        return None

    @property
    def googlemaps_key(self):
        return self._search_key('googlemaps_key')

    @memoize
    def getKmlRelated(self):
        """Get all related contents that lead to .kml files.
        @return: a list of URL to download those files.
        """
        try:
            related = self.context.getRelatedItems()
            related = ["%s/at_download/file" % x.absolute_url() for x in related if hasattr(x, 'getFilename') and x.getFilename().endswith(".kml")]
        except AttributeError:
            related = []
        return related

    @property
    def view_map(self):
        """Check if the current viewlet can display the map"""
        context = self.context
        if shasattr(context, 'getLocation') and context.getLocation():
            if IMonetMapsEnabledContent.providedBy(context):
                if self.canShowMap():
                    return True
        return False

    def update(self):
        context = self.context
        self.relatedKml = self.getKmlRelated()


