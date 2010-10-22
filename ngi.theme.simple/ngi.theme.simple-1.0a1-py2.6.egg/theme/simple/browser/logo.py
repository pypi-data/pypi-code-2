# encoding: utf-8

'''
Created on 2010/10/18

@author: nagai
'''

__author__ = """Takashi NAGAI <ngi644@gmail.com>"""
__docformat__ = 'plaintext'

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import LogoViewlet as PloneLogoViewlet
from ngi.theme.simple.config import *
from ngi.theme.simple import _


class LogoViewlet(PloneLogoViewlet):
    """
    Logo Viewlet.
    """
    template = ViewPageTemplateFile('logo.pt')
    
    def getInstalledName(self):
        qi = self.context.portal_url.getPortalObject().portal_quickinstaller
        return ( x['id'] for x in qi.listInstalledProducts())
    
    def update(self):
        super(LogoViewlet, self).update()
        if PROJECTNAME in self.getInstalledName():
            self.index = self.template
    
    def logoData(self):
        """
        Gett Logo data
        """
        portal = self.context.portal_url.getPortalObject()
        if hasattr(portal, LOGO_NAME):
            logo = portal.restrictedTraverse(LOGO_NAME)
            return logo.tag()
        else:
            return _(u'Please set a logo using control panel.')
    
    