from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES

def setVersionedTypes(portal):
    """Set up the types to be versioned.

    This is here instead of in teh policy because I want
    the types versioned no matter which policy is used.
    """
    portal_repository = getToolByName(portal,
                                      'portal_repository')
    versionable_types = list(portal_repository.getVersionableContentTypes())

    for type_id in ('collective.types.ExternalSearch',):
        if type_id not in versionable_types:
            versionable_types.append(type_id)
            #Add default versioning policies to the versioned type
            for policy_id in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(type_id,
                                                          policy_id)
    portal_repository.setVersionableContentTypes(versionable_types)

def importVarious(context):
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('collective.types.externalsearch_various.txt') is None:
        return
    portal = context.getSite()
    setVersionedTypes(portal)
