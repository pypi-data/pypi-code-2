from raptus.googlemaps.browser.api import Api as BaseApi
from raptus.article.maps.interfaces import IMap, IMaps
from raptus.article.maps.browser.maps import IMapsFull, IMapsLeft, IMapsRight
from zope.component import queryAdapter


class Api(BaseApi):
    """ This viewlet overrides the api-viewlet from raptus.googlemaps. With 
        the difference thats this viewlet is only rendered if some google-maps
        are available.
    """
    
    def render(self):
        if IMap.providedBy(self.context):
            return self.index()
        if not (IMapsFull.providedBy(self.context) or 
                IMapsLeft.providedBy(self.context) or 
                IMapsRight.providedBy(self.context)):
            return ''
        provider = queryAdapter(self.context, interface=IMaps)
        if provider and provider.getMaps():
            return self.index()
        return ''