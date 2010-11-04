# -*- coding: utf-8 -*-

import grok
from zope import component, site, location


class ApplicationRoot(grok.GlobalUtility):
    grok.implements(
        grok.interfaces.IApplication,
        site.interfaces.IRootFolder,
        location.ILocation,
        component.interfaces.ISite)
    grok.provides(site.interfaces.IRootFolder)
    grok.baseclass()

    __name__ = None
    __parent__ = None

    def getSiteManager(self):
        gsm = component.getGlobalSiteManager()
        return gsm

    def setSiteManager(self, sm):
        pass
