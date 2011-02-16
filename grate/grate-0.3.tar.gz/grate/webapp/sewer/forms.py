from django import forms
from django.contrib import messages
from twisted.conch.ssh import keys


def save_error_messages(request, form):
    for k, v in form.errors.iteritems():
        for message in v:
            messages.error(request, '%s: %s' % (k, message))


class PublicKeyField(forms.Field):

    def clean(self, value):
        try:
            value = ''.join(value.split('\r\n'))
            key = keys.Key.fromString(value)
            if not key.isPublic():
                # As a principle, do not accept private keys.
                raise forms.ValidationError('DO NOT SEND private keys.')
            return key
        except:
            # Parsing error.
            raise forms.ValidationError('Could not parse the key.')


class PublicKeyForm(forms.Form):
    key = PublicKeyField(widget=forms.Textarea(attrs={
        'class': 'ui-corner-all ui-state-default',
        'wrap': 'virtual'}))


class GroupForm(forms.Form):
    name = forms.CharField(max_length=50)
