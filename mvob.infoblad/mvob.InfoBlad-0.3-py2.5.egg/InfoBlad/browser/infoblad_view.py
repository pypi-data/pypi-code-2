from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class InfoBladView(BrowserView):
    ''' View class for InfoBlad type '''
    
    def getInnerMedia(self):
        '''Catalog search for media inside the infoblad'''
        
        catalog = getToolByName(self, 'portal_catalog')
        folder_url = '/'.join(self.context.getPhysicalPath())
        results = catalog.searchResults(path = {'query': folder_url, 'depth': 1}, sort_on = 'getObjPositionInParent', sort_order='descending', portal_type = ('Image'))
        
        return results