# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES

TYPES_TO_VERSION = ('Structured Document',)

def setVersionedTypes(context):
    '''
    Setup handler to put under version control the specified portal types
    
    '''

    if context.readDataFile('rer.structured_content_various.txt') is None:
        return

    portal=context.getSite()
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


def setDefaultView(context):
    """Step for setting the default view for this site"""

    if context.readDataFile('rer.structured_content_various.txt') is None:
        return
    
    portal=context.getSite()
    
    portal_properties = portal.portal_properties
    rer_properties = getattr(portal_properties, 'rer_properties',None)
    if not rer_properties:
        portal_properties.addPropertySheet(id='rer_properties',title="RER properties")
        rer_properties = getattr(portal_properties, 'rer_properties',None)
    if not rer_properties.hasProperty('structured_content_default_view'):
        rer_properties.manage_addProperty(id='structured_content_default_view',
                                          value='structured_document_view',
                                          type='string')
    
    portal_types = portal.portal_types
    stdoc_info = portal_types.getTypeInfo('Structured Document')
    stdoc_info.default_view = rer_properties.structured_content_default_view

