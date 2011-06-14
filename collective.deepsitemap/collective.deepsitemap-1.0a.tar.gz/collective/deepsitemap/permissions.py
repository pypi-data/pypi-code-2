# -*- coding: utf-8 -*-

from Products.CMFCore import permissions as CMFCorePermissions
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('collective.deepsitemap')

security.declarePublic('Use Deep Sitemap')
MyPermission = 'collective.deepsitemap: Use Deep Sitemap'
setDefaultRoles(MyPermission, ())

