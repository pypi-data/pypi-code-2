import os
from urlparse import urlsplit
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import Unauthorized

from zope.interface import implements, Interface, classProvides
from zope.component import getMultiAdapter
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope import schema
from zope.formlib import form
from zope.app.form.browser.interfaces import ISourceQueryView

from plone.app.vocabularies.users import UsersSource as BaseUsersSource, UsersSourceQueryView as BaseUsersSourceQueryView
from plone.app.vocabularies.groups import GroupsSource as BaseGroupsSource, GroupsSourceQueryView as BaseGroupsSourceQueryView

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _p

from Products.statusmessages.interfaces import IStatusMessage

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.Five.formlib import formbase

from raptus.workflownotification.interfaces import INotificationForm, INotificationSender
from raptus.workflownotification.utils import UserRecipientFactory
from raptus.workflownotification import workflownotificationMessageFactory as _

class UsersSource(BaseUsersSource):
    classProvides(IContextSourceBinder)
    def search(self, query):
        try:
            return super(UsersSource, self).search(query.encode('utf-8'))
        except:
            return super(UsersSource, self).search(query)
        
class UsersSourceQueryView(BaseUsersSourceQueryView):
    def getTerm(self, value):
        user = self.context.get(value)
        token = value
        title = value
        if user is not None:
            title = user.getProperty('fullname', None) or user.getId()
        return SimpleTerm(value, token=token, title=title.decode('utf-8'))

class GroupsSource(BaseGroupsSource):
    classProvides(IContextSourceBinder)
    def search(self, query):
        try:
            return super(GroupsSource, self).search(query.encode('utf-8'))
        except:
            return super(GroupsSource, self).search(query)
        
class GroupsSourceQueryView(BaseGroupsSourceQueryView):
    def getTerm(self, value):
        user = self.context.get(value)
        token = value
        title = value
        if user is not None:
            title = user.getProperty('title', None) or user.getId()
        return SimpleTerm(value, token=token, title=title.decode('utf-8'))

class INotificationForm(Interface):
    """Define the fields of our form
    """

    message = schema.Text(title=_(u"Message"),
                          required=True)
    
    users = schema.List(title=_(u"Users"),
                        required=False,
                        value_type=schema.Choice(source=UsersSource))
    
    groups = schema.List(title=_(u"Groups"),
                         required=False,
                         value_type=schema.Choice(source=GroupsSource))
    
class NotificationSearch(BrowserView):
    
    def __call__(self, f, q):
        if not INotificationForm.providedBy(self.context):
            return
        
        field = self.context.form_fields[f].field.bind(self.context.context)
        source = field.value_type.source
        query_view = getMultiAdapter((source, self.request), ISourceQueryView)
        
        if q:
            terms = set([query_view.getTerm(token) for token in source.search(q)])
        else:
            terms = set()
        
        return '\n'.join(["%s|%s" % (t.token,  t.title or t.token)
                            for t in sorted(terms, key=lambda t: t.title)])
        
