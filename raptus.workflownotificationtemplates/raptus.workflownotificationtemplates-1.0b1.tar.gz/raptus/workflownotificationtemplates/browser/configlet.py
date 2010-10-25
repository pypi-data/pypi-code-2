from persistent.dict import PersistentDict

from zope.annotation import IAnnotations
from zope.interface import implements, Interface
from zope import schema
from zope.i18n import translate
from zope.formlib import form

from plone.memoize.instance import memoize
from plone.app.controlpanel.interfaces import IPloneControlPanelForm
from plone.protect import CheckAuthenticator

from Products.CMFPlone import PloneMessageFactory as _p
from Products.statusmessages.interfaces import IStatusMessage

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.Five.formlib import formbase

from raptus.workflownotificationtemplates.browser.vocabulary import availableWorkflows
from raptus.workflownotificationtemplates import STORAGE_KEY, workflownotificationtemplatesMessageFactory as _

class NotificationConfiglet(BrowserView):
    
    template = ViewPageTemplateFile('configlet.pt')
    
    def __call__(self, delete=None):
        self.storage = IAnnotations(self.context)
        if delete and self.storage.has_key(STORAGE_KEY) and self.storage[STORAGE_KEY].has_key(delete):
            del self.storage[STORAGE_KEY][delete]
            statusmessages = IStatusMessage(self.request)
            statusmessages.addStatusMessage(_('message_deleted', default='Notification template deleted'), type='info')
        
        return self.template()
    
    @memoize
    def templates(self):
        if not self.storage.has_key(STORAGE_KEY):
            return []
        templates_raw = self.storage.get(STORAGE_KEY)
        vocabulary = availableWorkflows(self.context)
        templates = []
        for name, template in templates_raw.items():
            template = {'name': name,
                        'template': template}
            try:
                term = vocabulary.getTermByToken(name)
                template.update(dict(title=(term.title or term.token)))
            except:
                pass
            templates.append(template)
        return templates

class INotificationTemplateForm(Interface):
    """Define the fields of our form
    """
    
    name = schema.Choice(title=_(u"Workflow (Action)"),
                         required=True,
                         vocabulary='Available Workflows')

    template = schema.Text(title=_(u"Template"),
                           description=_(u"description_template", default="""The following keywords may be used in the form of %(keyword)s:
name (the full name of the receiver),
url (the url to the content object),
title (the title of the content object),
old_state (the old state of the content object),
new_state (the new state of the content object),
transition (the transition made on the the content object),
issuer (the full name of the issuer)"""),
                           required=True)

class NotificationTemplateForm(formbase.PageForm):
    implements(INotificationTemplateForm, IPloneControlPanelForm)
    form_fields = form.FormFields(INotificationTemplateForm)
    label = _(u"Manage notification templates")
    form_name = _(u"Edit notification template")
    description = ''
    is_fieldsets = 0
    name = None

    def __call__(self, name=None):
        self.name = name
        storage = IAnnotations(self.context)
        if not storage.has_key(STORAGE_KEY):
            storage[STORAGE_KEY] = PersistentDict()
        self.storage = storage[STORAGE_KEY]
        
        self.form_fields.get('name').field = self.form_fields.get('name').field.bind(self.context)
        self.form_fields.get('template').field = self.form_fields.get('template').field.bind(self.context)
        
        self.form_fields.get('template').field.default = None
        self.form_fields.get('template').field.default = None
        if self.name and self.storage.has_key(self.name):
            self.form_fields.get('name').field.default = self.name
            self.form_fields.get('template').field.default = self.storage.get(self.name)
            
        return super(NotificationTemplateForm, self).__call__()

    @form.action(_p(u"label_save", default=u"Save"))
    def action_send(self, action, data):
        """Save the notification template
        """
        CheckAuthenticator(self.request)
        self.storage[data['name']] = data['template']
        
        statusmessages = IStatusMessage(self.request)
        statusmessages.addStatusMessage(_('message_success', default='Notification template saved'), type='info')
        
        return self.request.response.redirect('%s/@@manage-notificationtemplates' % self.context.absolute_url())

    @form.action(_p(u"label_cancel", default=u"Cancel"),validator=lambda *args, **kwargs: {})
    def action_cancel(self, action, data):
        """Cancel
        """
        return self.request.response.redirect('%s/@@manage-notificationtemplates' % self.context.absolute_url())
