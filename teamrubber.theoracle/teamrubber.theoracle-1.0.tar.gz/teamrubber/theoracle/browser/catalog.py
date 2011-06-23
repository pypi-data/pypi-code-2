from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import ICategory
from zope.interface import implements

try:
    from Products.CMFCore.utils import getToolByName
    GTBN_AVAILABLE = True
except ImportError:
    GTBN_AVAILABLE = False

class Catalog(BrowserView):
    implements(ICategory)
    title = "Catalog"

    def __init__(self,context,request):
        self.oracle = context
        self.context = self.oracle.context
        self.request = request
        self.catalog = self._getCatalog()

    def _getCatalog(self):
        try:
            if GTBN_AVAILABLE:
                return getToolByName(self.context,'portal_catalog')
            else:
                return self.context.portal_catalog
        except AttributeError:
            return None
        
    def getIndexDataForContext(self):
        if self.catalog:
            rid = self.catalog.getrid(path=self.oracle.getPath())
            if rid is None:
                return {}
            return self.catalog.getIndexDataForRID(rid)
        return {}

    def getMetadataForContext(self):
        if self.catalog:
            rid = self.catalog.getrid(path=self.oracle.getPath())
            if rid is None:
                return {}
            return self.catalog.getMetadataForRID(rid)
        return {}