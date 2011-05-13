from zope.interface import implements

from Products.Archetypes import atapi

from Products.PloneServicesCenter.content import ServicesFolder
from Products.PloneServicesCenter.interfaces import ICaseStudyFolder


class CaseStudyFolder(ServicesFolder.BaseServicesFolder):
    """Folder for case studies."""

    implements(ICaseStudyFolder)
    allowed_content_types = ['CaseStudy']

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/casestudy_listing',
            'permissions': ('View',)
        },
    )

atapi.registerType(CaseStudyFolder, 'PloneServicesCenter')
