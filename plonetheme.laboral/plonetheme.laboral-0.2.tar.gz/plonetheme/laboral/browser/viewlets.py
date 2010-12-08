from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FooterView (BrowserView):
    """
    Footer menu. Reads the /footer page and generates a footer menu.
    A link to login_form will generate the default login menu with dropdown menu
    """
    implements(IViewlet)
    render = ViewPageTemplateFile('footer.pt')

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        
    def getFooterObject(self):
        lang = self.context.getLanguage()
        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()
        if hasattr(portal[lang], "footer"):
            return portal[lang].footer
        else:
            return None
        
    def generateFooter(self):
        footer = self.getFooterObject()
        if footer is not None:
            body = footer.getText()
            return body
        else:
            return "No footer exists"