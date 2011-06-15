from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.configuration import zconf
from Products.CMFCore.permissions import ModifyPortalContent

from collective.sitecontacts.interfaces import IContactFolder
from collective.sitecontacts.config import PROJECTNAME
from collective.sitecontacts.i18n import _

FolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    atapi.TextField('text',
        required=False,
        searchable=True,
        storage = atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default_output_type = 'text/x-html-safe',
        write_permission = ModifyPortalContent,
        widget = atapi.RichWidget(
            description = '',
            label = _(u'Text'),
            rows = 25,
            allow_file_upload = zconf.ATDocument.allow_document_upload),
    ),
    
    atapi.StringField('address_title',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Address title')
        )
    ),
    atapi.StringField('address_street',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Address street')
        )
    ),
    atapi.StringField('address_city',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Address city')
        )
    ),
    atapi.StringField('address_postal_code',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Address postal code')
        )
    ),
    atapi.StringField('phone',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Phone')
        )
    ),
    atapi.StringField('mobile',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Mobile')
        )
    ),
    atapi.StringField('fax',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Fax')
        )
    ),
    atapi.StringField('email',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        validators = ('isEmail',),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Email')
        )
    ),
    atapi.StringField('website',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        validators = ('isURL',),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Website')
        )
    ),
))

FolderSchema['title'].storage = atapi.AnnotationStorage()
FolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(FolderSchema)

class ContactFolder(folder.ATFolder):
    """ A contacts folder content type """
    implements(IContactFolder)

    meta_type = "ContactFolder"
    schema = FolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    address_title = atapi.ATFieldProperty('address_title')
    address_street = atapi.ATFieldProperty('address_street')
    address_city = atapi.ATFieldProperty('address_city')
    address_postal_code = atapi.ATFieldProperty('address_postal_code')
    phone = atapi.ATFieldProperty('phone')
    mobile = atapi.ATFieldProperty('mobile')
    fax = atapi.ATFieldProperty('fax')
    email = atapi.ATFieldProperty('email')
    website = atapi.ATFieldProperty('website')

atapi.registerType(ContactFolder, PROJECTNAME)