class NotificationForm(formbase.PageForm):
    implements(INotificationForm)
    form_fields = form.FormFields(INotificationForm)
    label = _(u"Send notifications")
    workflow_action = None

    template = ViewPageTemplateFile('notification_form.pt')
    template_standalone = ViewPageTemplateFile('notification_form_standalone.pt')
    
    def __call__(self, workflow_action, standalone=False):
        self.workflow_action = workflow_action
        self.standalone = standalone
        self.request.set('disable_border', 1)
        return super(NotificationForm, self).__call__()

    def update(self):
        wftool = getToolByName(aq_inner(self.context), 'portal_workflow')
        transitions = [t['id'] for t in wftool.getTransitionsFor(aq_inner(self.context))]
        if not self.workflow_action in transitions:
            raise Unauthorized
        
        if self.standalone:
            self.template = self.template_standalone
            
        self.utils = getMultiAdapter((self.context, self.request), name=u'workflownotification')
        self.recipients = self.utils.getRecipientsFor(self.context, self.workflow_action)
        self.message_template = self.utils.getTemplateFor(self.context, self.workflow_action)
        
        actions = form.Actions()
        for name, a in self.actions.byname.items():
            if name == 'form.actions.label_send':
                a.label = _p(wftool.getTitleForTransitionOnType(self.workflow_action, self.context.portal_type))
            actions.append(a)
        self.actions = actions
        
        self.form_fields.get('message').field.default = self.message_template
        
        super(NotificationForm, self).update()
    
    def js(self):
        url = self.context.absolute_url()
        js = []
        for id in ('users', 'groups',):
            js.append(self.js_template % dict(id=id,
                                              url=url))
        js.append("""\
        jq('document').ready(function() {
            jq('.workflownotification_form input[name$=send]').click(function() {
                if(!jq('.workflownotification_form .spinner').length) {
                    jq('.workflownotification_form input[name$=cancel]').hide();
                    jq('.workflownotification_form input[name$=send]').blur().hide().after('<img class="spinner" src="spinner.gif" />');
                }
            });
        });
        """)
        return '\n'.join(js)

    @form.action(_p(u"label_send", default=u"Send"))
    def action_send(self, action, data):
        """Send the notification
        """
        sender = INotificationSender(self.context)
        recipients = self.recipients
        for userid in data['users']:
            recipients.append(UserRecipientFactory(userid))
        groups = getToolByName(aq_inner(self.context), 'portal_groups')
        for groupid in data['groups']:
            group = groups.getGroupById(groupid)
            users = group.getGroupMemberIds()
            for userid in users:
                recipients.append(UserRecipientFactory(userid))
        receivers, message = sender.send(self.workflow_action, data['message'], recipients)
        receivers = ', '.join([r.name for r in receivers])
        
        statusmessages = IStatusMessage(self.request)
        statusmessages.addStatusMessage(_('message_success', default='Notifications successfully sent to ${receivers}', mapping={'receivers': receivers}), type='info')
        
        return self.context.content_status_modify(workflow_action=self.workflow_action, comment='', notified=True)

    @form.action(_p(u"label_cancel", default=u"Cancel"),validator=lambda *args, **kwargs: {})
    def action_cancel(self, action, data):
        """Cancel
        """
        return self.request.response.redirect(self.context.absolute_url())
    
    js_template = """\
    (function($) {
        $().ready(function() {
            $('#formfield-form-%(id)s').each(function() {
                if(!$('#formfield-form-%(id)s #%(id)s-input').length)
                    $('#formfield-form-%(id)s').append('<input name="%(id)s-input" type="text" id="%(id)s-input" />');
                $('#formfield-form-%(id)s .queries').remove();
                $('#formfield-form-%(id)s #%(id)s-input').autocomplete('%(url)s/@@workflownotification_form/@@workflownotification_form-search?f=%(id)s', {
                    autoFill: false,
                    minChars: 2,
                    max: 10,
                    mustMatch: false,
                    matchContains: true,
                    formatItem: function(row, idx, count, value) { return row[1]; },
                    formatResult: function(row, idx, count) { return ""; }
                }).result(
                    function(event, data, formatted) {
                        var field = $('#formfield-form-%(id)s input[type="checkbox"][value="' + data[0] + '"]');
                        if(field.length == 0)
                            $('#formfield-form-%(id)s #%(id)s-input').before("<" + "label class='plain'><" + "input type='checkbox' name='form.%(id)s:list' checked='checked' value='" + data[0] + "' /> " + data[1] + "</label><br />");
                        else
                            field.each(function() { this.checked = true });
                        if(data[0])
                            $('#formfield-form-%(id)s #%(id)s-input').val('');
                    });
            })
        });
    })(jQuery);
    """

class NotificationFormAJAX(BrowserView):
    def __call__(self, workflow_action):
        self.request.URL = '%s/@@workflownotification_form' % self.context.absolute_url()
        form = getMultiAdapter((self.context, self.request), name=u'workflownotification_form')(workflow_action=workflow_action, standalone=True)
        return form.replace('class="workflownotification_form"', 'class="workflownotification_form" id="js-workflownotification_form"')
