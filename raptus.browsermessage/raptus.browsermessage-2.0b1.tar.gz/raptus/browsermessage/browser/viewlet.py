from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.component import getMultiAdapter

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class BrowserMessage(BrowserView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(BrowserMessage, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        self.detector = getMultiAdapter((self.context, self.request), name=u'browser-detector')
        
        if self.request.get('browsermessage_ignore', 0):
            self.request.SESSION.set('browsermessage_ignore', 1)
        
    def available(self):
        properties = getattr(getToolByName(self.context, 'portal_properties'), 'browsermessage_properties', None)
        if not properties:
            return 0
        browsers = properties.getProperty('browsers', [])
        if not browsers or self.request.SESSION.get('browsermessage_ignore', 0):
            return 0
        for method in browsers:
            if getattr(self.detector, method, False):
                return True
    
    @memoize
    def suggest(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_context_state').actions().get('browsermessage_actions', [])

    def render(self):
        return self.index()
    
    index = ViewPageTemplateFile('viewlet.pt')