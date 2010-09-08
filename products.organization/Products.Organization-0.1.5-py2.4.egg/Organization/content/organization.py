# Zope3 imports
from zope.interface import implements

# CMF imports
from Products.CMFCore import permissions

# Archetypes & ATCT imports
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# Product imports
from Products.Organization import config
from Products.Organization.interfaces import IOrganization
from Products.Organization import OrganizationMessageFactory as _

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import finalizeATCTSchema

# Schema definition
OrganizationSchema = ATDocument.schema.copy() + atapi.Schema(())
"""
schema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

  atapi.StringField('priority',
              vocabulary = config.MESSAGE_PRIORITIES,
              default = 'normal',
              widget = atapi.SelectionWidget(label = _(u'Priority')),
             ),

  atapi.TextField('body',
            searchable = 1,
            required = 1,
            allowable_content_types = ('text/plain',
                                       'text/structured',
                                       'text/html',),
            default_output_type = 'text/x-html-safe',
            widget = atapi.RichWidget(label = _(u'Message Body')),
           ),

))
"""
finalizeATCTSchema(OrganizationSchema)

class Organization(atapi.OrderedBaseFolder, ATDocument):
    """An Archetype for an Organization application"""

    implements(IOrganization)

    # Rename some fields
    OrganizationSchema['title'].widget.label = u'Name'

    # Standard content type setup
    portal_type = meta_type = 'Organization'
    schema = OrganizationSchema
   
    _at_rename_after_creation = True
       
    # This method, from ISelectableBrowserDefault, is used to check whether
    # the "Choose content item to use as default view" option will be
    # presented. This makes sense for folders, but not for RichDocument, so
    # always disallow
    def canSetDefaultPage(self):
        return False
    
# Content type registration for the Archetypes machinery
atapi.registerType(Organization, config.PROJECTNAME)
