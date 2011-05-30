# -*- encoding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe
from ProcImap.ImapMailbox import ImapMailbox

from .models import Migration
from .utils.gmail2gmail import CaptchaError, ServerError, AuthenticationError, build_migration_service, get_server

import datetime

class MigrationForm(forms.ModelForm):

    captcha_token = forms.CharField(required=False, widget=forms.HiddenInput)
    captcha = forms.CharField(required=False, widget=forms.HiddenInput, label="CAPTCHA")

    class Meta:
        model = Migration
        exclude = ('labels_processed', 'current_since', 'current_label', 'auth_token', 'messages_cnt', 'last_uid')
        widgets = {
            'admin_password': forms.PasswordInput(render_value=True, attrs={'class': 'txt'}),
        }

    def __init__(self, *args, **kwargs):
        super(MigrationForm, self).__init__(*args, **kwargs)
        for bound_field in self:
            bound_field.field.widget.attrs['class'] = 'txt'

    def clean(self):
        cleaned_data = self.cleaned_data
        self.data = self.data.copy()
        domain = cleaned_data.get("domain")
        admin_username = cleaned_data.get("admin_username")
        admin_password = cleaned_data.get("admin_password")
        captcha_token = cleaned_data.get("captcha_token")
        captcha = cleaned_data.get("captcha")

        # check domain password
        if domain and admin_username and admin_password:
            try:
                build_migration_service(domain, admin_username, admin_password, captcha_token, captcha)
            except CaptchaError, e:
                self._errors["captcha"] = self.error_class([mark_safe("<img src='%s' />" % e.url)])
                self.fields['captcha'].widget = forms.TextInput()
                self.data['captcha_token'] = e.token
            except AuthenticationError, e:
                self._errors["admin_password"] = self.error_class([unicode(e)])

        # check source password
        from_email = cleaned_data.get("from_email")
        from_password = cleaned_data.get("from_password")
        if from_email and from_password:
            try:
                server = get_server(from_email, from_password)
            except ServerError, e:
                self._errors["from_email"] = self.error_class([unicode(e)])
            else:
                since = cleaned_data.get("since")
                # get real since date
                mailbox = ImapMailbox((server, '[Gmail]/All Mail'))
                uids = mailbox.search('UNDELETED')
                if len(uids) > 0:
                    # messages are returned from old to new, so get first and be happy
                    uid = mailbox.search('UNDELETED')[0]
                    message = mailbox[uid]
                    since = max(datetime.date(*message.internaldate[:3]), cleaned_data['since'])
                    cleaned_data['since'] = since
                    self.data['since'] = since.strftime("%Y-%m-%d")
                else:
                    self._errors["from_email"] = self.error_class(["Mailbox is empty. Nothing to migrate."])

        # errorize erroneous fields
        for bound_field in self:
            if bound_field._errors():
                bound_field.field.widget.attrs['class'] = 'txt error'
            else:
                bound_field.field.widget.attrs['class'] = 'txt'

        return cleaned_data