from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName

def runProfile(portal, profileName):
    setupTool = getToolByName(portal, 'portal_setup')
    setupTool.runAllImportStepsFromProfile(profileName)

def install(portal):
    """Register the adapter so it takes effect on this Plone site."""
    out = StringIO()
    runProfile(portal, 'profile-themetweaker.themeswitcher:default')
    print >>out, "Installed GenericSetup"
    return out.getvalue()

def uninstall(portal):
    """Unregister the adapter so it is no longer on this Plone site."""
    out = StringIO()
    runProfile(portal, 'profile-themetweaker.themeswitcher:uninstall')
    print >>out, "Uninstalled GenericSetup"
    return out.getvalue()
