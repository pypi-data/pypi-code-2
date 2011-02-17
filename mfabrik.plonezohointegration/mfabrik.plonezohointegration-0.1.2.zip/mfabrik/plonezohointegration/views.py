"""

    Zoho intergration user interface code.

"""

__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__license__ = "GPL"
__docformat__ = "Epytext"

import zope.interface
from zope import schema
from zope.component import getUtility

from z3c.form.form import Form
from z3c.form.field import Fields
from z3c.form import button

from plone.app.z3cform import layout
import z3c.form.interfaces
from plone.z3cform import layout
    
try:
    from z3c.form.browser.textlines import TextLinesFieldWidget
except ImportError:
    # z3c.form old version
    from plone.z3cform.textlines import TextLinesFieldWidget

from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

try:
    # plone.app.registry 1.0b1
    from plone.app.registry.browser.form import RegistryEditForm
    from plone.app.registry.browser.form import ControlPanelFormWrapper
except ImportError:
    # plone.app.registry 1.0b2+
    from plone.app.registry.browser.controlpanel import RegistryEditForm
    from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from plone.registry.interfaces import IRegistry
    
from mfabrik.zoho.crm import CRM
from mfabrik.plonezohointegration import _
from mfabrik.plonezohointegration.interfaces import ISettings

from plone.directives import form

class IZohoContactForm(form.Schema):
    """ Form field definitions for Zoho contact forms """
    
    first_name = schema.TextLine(title=_(u"First name"))
    
    last_name = schema.TextLine(title=_(u"Last name"))
    
    company = schema.TextLine(title=_(u"Company / organization"), description=_(u"The organization which you represent"))

    email = schema.TextLine(title=_(u"Email address"), description=_(u"Email address we will use to contact you"))
    
    phone_number = schema.TextLine(title=_(u"Phone number"), 
                                   description=_(u"Your phone number in international format. E.g. +44 12 123 1234"))
                                   #required=True,
                                   #default=u"")

    
    returnURL = schema.TextLine(title=_(u"Return URL"), 
                                description=_(u"Where the user is taken after the form is succesfully submitted. This URL is also submitted to Zoho CRM if the CRM URL field is configured from the control panel."),
                                required=False,
                                default=u"")

from z3c.form import validator

class PhoneNumberValidator(validator.SimpleFieldValidator):
    """ z3c.form validator class for international phone numbers """
    
    def validate(self, value):
        """ Validate international phone number on input """
        allowed_characters = "+- () / 0123456789"

        if value == "" or value == None:
            raise zope.interface.Invalid(_(u"Phone number missing"))
                                                                                               
        value = value.strip()
                
        # The value is not required
        for c in value:
            if c not in allowed_characters:    
                raise zope.interface.Invalid(_(u"Phone number contains bad characters"))

        if not (value.startswith("+") or value.startswith("00")):
            raise zope.interface.Invalid(_(u"Phone number is not international format. It must start with + or 00"))
            
        if len(value) < 7:
            raise zope.interface.Invalid(_(u"Phone number is too short"))

# Set conditions for which fields the validator class applies
validator.WidgetValidatorDiscriminators(PhoneNumberValidator, field=IZohoContactForm['phone_number'])

# Register the validator so it will be looked up by z3c.form machinery
import zope.component
zope.component.provideAdapter(PhoneNumberValidator)

