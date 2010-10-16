from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

class Configlet(BrowserView):

    label = _("Navigation Portlet")
    status = None

    def __call__(self, *args, **kwargs):
        if self.request.has_key('submit'):
            portal_catalog = getToolByName(self.context, 'portal_catalog')
            nav_catalog = getToolByName(self.context, 'nav_catalog')

            for brain in portal_catalog():
                obj = brain.getObject()
                obj.reindexObject()

            self.status = _("Content reindexed successfully.")

        return self.index()
