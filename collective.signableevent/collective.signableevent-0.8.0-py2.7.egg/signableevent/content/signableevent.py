"""FIXME

$Id: SignableEvent.py 64 2010-01-12 10:29:10Z gael.le-mignot $
"""

from AccessControl import ClassSecurityInfo, Unauthorized

from Products.ATContentTypes.content.event import ATEvent, ATEventSchema
from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema
from Products.CMFCore.utils import getToolByName

from DateTime import DateTime

from Products.Archetypes.public import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema

from collective.signableevent.config import PROJECT_NAME
from collective.signableevent.utils import run_as_manager
from zope.interface import Interface, implements
from collective.signableevent.interfaces import ISignableEvent

from collective.signableevent.csvsigners import exportSignersToCsv

schema = ATEventSchema.copy()  + ConstrainTypesMixinSchema.copy() + Schema((
    DateTimeField('signup_start_date',
                  searchable=False,
                  required=False,
                  widget = CalendarWidget(
                    description = "",
                    description_msgid = "signup_start_date_description",
                    label = "Sign up start date",
                    label_msgid = "signup_start_date_label",
                    i18n_domain = "signableevent")),

    DateTimeField('signup_end_date',
                  searchable=False,
                  required=False,
                  widget = CalendarWidget(
                    description = "",
                    description_msgid = "signup_end_date_description",
                    label = "Sign up end date",
                    label_msgid = "signup_end_date_label",
                    i18n_domain = "signableevent")),

    BooleanField('signable',
                 required = False,
                 searchable = False,
                 index = "FieldIndex",
                 default = True,
                 widget = BooleanWidget(
                    description = "",
                    description_msgid = "can_signup_description",
                    label = "People can sign up to this event",
                    label_msgid = "can_signup_label",
                    i18n_domain = "signableevent")),
    
        ))

finalizeATCTSchema(schema)
schema['relatedItems'].widget.visible['edit'] = 'visible'

class SignableEvent(ATFolder, ATEvent):
    """A signable event"""
    implements(ISignableEvent)
    
    ## Type, icon and description
    meta_type = portal_type = 'SignableEvent'
    archetype_name = 'Signable Event'
    content_icon = 'signable_event_icon.png'
    typeDescription = 'A Signable Event'
    typeDescMsgId = 'signable_event_description'

    ## Various settings
    _at_rename_after_creation = True
    global_allow = True
    allow_discussion = True
    filter_content_types = True
    allowed_content_types = ('EventSignup', )

    ## Views
    default_view = 'signable_event_view'
    immediate_view = default_view
    suppl_views = ()

    ## Actions
##     actions = ATFolder.actions + (
##         {
##         'id'          : 'signers',
##         'name'        : 'View signers',
##         'action'      : 'string:${object_url}/signable_event_signers',
##         'permissions' : ("List folder contents",)
##         },
##         ) 

    ## Security shortcuts
    security = ClassSecurityInfo()

    schema = schema

    def getNextPreviousEnabled(self):
        """
        Hum, no, sorry
        """
        return False
 
    security.declareProtected("View", "canRegister")
    def canRegister(self):
        """
        Check if we are allowed to register on this event
        """
        if not self.getSignable():
            return False
        start = self.getSignup_start_date()
        end = self.getSignup_end_date()
        now = DateTime()
        if start and start > now:
            return False
        if end and end < now:
            return False
        return True

    security.declareProtected("View", "register")
    def register(self):
        """
        Create a new subscriber
        """
        if not self.canRegister():
            raise Unauthorized
        rid = self.generateUniqueId('EventSignup')
        run_as_manager(self, self.invokeFactory, 'EventSignup', rid)
        obj = getattr(self, rid)
        return self.REQUEST.RESPONSE.redirect(obj.absolute_url() + "/eventsignup_edit")


    security.declareProtected("List folder contents",  "getSigners")
    def getSigners(self):
        """
        Return signers (catalog query)
        """
        catalog = getToolByName(self, "portal_catalog")
        return catalog(review_state = "valid", portal_type = "EventSignup",
                       path = "/".join(self.getPhysicalPath()))

    security.declareProtected("List folder contents",  "getSigners")
    def exportSignersToCsv(self):
        """
        Export to csv the list of signers for this signable event
        """
        return exportSignersToCsv(self.getSigners())

registerType(SignableEvent, PROJECT_NAME)
