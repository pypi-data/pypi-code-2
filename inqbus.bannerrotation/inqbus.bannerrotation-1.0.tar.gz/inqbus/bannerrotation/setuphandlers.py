__docformat__ = "epytext"

from Products.CMFCore.utils import getToolByName

def runCustomCode(site):
    """ Run custom add-on product installation code to modify Plone site object and others

    @param site: Plone site
    """
    if not 'banners' in site.objectIds():
        site.invokeFactory("Folder", "banners")
        workflowTool = getToolByName(site, "portal_workflow")
        workflowTool.doActionFor(site.banners, "publish")
        site.banners.setTitle("Banners")
        site.banners.setExcludeFromNav(True)
        site.banners.reindexObject()
    

def setupVarious(context):
    """
    @param context: Products.GenericSetup.context.DirectoryImportContext instance
    """

    # We check from our GenericSetup context whether we are running
    # add-on installation for your product or any other proudct
    if context.readDataFile('inqbus.bannerrotation.marker.txt') is None:
        # Not your add-on
        return

    portal = context.getSite()

    runCustomCode(portal)
