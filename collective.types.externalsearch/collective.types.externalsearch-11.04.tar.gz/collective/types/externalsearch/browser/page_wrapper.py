from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile \
     import ViewPageTemplateFile
from plone.memoize.instance import memoize

from util import extractInnerView as getView

class ViewPage(BrowserView):
    """View mode for an External Search
    """
    __call__ = ViewPageTemplateFile('page_wrapper.pt')

    def getInnerView(self, template_name=None):
        """Get the view for the context, and return
        the html.

        Returns a string containing html.
        """
        self.context.thisTemplate = template_name
        view = getView(self.context)

        #Reset the template, or it will be stored in memory
        self.context.thisTemplate = ''
        return view

    def getInnerView(self):
        return self.context.restrictedTraverse('@@view')
