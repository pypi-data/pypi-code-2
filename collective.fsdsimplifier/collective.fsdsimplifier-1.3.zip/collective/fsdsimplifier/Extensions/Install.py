from Products.CMFCore.utils import getToolByName

# The install method isn't necessary because GS will run the default profile.
#def install(portal):
#    """Apply default profile upon installation"""
#    setup_tool = getToolByName(portal, 'portal_setup')
#    setup_tool.runAllImportStepsFromProfile('profile-collective.fsdsimplifier:default')
#    return "Ran all import steps."

def uninstall(portal):
    """"Apply uninstall profile and other steps to remove product"""
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.fsdsimplifier:uninstall')
    return "Ran all uninstall steps."

