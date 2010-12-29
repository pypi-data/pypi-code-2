from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES

TYPES_TO_VERSION = ['FolderishDocument']

def setVersionedTypes(portal):

    portal_repository = getToolByName(portal, 'portal_repository')
    versionable_types = list(portal_repository.getVersionableContentTypes())

    for type_id in TYPES_TO_VERSION:
        if type_id not in versionable_types:
            versionable_types.append(type_id)
            for policy_id in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(type_id, policy_id)

    portal_repository.setVersionableContentTypes(versionable_types)

def importVarious(context):
    """Miscellanous steps import handle
    """

    portal = context.getSite()
    setVersionedTypes(portal)
