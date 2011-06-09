from zope.interface import implements
from Products.CMFQuickInstallerTool.interfaces import INonInstallable as INonInstallableProducts
from Products.CMFPlone.interfaces import INonInstallable as INonInstallableProfiles

class HiddenProducts(object):
    implements(INonInstallableProducts)
    
    def getNonInstallableProducts(self):
        return [
        u'beyondskins.pythonbrasil.site',
        ]

class HiddenProfiles(object):
    implements(INonInstallableProfiles)
    
    def getNonInstallableProfiles(self):
        return [
        u'beyondskins.pythonbrasil.site:default',
               ]


