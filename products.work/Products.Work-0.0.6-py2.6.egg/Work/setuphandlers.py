from Products.CMFCore.utils import getToolByName
try:
    from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES
except ImportError:
    DEFAULT_POLICIES = ('at_edit_autoversion', 'version_on_revert')

# put your custom types in this list
TYPES_TO_VERSION = ('Work',)

def setVersionedTypes(portal):
    portal_repository = getToolByName(portal, 'portal_repository')
    versionable_types = list(portal_repository.getVersionableContentTypes())
    for type_id in TYPES_TO_VERSION:
        if type_id not in versionable_types:
            # use append() to make sure we don't overwrite any
            # content-types which may already be under version control
            versionable_types.append(type_id)
            # Add default versioning policies to the versioned type
            for policy_id in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(type_id, policy_id)
    portal_repository.setVersionableContentTypes(versionable_types)
    
def importVarious(context):
    """Miscellanous steps import handle"""
    portal = context.getSite()
    setVersionedTypes(portal)
    
    #print "Work: setuphandlers: importVarious"
    #Code to debug which contents types are in the version system
    #portal_repository = portal.portal_repository
    #map = portal_repository.getPolicyMap()
    #for i in map.items(): print i