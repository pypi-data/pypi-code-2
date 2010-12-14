from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.memoize.instance import memoize

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.maps.interfaces import IMarkers

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
