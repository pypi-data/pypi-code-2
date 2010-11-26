from Acquisition import aq_inner, aq_parent
from zope.component import getUtility
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.langMailHost.interfaces import ILangCharset

class Encoding(BrowserView):

    def encoding(self):
        context = aq_inner(self.context)
        urltool = getToolByName(context, "portal_url")
        portal = urltool.getPortalObject()
        return ILangCharset(portal).effective_charset() or portal.getProperty('email_charset', 'UTF-8')
