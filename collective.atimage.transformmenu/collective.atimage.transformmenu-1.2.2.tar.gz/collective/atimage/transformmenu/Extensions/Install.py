from Products.CMFCore.utils import getToolByName

def uninstall(portal):
    qi = getToolByName(portal, 'portal_quickinstaller')
    if qi.isProductInstalled('collective.atimage.transformtoolbar'):
        return "Transform tab kept for collective.atimage.transformtoolbar"

    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.atimage.transformmenu:uninstall')
    return "Ran all uninstall steps."
