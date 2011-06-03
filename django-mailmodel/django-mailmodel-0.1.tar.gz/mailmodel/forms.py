#-*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from models import MailModel
from app_settings import MAILMODEL_CONFIG

class MailModelForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size' : 40}), label=_("Your name"))
    email = forms.EmailField(widget=forms.TextInput(attrs={'size' : 40} ), label=_("Your email"))
    recipient_name = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'size' : 40}), label=_("Recipient"))
    recipient_email = forms.EmailField(widget=forms.TextInput(attrs={'size' : 40} ), label=_(u"Recipient's email"))
    body = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':6, 'cols':40}), label=_(u"Your message"))
    content_type = forms.CharField(widget=forms.HiddenInput())
    object_pk = forms.CharField(widget=forms.HiddenInput())
    
    def clean(self):
        if not self.cleaned_data["content_type"] in MAILMODEL_CONFIG["APPS"]:
            raise forms.ValidationError(_(u"This model is not included in MAILMODEL_CONFIG[\"APPS\"]"))
        model_tuple = self.cleaned_data["content_type"].split(".")
        model = get_model(*model_tuple)
        self.target_object = model._default_manager.get(id=self.cleaned_data["object_pk"])
        return self.cleaned_data
        
    def send(self):
        self.cleaned_data.update({"obj": self.target_object, "current_site": Site.objects.get_current()})
        data = self.cleaned_data
        body = render_to_string('mailmodel/email_body.txt', data)
        title = render_to_string('mailmodel/email_title.txt', data)
        EmailMessage(title, body, settings.DEFAULT_FROM_EMAIL,
            [self.cleaned_data['recipient_email']],
            headers = {'Reply-To': self.cleaned_data['email']}).send()
    
    def save(self):
        MailModel.objects.create(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_pk = self.cleaned_data["object_pk"],
            name = self.cleaned_data["name"],
            email = self.cleaned_data["email"],
            recipient_name = self.cleaned_data["recipient_name"],
            recipient_email = self.cleaned_data["recipient_email"],
            body = self.cleaned_data["body"],
        )
        self.send()
        