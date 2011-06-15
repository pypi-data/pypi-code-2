from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import Batch
from Products.Five import BrowserView

from collective.sitecontacts.interfaces import IContact

class ContactFolderView(BrowserView):
    
    @property
    def contacts(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'path':'/'.join(self.context.getPhysicalPath()),
            'object_provides':IContact.__identifier__,
            'sort_on':'getObjPositionInParent'
        }
        result = catalog(**query)
        b_start = self.request.get('b_start', 0)
        return Batch(result, 10, int(b_start), orphan=0)


class ContactView(BrowserView):
    pass