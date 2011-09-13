from Products.feedfeeder.browser.feed import FeedFolderView
from Products.CMFPlone import Batch

class FeedFolderView(FeedFolderView):
    title = u"Standard"

    batch_size = 20
    
    @property
    def batch(self):
        results = self.item_list()
        b_size = self.request.get('b_size', self.batch_size)
        b_start = self.request.get('b_start', 0)        
        return Batch(results, b_size, int(b_start), orphan=1)
                    
