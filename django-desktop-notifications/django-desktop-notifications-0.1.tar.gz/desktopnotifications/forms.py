# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings

DESKTOP_NOTIFICATION_TAGS = getattr(settings, "DESKTOP_NOTIFICATION_TAGS", ())

class SimpleAddNotificationForm(forms.Form):
    autoclose_delay = forms.IntegerField(label=u'Autoclose delay', required=True, initial=-1)
    content = forms.CharField(label=u"Content", required=True, widget=forms.Textarea)
    tag = forms.ChoiceField(choices = DESKTOP_NOTIFICATION_TAGS)