from Products.CMFCore.utils import getToolByName
try:
    import plone.app.upgrade
    PLONE_VERSION = 4
except ImportError:
    PLONE_VERSION = 3


def uninstall(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-zettwerk.users:uninstall')

    cp_tool = getToolByName(portal, 'portal_controlpanel')
    cp_tool.unregisterConfiglet('zettwerkuserlist')

    if PLONE_VERSION == 3:
        ai_tool = getToolByName(portal, 'portal_actionicons')
        try:
            ai_tool.removeActionIcon('controlpanel', 'zettwerkuserlist')
        except KeyError:
            # was not there, so nothing removed
            pass

    return "Ran all uninstall steps for zettwerk.users"
