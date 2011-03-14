from Products.CMFCore.utils import getToolByName

def setupVerkkomaksutProperties(portal):
    pfgv = 'PFGVerkkomaksut'
    properties = getToolByName(portal, 'portal_properties')

    ## Site Properties
    site_properties = getattr(properties, 'site_properties')

    types_not_searched = list(site_properties.getProperty('types_not_searched'))
    if pfgv not in types_not_searched:
        types_not_searched.append(pfgv)
    site_properties.manage_changeProperties(types_not_searched = types_not_searched)

    ## Navtree Properties
    navtree_properties = getattr(properties, 'navtree_properties')
    types_not_listed = list(navtree_properties.getProperty('metaTypesNotToList'))
    if pfgv not in types_not_listed:
        types_not_listed.append(pfgv)
    navtree_properties.manage_changeProperties(metaTypesNotToList = types_not_listed)

    ## Allowed types
    types = getToolByName(portal, 'portal_types')
    allowed_content_types = list(types['FormFolder'].allowed_content_types)
    if pfgv not in allowed_content_types:
        allowed_content_types.append(pfgv)
    types.getTypeInfo('FormFolder').manage_changeProperties(allowed_content_types = allowed_content_types)

def setupVarious(context):

    if context.readDataFile('Products.PFGVerkkomaksut_various.txt') is None:
        return

    portal = context.getSite()
    setupVerkkomaksutProperties(portal)
