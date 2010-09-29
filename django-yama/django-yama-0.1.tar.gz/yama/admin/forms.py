from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from yama.models import MenuItem, Menu

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu

class MenuItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MenuItemForm, self).__init__(*args, **kwargs)

        # The rest is just an attempt to display verbose names
        # for the allowed content types

        def ct_verbose_name(content_type_pk, name):
            if not content_type_pk:
                return name
            typ = ContentType.objects.get(pk=content_type_pk).model_class()
            return unicode(typ._meta.verbose_name).capitalize()

        if 'content_type' in self.fields:
            cts = self.fields['content_type'].choices
            self.fields['content_type'].choices = [
                (ct_pk, ct_verbose_name(ct_pk, name)) for (ct_pk, name) in cts
            ]


    class Meta:
        model = MenuItem