class ZohoContactForm(form.SchemaForm):
    """ z3c.form used to handle the new lead submission.
    
    This form can be rendered  
    
    * standalone (@@zoho-contact-form view)
   
    * embedded into the portlet
    
    ..note:: 
        
        It is recommended to use a CSS rule
        to hide form descriptions when rendered in the portlet to save
        some screen estate. 
    
    Example CSS::
    
        .portletZohoCRMContact .formHelp {
           display: none;
        } 
    """
        
    schema = IZohoContactForm
    
    label = _(u"Contact Us")
    
    description = _(u"If you are interested in our services leave your contact details below and our sales representatives will contact you.")
    
    ignoreContext = True
    
    def __init__(self, context, request, returnURLHint=None, full=True):
        """
        
        @param returnURLHint: Should we enforce return URL for this form
        
        @param full: Show all available fields or just required ones.
        """
        form.SchemaForm.__init__(self, context, request)
        self.all_fields = full
        
        self.returnURLHint = returnURLHint
            
    @property
    def action(self):
        """ Rewrite HTTP POST action.
        
        If the form is rendered embedded on the others pages we 
        make sure the form is posted through the same view always,
        instead of making HTTP POST to the page where the form was rendered.
        """
        return self.context.portal_url() + "/@@zoho-contact-form"
      
    def updateWidgets(self):
        """ Make sure that return URL is not visible to the user.
        """
        form.SchemaForm.updateWidgets(self)
        
        
        # Use the return URL suggested by the creator of this form
        # (if not acting standalone)
        self.widgets["returnURL"].mode = z3c.form.interfaces.HIDDEN_MODE
        if self.returnURLHint:
            self.widgets["returnURL"].value = self.returnURLHint

        # Prepare compact version of this formw
        if not self.all_fields:
            # Hide fields which we don't want to bother user with
            self.widgets["phone_number"].mode = z3c.form.interfaces.HIDDEN_MODE
            
    def parseExtraFields(self, text):
        """ Get Zoho CRM fields set to every lead created through web.
        
        From Zoho CRM integration settings get all 
        fields which are set to every lead created through the web.
        
        @param text: Setting field value as-is
        """
        data = {}
        
        if not text or text == "":
            # No extra fields configured
            return data
        
        pairs = text.split("\n")
        for p in pairs:
            p = p.strip()
            
            if len(p) == 0:
                # Skip empty lines
                continue
            
            key, value = p.split("=")
            data[key] = value
            
        return data
    
    def postData(self, data):
        """ Post data to Zoho """
        
        settings = self.getZohoSettings()
        if settings is None:
            self.status = _(u"Zoho is not configured in Site Setup. Please contact the site administration.")
            return 
            
        crm = CRM(settings.username, settings.password, settings.apikey)
    
        # Fill in data going to Zoho CRM
        lead = {
            "First Name" : data["first_name"],
            "Last Name" : data["last_name"],
            "Company" : data["company"],
            "Email" : data["email"],   
        }
        
        # Post the page where the user came from to CRM
        # using a field specified in the settings
        
        if settings.crm_lead_url_field is not None and settings.crm_lead_url_field.strip() != u"":
            lead[settings.crm_lead_url_field] = data.get("returnURL", "")
        
        phone = data.get("phone_number", "")
        
        if phone == "" or phone == None:
            raise RuntimeError("Phone number required always")
        
        if phone != "":
            # Only pass phone number to Zoho if it's set
            lead["Phone"] = phone
        
        # Pass in all prefilled lead fields configured in the site setup
        lead.update(self.parseExtraFields(settings.crm_lead_extra_data))
        
        # Open Zoho API connection
        try:
            # This will raise ZohoException and nuke the request
            # if Zoho credentials are wrong
            crm.open()
            
            # Make sure that wfTrigger is true
            # and Zoho does workflow actions for the new leads
            # (like informing sales about the availability of the lead)
            crm.insert_records([lead], {"wfTrigger" : "true"})
        except IOError:
            # Network down?
            self.status = _(u"Cannot connect to Zoho servers. Please contact web site administration")
            return

    
    @button.buttonAndHandler(_('Send contact request'), name='ok')
    def send(self, action):
        """ Form button hander. """
        
        # data is dict form field name -> cleaned value look-up
        # errors is a list of z3c error objects which have attribute message
        # extractData() also sets self.errors by default
        
        data, errors = self.extractData()
               
        if len(errors) == 0:
                    
            self.postData(data)
                
            ok_message = _(u"Thank you for contacting us. Our sales representatives will come back to you in few days")
        
            # Check whether this form was submitted from another page
            returnURL = data.get("returnURL", "")

            if returnURL != "" and returnURL is not None:
                
                # Go to page where we were sent and
                # pass the confirmation message as status message (in session)
                # as we are not in the control of the destination page
                from Products.statusmessages.interfaces import IStatusMessage
                messages = IStatusMessage(self.request)
                messages.addStatusMessage(ok_message, type="info")
                self.request.response.redirect(returnURL)
            else:
                # Act standalone
                self.status = ok_message
        else:
            # errors on the form
            self.status = _(u"Please correct the errors below")        
            

            
        
    def getZohoSettings(self):
        """ Retrieve Zoho settings
        
        @return plone.registry settings object configured in the site setup or None
            if Zoho is not configured
            
        """
        registry = getUtility(IRegistry)
    
        try:
            settings = registry.forInterface(ISettings)
        except KeyError:
            return None
        
        return settings

    def __call__(self):
        # Just make sure exceptions are fired always 
        # even if form is not submitted and settings are broken
        self.getZohoSettings()
        
        ZohoContactForm.__call__(self)


class ControlPanelForm(RegistryEditForm):
    """ Zoho settings form in Site Setup """
    
    label = _(u"Zoho integration settings")
    
    description = _(u"These settings are used to connect your Plone site to various Zoho services")
    
    schema = ISettings
    
    def updateFields(self):
        RegistryEditForm.updateFields(self)
        self.fields['crm_lead_extra_data'].widgetFactory = TextLinesFieldWidget
        
        # see http://plone.293351.n2.nabble.com/plone-app-registry-RecordsProxy-vs-acquisition-vs-TinyMCE-tp5446190p5446190.html
        #self.fields['contact_form_prefix'].widgetFactory = WysiwygFieldWidget
        #self.fields['contact_form_suffix'].widgetFactory = WysiwygFieldWidget
        

ControlPanelView = layout.wrap_form(ControlPanelForm, ControlPanelFormWrapper)

ZohoContactFormView = layout.wrap_form(ZohoContactForm)
