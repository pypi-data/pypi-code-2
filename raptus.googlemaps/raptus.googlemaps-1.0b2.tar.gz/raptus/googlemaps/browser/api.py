from urlparse import urlparse

from Acquisition import aq_inner
from zope import component

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

class Api(ViewletBase):
    """ Viewlet including the google maps api using the specified api key
    """
    index = ViewPageTemplateFile('api.pt')
    
    @property
    @memoize
    def url(self):
        key = None
        properties = component.getMultiAdapter((self.context, self.request), name=u'plone_tools').properties().get('raptus_googlemaps', None)
        if properties is not None:
            scheme, host, path, params, query, fragment = urlparse(self.request.get('BASE1'))
            while True:
                key = properties.getProperty(host, None)
                if key is None and host.find(':') > 0:
                    key = properties.getProperty(host[:host.find(':')], None)
                if key is not None or host.find('.') is -1:
                    break
                host = host[host.find('.')+1:]
        
        if key is None:
            portal_state = component.getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
            portal = portal_state.portal()
            key = portal.getProperty('google_api_key', '')
        return 'http://maps.google.com/maps?file=api&v=2&sensor=false&key=%s' % key