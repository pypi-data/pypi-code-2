from Acquisition import aq_inner

from AccessControl import ClassSecurityInfo

from zope.component import queryAdapter

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore import permissions

from plone.memoize.instance import memoize
from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.maps.interfaces import IMarkers
from raptus.article.maps.interfaces import IMap, IMaps
from raptus.article.maps.browser.maps import IMapsFull, IMapsLeft, IMapsRight
from raptus.article.maps.interfaces import IMarker



class View(BrowserView):
    """Map view
    """

    template = ViewPageTemplateFile('view.pt')
    
    def __call__(self):
        return self.template()
    
    @property
    @memoize
    def markers(self):
        context = aq_inner(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(IMarkers(context).getMarkers())
        for item in items:
            item.update({'uid': item['brain'].UID,
                         'title': item['brain'].Title,
                         'description': item['brain'].Description,
                         'text': item['obj'].getText(),
                         'longitude': item['obj'].getLongitude(),
                         'latitude': item['obj'].getLatitude()})
        return items


class HelperView(BrowserView):
    """ Used for a python expression in the javascript registry. its
        turn off google map api if it not used.
    """
    
    def hasMaps(self):
        return (
            IMap.providedBy(self.context) or
            IMarker.providedBy(self.context) or
            IMapsFull.providedBy(self.context) or 
            IMapsLeft.providedBy(self.context) or 
            IMapsRight.providedBy(self.context) or
            IMaps.providedBy(self.context))

    
    
    
    
    