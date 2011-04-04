from plone.memoize.instance import memoize

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile \
     import ViewPageTemplateFile

class View(BrowserView):
    """View mode for an External Search
    """ 
    __call__ = ViewPageTemplateFile('page_wrapper.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getInnerView(self):
        return self.context.restrictedTraverse('@@innerView')()

class InnerView(BrowserView):
    """View mode for an External Search
    """ 
    __call__ = ViewPageTemplateFile('external_search.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

