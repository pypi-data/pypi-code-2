from Products.CMFCore.utils import getToolByName

def setupAttachments(context):
    if context.readDataFile('richimage_various.txt') is None:
        return

    portal = context.getSite()

    # Add RichImage to kupu's linkable and media types
    kupuTool = getToolByName(portal, 'kupu_library_tool', None)
    if kupuTool is None:
        return

    linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))
    mediaobject = list(kupuTool.getPortalTypesForResourceType('mediaobject'))
    if 'RichImage' not in linkable:
        linkable.append('RichImage')
    if 'RichImage' not in mediaobject:
        mediaobject.append('RichImage')
    kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
                                   'old_type'      : 'linkable',
                                   'portal_types'  :  linkable},
                                  {'resource_type' : 'mediaobject',
                                   'old_type'      : 'mediaobject',
                                   'portal_types'  :  mediaobject},))
