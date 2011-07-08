import pysvn
from django import forms
from django.contrib import admin

from svnlit import models


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = models.Repository

    password = forms.CharField(
        max_length=512, required=False, widget=forms.PasswordInput)


class RepositoryAdmin(admin.ModelAdmin):
    form = RepositoryForm

    fieldsets = (
        (None, {'fields': ('label', 'root', 'uri', 'is_private')}),
        (u'Credentials', {'fields': ('username', 'password')}),
    )


admin.site.register(models.Repository, RepositoryAdmin)
