from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Acquisition import aq_base, aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from zope.component import getMultiAdapter
import time
import string
from zope.interface import implements
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot

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
        urltool = getToolByName(self.context, 'portal_url')
        languagetool = getToolByName(self.context, 'portal_languages')
        portal = urltool.getPortalObject()
        try:
            lang = self.context.getLanguage()
        except:
            lang = languagetool.getDefaultLanguage()
            
        if lang == '':
            lang = "es"
            
        if hasattr(portal, lang):	 
	    if hasattr(portal[lang], "footer"):
	       return portal[lang].footer
	    else:
		return None
	else:
	    if hasattr(portal, "footer"):
	       return portal.footer
	    else:
		return None
        
    def generateFooter(self):
        footer = self.getFooterObject()
        if footer is not None:
            body = footer.getText()
            return body
        else:
            return ""