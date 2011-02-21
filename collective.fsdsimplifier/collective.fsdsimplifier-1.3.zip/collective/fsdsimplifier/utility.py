from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implements

class FSDSimplifierNonInstallable(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return [u'collective.fsdsimplifier:default',
                u'collective.fsdsimplifier:uninstall']