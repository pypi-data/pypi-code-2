from django import forms
from django.forms.util import ErrorList
from django.contrib.auth.models import User
from django.contrib import auth
from django.utils.translation import ugettext as _

class BaseSignupForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password2 = forms.CharField(widget=forms.PasswordInput, label=_('Password confirmation'))

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        else:
            raise forms.ValidationError(_('This username is already registered'))

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        else:
            raise forms.ValidationError(_('This email is already registered'))


    def clean(self):
        data = self.cleaned_data
        if ('password' in data and
            'password2' in data):
            if data['password'] != data['password2']:
                self._errors['password'] = ErrorList([_('Passwords are not same')])
        return data


class UsernameSignupForm(BaseSignupForm):
    username = forms.CharField(label=_('Username'))
    email = forms.EmailField(label=_('Email'))

    def save(self, *args, **kwargs):
        user = User.objects.create_user(self.cleaned_data['username'], self.cleaned_data['email'], self.cleaned_data['password'])
        return user


class EmailSignupForm(BaseSignupForm):
    email = forms.EmailField(label=_('Email'))

    def save(self, *args, **kwargs):
        user = User.objects.create_user(self.cleaned_data['email'], self.cleaned_data['email'], self.cleaned_data['password'])
        return user


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        data = self.cleaned_data
        if ('username' in data and
            'password' in data):
            user = auth.authenticate(username=data['username'], password=data['password'])
            if not user:
                self._errors['username'] = ErrorList([_('Invalid username or password')])
        return data
