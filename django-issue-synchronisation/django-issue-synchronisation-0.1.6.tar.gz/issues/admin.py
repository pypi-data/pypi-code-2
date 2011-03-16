# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin, messages
from django.core.urlresolvers import RegexURLPattern, reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from issues import models
from issues.management.commands import sync_issues


def sync_all(request):
    query = models.Tracker.objects.all()
    num = query.count()
    for tracker in query:
        sync_issues.run(tracker)
    messages.add_message(request, messages.INFO,
                         _(u'%(num)d tracker synchronized.') % {'num': num})
    return HttpResponseRedirect(reverse('admin:issues_tracker_changelist'))


def sync_tracker(modeladmin, request, queryset):
    num = queryset.count()
    for tracker in queryset:
        sync_issues.run(tracker)
    messages.add_message(request, messages.INFO,
                         _(u'%(num)d tracker synchronized.') % {'num': num})
    sync_tracker.short_description = _(u'Synchronize tickets for selected')


class TypeAdmin(admin.ModelAdmin):

    list_display = ('id', 'cid', 'name')
    list_display_links = ('id', 'name')
    ordering = ['id']


class TrackerAdmin(admin.ModelAdmin):

    #actions = [sync_tracker]
    list_display = ('id', 'name', 'type', 'config', 'active',
                    'last_update')
    list_display_links = ('id', 'name')
    list_filter = ['type', 'active']
    ordering = ['id']

    def get_urls(self, *args, **kwds):
        urls = super(TrackerAdmin, self).get_urls(*args, **kwds)
        urls.insert(0, RegexURLPattern(r'sync_all$', sync_all))
        return urls


class IssueInline(admin.TabularInline):

    model = models.IssueUser
    readonly_fields = ['user']
    verbose_name = _(u'Related user')
    verbose_name_plural = _(u'Related users')


class IssueAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('no',
                       'title',
                       'description',
                       )}),
        (_(u'Userdata'), {
            'fields': ('reporter',
                       'owner',
                       )}),
        (_(u'Tracker information'), {
            'fields': ('tracker',
                       'active',
                       'last_change',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'updated',
                       )}),
    )
    inlines = [IssueInline]
    list_display = ('id', 'no', 'title', 'reporter', 'owner', 'active',
                    'tracker', 'last_change')
    list_display_links = ('id', 'title')
    list_filter = ['tracker', 'active']
    ordering = ['-id']
    search_fields = ('title', 'description',)
    readonly_fields = ['no', 'title', 'description', 'active', 'tracker',
                       'last_change', 'reporter', 'owner', 'created',
                       'updated']


class IssueUserAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'issue')
    list_display_links = ('id',)


class UserMappingForm(forms.ModelForm):
    """Form for :class:`UserMappingAdmin`"""

    class Meta:
        model = models.UserMapping

    def clean(self, *args, **kwds):
        data = self.cleaned_data
        query = models.UserMapping.objects.filter(
            user=data['user'], tracker=data['tracker'])
        if query.count() == 1 and self.instance.pk is None:
            raise forms.ValidationError('The user "%s" has already a loginname'
                                        ' for the tracker "%s".'
                                        % (data['user'], data['tracker']))
        return data


class UserMappingAdmin(admin.ModelAdmin):

    form = UserMappingForm
    list_display = ('id', 'user', 'tracker', 'login_name')
    list_display_links = ('id',)
    list_filter = ['tracker', 'user']


admin.site.register(models.Issue, IssueAdmin)
admin.site.register(models.IssueUser, IssueUserAdmin)
admin.site.register(models.Tracker, TrackerAdmin)
admin.site.register(models.Type, TypeAdmin)
admin.site.register(models.UserMapping, UserMappingAdmin)
