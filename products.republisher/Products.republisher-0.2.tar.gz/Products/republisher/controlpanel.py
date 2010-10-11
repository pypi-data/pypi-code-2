from plone.app.registry.browser import controlpanel
from Products.republisher.interfaces import IRepublisherSettings
from Products.CMFPlone import PloneMessageFactory as _p
from z3c.form import form, button
from plone.app.form.validators import null_validator
from Products.statusmessages.interfaces import IStatusMessage
from uploadr import Uploadr

from plone.registry.interfaces import IRegistry
from Products.republisher.interfaces import IRepublisherTokenKeeper, IRepublisherSettings
from zope.component import getUtility
from zope.component import queryUtility

class RepublisherSettingsEditForm(controlpanel.RegistryEditForm):
    schema = IRepublisherSettings
    label = u"Republisher"
    description = u"Settings for the republisher product authentication on the social networks"

    def updateFields(self):
        super(RepublisherSettingsEditForm, self).updateFields()
        

    def updateWidgets(self):
        super(RepublisherSettingsEditForm, self).updateWidgets()
        
    # handle_edit_action and handle_cancel_action are copied from 
    # ControlPanelForm because they are overriden by my handle_auth_action
    '''@form.action(_p(u'label_save', default=u'Save'), name=u'save')
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
    '''
    
    @button.buttonAndHandler(_p('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_p(u"Changes saved"), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_p('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_p(u"Edit cancelled"), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))
            
    @button.buttonAndHandler(u"Generate Auth URL", name="auth")
    def handle_auth_action(self, action):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IRepublisherSettings)
        tokenkeeper = registry.forInterface(IRepublisherTokenKeeper)
        flickr = Uploadr()
        flickr.setAPIKeyAndSecret(settings.api_key, settings.api_secret)
        frob = flickr.getFrob()
        tokenkeeper.flickr_frob = unicode(str(frob))
        url = flickr.getAuthKey()
        self.status = "To Authorise the republisher please visit: " + url + " and then press check authentication."

    @button.buttonAndHandler(u"Check authorization", name="check")
    def handle_check_action(self, action):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IRepublisherSettings)
        tokenkeeper = registry.forInterface(IRepublisherTokenKeeper)
        flickr = Uploadr(frob=tokenkeeper.flickr_frob)
        flickr.setAPIKeyAndSecret(settings.api_key, settings.api_secret)
        if flickr.getToken():
            tokenkeeper.flickr_token = unicode(flickr.token)
            self.status = "You have authorized the app sucessfully"
        else:
            url = flickr.getAuthKey()
            self.status = "You have not yet authorized the app. Please visit " + url + "and then try again."
        
class RepublisherSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = RepublisherSettingsEditForm
    
    
    