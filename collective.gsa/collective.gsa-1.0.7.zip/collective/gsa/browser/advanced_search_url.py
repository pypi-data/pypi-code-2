from zope.component import getUtility

from Products.Five import BrowserView
from collective.gsa.interfaces import IGSAConnectionConfig



class AdvancedSearchURL(BrowserView):
    
    def __call__(self):
        
        config = getUtility(IGSAConnectionConfig)
        return config.advanced_search