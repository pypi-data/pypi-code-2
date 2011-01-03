# -*- coding: utf-8 -*-

from zope import interface
from collective.flowplayercaptions.interfaces import ICaptionsSource

def uninstall(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-collective.flowplayercaptions:uninstall')
    setup_tool.runAllImportStepsFromProfile('profile-collective.flowplayercaptions:uninstall')
    if not reinstall:
        removeFlowplayerCaptionsMarks(portal)

def removeFlowplayerCaptionsMarks(portal):
    """Remove all marker interfaces all around the site"""
    log = portal.plone_log
    catalog = portal.portal_catalog
    captionedContents = catalog(object_provides=ICaptionsSource.__identifier__)

    log("Uninstall Flowplayer captions support: removing merker on captioned video contents...")
    for captioned in captionedContents:
        content = captioned.getObject()
        # Bee lazy, so use the already developed procedure for the delete-events
        interface.noLongerProvides(content, ICaptionsSource)
        content.reindexObject(['object_provides'])
        log("   unmarked %s" % '/'.join(content.getPhysicalPath()))
    log("...done. Thanks you for using me!")

