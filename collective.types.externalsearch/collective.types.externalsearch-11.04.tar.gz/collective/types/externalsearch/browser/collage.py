#from Acquisition import aq_inner
#from Products.Five.browser.pagetemplatefile \
#     import ViewPageTemplateFile
from Products.Collage.browser.views import BaseView

#from external_search import View

#from util import extractInnerView as getView

from Products.Five.browser.pagetemplatefile import \
     ZopeTwoPageTemplateFile
        
def _getContext(self):
    while 1:
        self = self.aq_parent
        if not getattr(self, '_is_wrapperish', None):
            return self

class CollageView(BaseView):
    """Grab the selected view, and stick it into the
    Collage layout.
    """
    title = u'standard'
#    __call__ = ViewPageTemplateFile('external_search.pt')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

        #Monkey patch for the strange error shown here
        #https://bugs.launchpad.net/zope2/+bug/176566
        ZopeTwoPageTemplateFile._getContext = _getContext
        
class TopicInlineSearch(BaseView):
    title = u'Inline Search'