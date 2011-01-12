from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class FormView(BrowserView):

    template = ViewPageTemplateFile('view.pt')

    def __call__(self):

        return self.template()
