from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from plone.memoize import instance

class MultisiteBase(BrowserView):
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.messages=IStatusMessage(self.request)

    def back_link(self):
        return dict(label=_(u"Up to Multisite Panel"),
                    url=self.context.absolute_url())

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    @property
    def zopeRoot(self):
        return self.context.restrictedTraverse('/')
    
    @property
    @instance.memoize
    def sitesList(self):
        return self.context.ZopeFind(self.zopeRoot,obj_metatypes=['Plone Site'])