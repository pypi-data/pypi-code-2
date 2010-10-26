from zope import interface

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from betahaus.memberprofile.browser.interfaces import IRedirectView

class HomeFolder(BrowserView):
    """ Sends user to their home folder
    """
    interface.implements(IRedirectView)
    
    def __call__(self):
        portal_membership = getToolByName(self.context, 'portal_membership')
        homefolder = portal_membership.getHomeFolder()
        if homefolder:
            return self.context.REQUEST.response.redirect( homefolder.absolute_url() )