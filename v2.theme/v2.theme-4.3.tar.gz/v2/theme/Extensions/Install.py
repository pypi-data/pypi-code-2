from Products.CMFCore.utils import getToolByName

def uninstall(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.setImportContext('profile-v2.theme:default')
    setup_tool.runAllImportSteps()
    return "Ran all uninstall steps."


def uninstall(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.setImportContext('profile-v2.theme:uninstall')
    setup_tool.runAllImportSteps()
#    setup_tool.setImportContext('profile-CMFPlone:plone')
    return "Ran all uninstall steps."

