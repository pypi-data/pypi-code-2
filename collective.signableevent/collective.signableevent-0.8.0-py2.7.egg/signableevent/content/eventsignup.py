"""FIXME

$Id: EventSignup.py 64 2010-01-12 10:29:10Z gael.le-mignot $
"""

from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.base import ATCTContent, ATContentTypeSchema
from Products.CMFCore.utils import getToolByName

import urllib
import transaction

from Products.Archetypes.public import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from collective.signableevent.utils import run_as_manager
from zope.interface import Interface, implements
from collective.signableevent.interfaces import IEventSignup
from collective.signableevent.config import PROJECT_NAME

from zExceptions import Redirect

from zope.event import notify
from collective.signableevent import _
from collective.signableevent.events import SignupAddedEvent

schema = ATContentTypeSchema.copy() + Schema((
    ComputedField('title',
                  searchable=True,
                  required=True,
                  widget = ComputedWidget(label_msgid='label_title',
                                          description_msgid='help_title',
                                          i18n_domain='plone'),
                  expression='context.Title()'
                  ),
    
    StringField('gender',
                index="FieldIndex:schema",
                searchable=False,
                required=True,
                vocabulary = ('Miss', 'Madam', 'Mister',),
                widget = SelectionWidget(description = "",
                                      description_msgid = "gender_description",
                                      label = "Gender",
                                      label_msgid = "gender_label",
                                      i18n_domain = "signableevent")),
    
    StringField('firstname',
                index="FieldIndex:schema",
                searchable=False,
                required=True,
                widget = StringWidget(description = "",
                                      description_msgid = "firstname_description",
                                      label = "First name",
                                      label_msgid = "firstname_label",
                                      i18n_domain = "signableevent")),

    StringField('lastname',
                index="FieldIndex:schema",
                searchable=False,
                required=True,
                widget = StringWidget(description = "",
                                      description_msgid = "lastname_description",
                                      label = "Last name",
                                      label_msgid = "lastname_label",
                                      i18n_domain = "signableevent")),
    
    StringField('email',
                index="FieldIndex:schema",
                searchable=False,
                required=True,
                validators=('isEmail',),
                widget = StringWidget(description = "",
                                      description_msgid = "email_description",
                                      label = "E-mail",
                                      label_msgid = "email_label",
                                      i18n_domain = "signableevent")),
    
    StringField('company',
                index="FieldIndex:schema",
                searchable=False,
                required=True,
                widget = StringWidget(description = "",
                                      description_msgid = "company_description",
                                      label = "Company",
                                      label_msgid = "company_label",
                                      i18n_domain = "signableevent")),
    
    StringField('function',
                index="FieldIndex:schema",
                searchable=False,
                required=True,
                widget = StringWidget(description = "",
                                      description_msgid = "function_description",
                                      label = "Function",
                                      label_msgid = "function_label",
                                      i18n_domain = "signableevent")),
    
    StringField('address',
                searchable=False,
                required=False,
                widget = StringWidget(description = "",
                                      description_msgid = "address_description",
                                      label = "Address",
                                      label_msgid = "address_label",
                                      i18n_domain = "signableevent")),
    
    StringField('zipcode',
                searchable=False,
                required=False,
                widget = StringWidget(description = "",
                                      description_msgid = "zipcode_description",
                                      label = "Zip/Postal code",
                                      label_msgid = "zipcode_label",
                                      i18n_domain = "signableevent")),
    
    StringField('city',
                searchable=False,
                required=False,
                widget = StringWidget(description = "",
                                      description_msgid = "city_description",
                                      label = "City",
                                      label_msgid = "city_label",
                                      i18n_domain = "signableevent")),
    
    StringField('phone',
                searchable=False,
                required=False,
                widget = StringWidget(description = "",
                                      description_msgid = "phone_description",
                                      label = "Phone number",
                                      label_msgid = "phone_label",
                                      i18n_domain = "signableevent")),
    
    StringField('fax',
                searchable=False,
                required=False,
                widget = StringWidget(description = "",
                                      description_msgid = "fax_description",
                                      label = "Fax number",
                                      label_msgid = "fax_label",
                                      i18n_domain = "signableevent")),
    
    StringField('comment',
                index="FieldIndex:schema",
                searchable=True,
                required=False,
                widget = TextAreaWidget(description = "",
                                    description_msgid = "comment_description",
                                    label = "Comments",
                                    label_msgid = "comment_label",
                                    i18n_domain = "signableevent")),

    
        ))

del schema["description"]
schema['relatedItems'].widget.visible['edit'] = 'invisible'
finalizeATCTSchema(schema, moveDiscussion=False)

                    
class EventSignup(ATCTContent):
    """A signup of an event"""
    implements(IEventSignup)

    ## Type, icon and description
    meta_type = portal_type = 'EventSignup'
    archetype_name = 'Event Signup'
    content_icon = 'event_signup_icon.png'
    typeDescription = 'A signup of an event'
    typeDescMsgId = 'event_signup_description'

    ## Various settings
    _at_rename_after_creation = True
    global_allow = False
    allow_discussion = True

    ## Actions
##     actions =  ATCTContent.actions + ({'id': 'edit',
##                                        'name': 'Edit',
##                                        'action': 'string:${object_url}/eventsignup_edit',
##                                        'permissions': ("Modify portal content",)
##                                        },
##                                       )

    ## Security shortcuts
    security = ClassSecurityInfo()

    schema = schema

    security.declareProtected("View", "Title")
    def Title(self):
        """
        Create title from firstname and lastname
        """
        return self.getFirstname() + " " + self.getLastname()

    security.declareProtected("View", "setId")
    def setId(self, *args, **kwargs):
        """
        Ugly wrapper to allow renaming by anonymous
        """
        return run_as_manager(self, ATCTContent.setId, self, *args)

    def at_post_create_script(self, *args, **kwargs):
        """
        Called after creation
        """
        utool = getToolByName(self, 'plone_utils')
        ATCTContent.at_post_create_script(self, *args, **kwargs)
        msg = _(u"Signup recorded")
        worflow = getToolByName(self, "portal_workflow")
        worflow.doActionFor(self, "validate")
        msg = urllib.quote_plus(msg)
        url = self.aq_inner.getParentNode().absolute_url()
        notify(SignupAddedEvent(self))
        transaction.commit()
        utool.addPortalMessage(msg, 'info')
        raise Redirect, url
    

registerType(EventSignup, PROJECT_NAME)