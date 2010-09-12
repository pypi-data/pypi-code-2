# -*- coding: utf-8 -*-

from zope import interface
from redturtle.smartlink.interfaces import ISmartLinked


def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.setImportContext('profile-redturtle.smartlink:uninstall')
        setup_tool.runAllImportSteps()
        if not reinstall:
            removeSmartLinkMarks(portal)


def removeSmartLinkMarks(portal):
    """Remove all Smart Link marker interfaces all around the site"""
    log = portal.plone_log
    catalog = portal.portal_catalog
    smartlinkeds = catalog(object_provides=ISmartLinked.__identifier__)

    log("Uninstall Smart Link: removing flag to internally linked contents...")
    for linked in smartlinkeds:
        content = linked.getObject()
        # Bee lazy, so use the already developed procedure for the delete-events
        unLink(portal, content)
        interface.noLongerProvides(content, ISmartLinked)
        content.reindexObject(['object_provides'])
        log("   unmarked %s" % '/'.join(content.getPhysicalPath()))
    log("...done.")

    # TODO: the perfect world is the one where SmartLink(s) are converted back to ATLink(s)


def unLink(portal, object):
    """Remove the reference from the smart link and the object itself, changing the internal link to
    a normal external link.
    """
    reference_catalog = portal.reference_catalog
    backRefs = reference_catalog.getBackReferences(object, relationship='internal_page')
    for r in backRefs:
        r.setInternalLink(None)
        r.setExternalLink(object.absolute_url())
        r.reindexObject(['getRemoteUrl'])
