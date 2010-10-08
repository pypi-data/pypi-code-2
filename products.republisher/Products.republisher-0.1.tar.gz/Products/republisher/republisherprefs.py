from zope import schema
from zope.component import adapts
from zope.formlib import form
from zope.interface import Interface, implements
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.form.validators import null_validator
from plone.protect import CheckAuthenticator
from zope.event import notify
from plone.app.controlpanel.events import ConfigurationChangedEvent
from Products.CMFPlone import PloneMessageFactory as _p

class IRepublisherPrefsForm(Interface):    
    """ The view for Republisher prefs form. """

    allowed_types = schema.Tuple(title=u'Portal types',
                          description=u'Portal types to republish',
                          missing_value=tuple(),
                          value_type=schema.Choice(
                                   vocabulary="plone.app.vocabularies.UserFriendlyTypes"),
                          required=False)

    api_key = schema.TextLine(title=u"Republisher Flickr app key",
                    default = u"None",
                )
    
    api_secret = schema.TextLine(title=u"Republisher Flickr app secret",
                    default = u"None",
                )

    republisher_toggle = schema.Bool(title=u'Republisher on',
                                  default=True,
                          )
 
 
class RepublisherControlPanelAdapter(SchemaAdapterBase):
    """ Control Panel adapter """

    adapts(IPloneSiteRoot)
    implements(IRepublisherPrefsForm)
    
    def __init__(self, context, other):
        super(RepublisherControlPanelAdapter, self).__init__(context)
        self.context = context
    
    
class RepublisherPrefsForm(ControlPanelForm):
    """ The view class for the lead image preferences form. """

    implements(IRepublisherPrefsForm)
    form_fields = form.FormFields(IRepublisherPrefsForm)

    schema = IRepublisherPrefsForm
    label = u'Republisher Settings Form'
    description = u'Select properties for the Republisher'
    form_name = u'Republisher Settings'
    
    # handle_edit_action and handle_cancel_action are copied from 
    # ControlPanelForm because they are overriden by my handle_scales_action
    @form.action(_p(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _p("Changes saved.")
            notify(ConfigurationChangedEvent(self, data))
            self._on_save(data)
        else:
            self.status = _p("No changes made.")

    @form.action(_p(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_p("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''
            
    @form.action(u'Authenticate FLICKR', name=u'authFlickr', validator=null_validator)
    def handle_scales_action(self, action, data):
        CheckAuthenticator(self.request)
        self.status = u"You are now authenticated."