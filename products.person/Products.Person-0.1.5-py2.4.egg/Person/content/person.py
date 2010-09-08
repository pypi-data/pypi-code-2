# Zope3 imports
from zope.interface import implements

# CMF imports
from Products.CMFCore import permissions

# Archetypes & ATCT imports
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# Product imports
from Products.Person import config
from Products.Person.interfaces import IPerson
from Products.Person import PersonMessageFactory as _

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import finalizeATCTSchema


# Security and permission
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
# Schema definition
 
#schema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
PersonSchema = ATDocument.schema.copy() + atapi.Schema((
    atapi.StringField(
        name='firstName',
        required=True,
        searchable=True,
        widget=atapi.StringWidget(
            label=u"First name",
            label_msgid='Person_label_firstName',
        )
    ),
    atapi.StringField(
        name='middleName',
        searchable=True,
        widget=atapi.StringWidget(
            label=u"Middle name",
            label_msgid='Person_label_middleName',
        )
    ),
    atapi.StringField(
        name='lastName',
        searchable=True,
        widget=atapi.StringWidget(
            label=u"Last name",
            label_msgid='Person_label_lastName',
        )
    ),
    atapi.ComputedField(
        name='title',
        accessor="Title",
        user_property='fullname',
        searchable=True,
        widget=atapi.ComputedField._properties['widget'](
            label=u"Full name",
            visible={'edit': 'invisible', 'view': 'visible'},
            label_msgid='Person_label_fullName',
        )
    ),
    atapi.StringField('contact_email',
        required=False,
        searchable=True,
        #write_permission = ChangeEvents,
        validators = ('isEmail',),
        widget = atapi.StringWidget(
                description = '',
                label = _(u'label_contact_email', default=u'Contact E-mail')
                )
    ),

))

# Finalise the schema according to ATContentTypes standards. This basically
# moves the Related items and Allow discussion fields to the bottom of the
# form. See ATContentTypes.content.schemata for details.
finalizeATCTSchema(PersonSchema)

#class Person(base.ATCTContent):
class Person(atapi.OrderedBaseFolder, ATDocument):
    """An Archetype for an Person application"""
    implements(IPerson)

    security = ClassSecurityInfo()
            
    # Readjust schema
    PersonSchema.moveField('firstName', before='description')
    PersonSchema.moveField('middleName', after='firstName')
    PersonSchema.moveField('lastName', after='middleName')
    PersonSchema['text'].widget.label = u'Biography'
        
    
    # Standard content type setup
    portal_type = meta_type = 'Person'
    schema = PersonSchema
    #schema = schema

    # Make sure we get title-to-id generation when an object is created
    _at_rename_after_creation = True
    
    # This method, from ISelectableBrowserDefault, is used to check whether
    # the "Choose content item to use as default view" option will be
    # presented. This makes sense for folders, but not for RichDocument, so
    # always disallow
    def canSetDefaultPage(self):
        return False

    security.declareProtected(View, 'Title')

    def ContactEmail(self):
        return self.getContact_email()
    
    def Title(self):
        """Return the Title as firstName middleName(when available) lastName, suffix(when available)"""
        try:
            # Get the fields using the accessors, so they're properly Unicode encoded.
            # We also can't use the %s method of string concatentation for the same reason.
            # Is there another way to manage this?
            fn = self.getFirstName()
            ln = self.getLastName()
        except AttributeError:
            return u"new person" # YTF doesn't this display on the New Person page?  # Couldn't call superclass's Title() for some unknown reason
        
        if self.getMiddleName():
            mn = " " + self.getMiddleName() + " "
        else:
            mn = " "
        
        t = fn + mn + ln
        
        #if self.getSuffix():
        #    t = t + ", " + self.getSuffix()
        
        return t
        
# Content type registration for the Archetypes machinery
atapi.registerType(Person, config.PROJECTNAME)
