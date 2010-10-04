import re

from zope.interface import Interface, implements
from zope import schema
from zope.formlib import form
from zope.schema.interfaces import ValidationError
from zope.i18n import translate

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.formlib import formbase

from Products.CMFCore.utils import getToolByName

from collective.salesforce.rsvp import RSVPMessageFactory as _

class IRegistrationForm(Interface):
    """Interface for registration form
    """

class InvalidEmailAddress(schema.ValidationError):
    __doc__ = _(u'message_invalid_email', default=u"Invalid email address")

check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match
def validate_email(value):
    if not check_email(value):
        raise InvalidEmailAddress(value)
    return True


class IRegistrationFormFields(Interface):
    """Fields needed for a form for registration
    """
    first_name = schema.TextLine(
            title = _(u'label_first_name', default=u"First Name"),
            description = _(u'help_first_name', default=u"Your first name"),
            required=True,
    )
    
    last_name = schema.TextLine(
            title = _(u'label_last_name', default=u"Last Name"),
            description = _(u'help_last_name', default=u"Your last name"),
            required=True,
    )
    
    email = schema.ASCIILine(
            title = _(u'label_email', default=u"Email"),
            description = _(u'help_email', default=u"Your email address"),
            required=True,
            constraint=validate_email,
    )
    
    company = schema.TextLine(
            title = _(u'label_organization', default=u"Organization"),
            description = _(u'help_organization', default=u"Your organization name"),
            required=False,
    )
    
    phone = schema.TextLine(
            title = _(u'label_phone', default=u"Phone"),
            description = _(u'help_phone', default=u"Your preferred phone number"),
            required=False,
    )

class RegistrationForm(formbase.Form):
    """The formlib class for basic event registration
    """
    implements(IRegistrationForm)
    
    form_fields = form.Fields(IRegistrationFormFields)
    
    template = ViewPageTemplateFile('templates/registration-form.pt')
    form_name = _(u'register', default=u'Register')
    
    status = errors = None
    prefix = 'rsvpform'
    
    @form.action(_(u'register', default=u'Register'), failure='handle_register_action_failure')
    def action_register(self, action, data):
        lead_obj = dict(type='Lead',
            FirstName = data['first_name'],
            LastName = data['last_name'],
            Email = data['email'],
            Phone = data.has_key('phone') and data['phone'] or '',
            Company = data.has_key('company') and data['company'] or translate(_(u'default_company', default=u"[not provided]")),  # and some required fields...
            LeadSource = translate(_(u'default_lead_source', default=u"Website RSVP")),                                            # ...for the lead object
        )
        
        sbc = getToolByName(self.context, 'portal_salesforcebaseconnector')
        lead_res = sbc.create(lead_obj)
        
        signupSFObjectId = self.context.getField('sfObjectId').get(self.context)
        if signupSFObjectId:
            # practically speaking, the user won't ever make it here
            # but we confirm that there is a set sfObjectId on the
            # rsvpable object to be safe
            junction_obj = dict(type='CampaignMember',
                LeadId = lead_res[0]['id'],
                CampaignId = signupSFObjectId,
            )
            sbc.create(junction_obj)
        
        self.status = _(u'message_registration_received', default=u"We've received your registration.")
    
    def handle_register_action_failure(self, action, data, errors):
        # set the status
        self.status = _(u'message_registration_failed', default=u'There were errors')
