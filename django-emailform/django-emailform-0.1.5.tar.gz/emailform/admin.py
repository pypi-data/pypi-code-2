from __future__ import absolute_import

import re

from django.contrib import admin
from django.forms import ModelForm, ValidationError

from .models import Question, EmailForm, Entry


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 3


class EmailFormAdminForm(ModelForm):

    class Meta:
        model = EmailForm


class EmailFormAdmin(admin.ModelAdmin):
    save_as = True
    form = EmailFormAdminForm
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_display = (
        'title',
        'slug',
        'is_published',
        'site')
    list_filter = ('is_published', 'site')
    date_hierarchy = 'starts_at'
    inlines = [QuestionInline]


admin.site.register(EmailForm, EmailFormAdmin)


class EntryAdmin(admin.ModelAdmin):
    search_fields = ('content',)
    list_display = ('emailform', 'submitted_at',
                    'ip_address', )
    list_filter = ('emailform', 'submitted_at', )
    date_hierarchy = 'submitted_at'


admin.site.register(Entry, EntryAdmin)
