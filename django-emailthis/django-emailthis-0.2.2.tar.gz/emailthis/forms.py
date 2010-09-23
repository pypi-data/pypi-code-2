import re

from django import forms
try:
    from django.core.validators import email_re
except ImportError:
    # django 1.1
    from django.forms.fields import email_re

from emailthis.models import EmailEvent


class MultiEmailField(forms.CharField):

    def clean(self, value):
        if not value:
            raise forms.ValidationError('Enter at least one e-mail address.')
        emails = set(re.split('\s*,?\s*', value))
        for email in emails:
            if not email_re.match(email):
                raise forms.ValidationError(
                    '%s is not a valid e-mail address.' % email)
        return ','.join(list(emails))


class EmailEventForm(forms.ModelForm):

    email_from = forms.EmailField(label="Your Email",
                                  help_text="required",
                                  required=True)
    email_to = MultiEmailField(
        max_length=300,
        label="Addressees",
        required=True,
        help_text="required, please separate multiple addresses with commas")
    subject = forms.CharField(max_length=120,
                              label="Subject",
                              required=True)
    message = forms.CharField(label="Personal Message",
                              widget=forms.Textarea,
                              required=False)

    class Meta:
        model = EmailEvent
        exclude = ('mailed_by',
                   'happened_at',
                   'content_type',
                   'object_id',
                   'remote_ip')
