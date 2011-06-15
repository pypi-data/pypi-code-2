from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore.permissions import ModifyPortalContent

from collective.sitecontacts.interfaces import IContact
from collective.sitecontacts.config import PROJECTNAME
from collective.sitecontacts.i18n import _

ContactSchema = base.ATContentTypeSchema.copy() + atapi.Schema((
    
    atapi.StringField('grade',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            description = '',
            label = _(u'Grade')
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
))

ContactSchema['title'].storage = atapi.AnnotationStorage()
ContactSchema['title'].widget.label = _(u'Fullname')
ContactSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(ContactSchema)

class Contact(base.ATCTContent):
    """ A contact content type """
    implements(IContact)

    meta_type = "Contact"
    schema = ContactSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    grade = atapi.ATFieldProperty('grade')
    phone = atapi.ATFieldProperty('phone')
    mobile = atapi.ATFieldProperty('mobile')
    email = atapi.ATFieldProperty('email')

atapi.registerType(Contact, PROJECTNAME)
