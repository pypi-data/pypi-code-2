from Products.CMFCore.utils import getToolByName
try:
    import plone.app.upgrade
    PLONE_VERSION = 4
except ImportError:
    PLONE_VERSION = 3


def setup_action_icons(context):
    """ Setup action icons """
    # We check from our GenericSetup context whether we are currently
    # in the context of our profile
    if context.readDataFile('zettwerk.users.actionicons.txt') is None:
        # Marker file not present
        return

    if PLONE_VERSION == 4:
        # we only need this for plone 3
        return

    portal = context.getSite()
    ai_tool = getToolByName(portal, 'portal_actionicons')
    ai_tool.addActionIcon('controlpanel', 'zettwerkuserlist',
        '++resource++zettwerk.users.images/z.png',
        title='Zettwerk Userlist')

    return "Ran import steps for plone 3"
