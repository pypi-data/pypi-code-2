from Products.PlonePAS.Extensions.Install import activatePluginInterfaces

from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

from pas.plugins.userdeletedevent.plugin import addUserDeletedEventPlugin


PLUGIN_ID = 'userdeleted_event'
PLUGIN_TITLE = 'User Deleted Event Plugin'


def setupVarious(context):
    """ Install the UserDeletedEventPlugin 
    """
    if context.readDataFile('pas.plugins.userdeletedevent_various.txt') is None:
        return

    out = StringIO()
    portal = context.getSite()
    uf = getToolByName(portal, 'acl_users')
    installed = uf.objectIds()

    if PLUGIN_ID not in installed:
        addUserDeletedEventPlugin(uf, PLUGIN_ID, PLUGIN_TITLE)
        activatePluginInterfaces(portal,PLUGIN_ID, out)
    else:
        print >> out, '%s already installed' % PLUGIN_ID
    print out.getvalue()
