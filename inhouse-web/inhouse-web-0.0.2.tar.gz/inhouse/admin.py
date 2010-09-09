# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext as _

from library import format_minutes_to_time
import models


class ModelAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)
        #super(ModelAdmin, self).save_model(request, obj, form, change)


class AddressAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name1',
                       'name2',
                       'name3',
                       'name4',
                       'street',
                       'zip_code',
                       'city',
                       'country',
                       'group',
                       )}),
        (_(u'Box office'), {
            'fields': ('post_office_box',
                       'box_zip_code',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'name1', 'name2', 'name3', 'name4', 'street',
                    'zip_code', 'city', 'country', 'group', 'created',
                    'updated')
    list_display_links = ('id', 'name1', 'name2', 'name3', 'name4')
    list_filter = ['group']
    ordering = ['id']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class AddressGroupAdmin(ModelAdmin):

    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    ordering = ['id']


class BillingTypeAdmin(ModelAdmin):

    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    ordering = ['id']


class BookAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',
                       'author',
                       'publisher',
                       'edition',
                       'language',
                       'isbn',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'name', 'author', 'publisher', 'isbn',
                    'created', 'updated')
    list_display_links = ('id',)
    list_filter = ['publisher']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class BookingAdmin(ModelAdmin):

    date_hierarchy = 'created'
    fieldsets = (
        (None, {
            'fields': ('title',
                       'description',
                       'location',
                       )}),
        (_(u'Ticket information'), {
            'fields': ('issue',
            )}),
        (_(u'Details'), {
            'fields': ('day',
                       'project',
                       'step',
            )}),
        (_(u'Time information'), {
            'fields': ('from_time',
                       'to_time',
                       'duration',
            )}),
        (_(u'Billing information'), {
            'classes': ('collapse',),
            'fields': ('invoice_no',
                       'coefficient',
                       'external_coefficient',
            )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'created_by', 'day', 'project', 'step', 'get_title',
                    'get_duration', 'created', 'updated')
    list_display_links = ('id', 'get_title')
    list_filter = ['project', 'created_by']
    ordering = ['id']
    raw_id_fields = ['issue', 'step']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')
    search_fields = ['title', 'description', 'issue__title',
                     'issue__description', 'issue__no']

    def get_duration(self, booking):
        return format_minutes_to_time(booking.duration)
    get_duration.admin_order_field = 'duration'
    get_duration.short_description = _(u'Duration')

    def get_title(self, booking):
        return booking.get_title()
    get_title.short_description = _(u'Activity')


class BookingHistoryAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('title',
                       'description',
                       'location',
                       )}),
        (_(u'Ticket information'), {
            'fields': ('issue',
            )}),
        (_(u'Details'), {
            'fields': ('day',
                       'project',
                       'step',
            )}),
        (_(u'Time information'), {
            'fields': ('from_time',
                       'to_time',
                       'duration',
            )}),
        (_(u'Billing information'), {
            'classes': ('collapse',),
            'fields': ('invoice_no',
                       'coefficient',
                       'external_coefficient',
            )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'action', 'created_by', 'day', 'project', 'step',
                    'get_title', 'get_duration', 'created',
                    'updated')
    list_display_links = ('id', 'get_title')
    list_filter = ['project', 'created_by']
    ordering = ['id']
    raw_id_fields = ['issue', 'step']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')

    def get_duration(self, booking_history):
        return format_minutes_to_time(booking_history.duration)
    get_duration.admin_order_field = 'duration'
    get_duration.short_description = _(u'Duration')

    def get_title(self, booking_history):
        return booking_history.get_title()
    get_title.short_description = _(u'Activity')


class BookUserAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('book',
                       'user',
                       'lent',
                       'returned',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'book', 'user', 'lent', 'returned')
    list_display_links = ('id', 'book')
    list_filter = ['user',]
    ordering = ['id']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class CommissionStatusAdmin(ModelAdmin):

    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    ordering = ['id']


class CompanyAdmin(ModelAdmin):
    """Admin class for model :class:`Company`"""

    fieldsets = (
        (None, {
            'fields': ('name',
                       'description',
                       )}),
        (_(u'Contact information'), {
            'fields': ('address',
                       'communication',
                       )}),
        (_(u'Bank account'), {
            'fields': ('account_no',
                       'bank_code',
                       'bank',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'name', 'created', 'updated')
    list_display_links = ('id', 'name')
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')
    raw_id_fields = ['address', 'communication']


class CommunicationAdmin(ModelAdmin):
    """Admin class for model :class:`Communication`"""

    fieldsets = (
        (None, {
            'fields': ('email',
                       'phone_landline',
                       'phone_mobile',
                       'fax',
                       'url'
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'email', 'phone_landline', 'phone_mobile', 'fax',
                    'url')
    list_display_links = ('id', 'email')
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class ContactAdmin(ModelAdmin):
    """Admin class for model :class:`Contact`"""

    fieldsets = (
        (None, {
            'fields': ('salutation',
                       'title',
                       'first_name',
                       'last_name',
                       'description'
                       )}),
        (_(u'Contact information'), {
            'fields': ('address',
                       'communication',
                       'birthday',
                       )}),
        (_(u'Company information'), {
            'fields': ('customer',
                       'position',
                       'department',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'salutation', 'title', 'first_name', 'last_name',
                    'customer')
    list_display_links = ('id',)
    raw_id_fields = ['address', 'communication']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class CountryAdmin(ModelAdmin):

    list_display = ('id', 'name', 'printable_name', 'num_code', 'iso2', 'iso3',
                    'dial_code')
    list_display_links = ('id', 'name' ,'printable_name')


class CustomerAdmin(ModelAdmin):
    """Admin class for model :class:`Customer`"""

    fieldsets = (
        (None, {
            'fields': ('name1',
                       'name2',
                       'name3',
                       )}),
        (_(u'Contact information'), {
            'fields': ('salutation',
                       'address',
                       'communication',
                       'language',
                       )}),
        (_(u'Billing'), {
            'fields': ('day_rate',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'name1', 'name2', 'name3', 'created', 'updated')
    list_display_links = ('id', 'name1', 'name2', 'name3')
    #list_filter = []
    ordering = ['id']
    raw_id_fields = ['address', 'communication']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class DepartmentAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'name', 'created', 'updated')
    list_display_links = ('id', 'name')
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class HardwareAdmin(ModelAdmin):

    list_display = ('id', 'name', 'manufacturer', 'group', 'model',
                    'inventory_no', 'serial_no')
    list_display_links = ('id', 'name')


class HardwareGroupAdmin(ModelAdmin):

    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')


class HardwareUserAdmin(ModelAdmin):

    list_display = ('id', 'hardware', 'user')
    list_display_links = ('id', )


class LanguageAdmin(ModelAdmin):

    list_display = ('id', 'name', 'cid',)
    list_display_links = ('id', 'name')


class ManufacturerAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',
                       'address',
                       'communication',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'name', 'created', 'updated')
    list_display_links = ('id', 'name')
    raw_id_fields = ['address', 'communication']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class NewsAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('title',
                       'message',
                       'valid_from',
                       'valid_to',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'title', 'valid_from', 'valid_to', 'created',
                    'updated')
    list_display_links = ('id', 'title')
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class ProjectForm(forms.ModelForm):

    class Meta:
        model = models.Project

    def clean(self):
        pass


class ProjectAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',
                       'description',
                       'type',
                       'status',
                       'master',
                       )}),
        (_(u'Customer'), {
            'fields': ('customer',
                       'contact',
                       )}),
        (_(u'Billing'), {
            'fields': ('billing_type',
                       'commission_status',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    #form = ProjectForm
    list_display = ('id', 'name', 'customer', 'type', 'colored_status',
                    'created', 'updated')
    list_display_links = ('id', 'name')
    list_filter = ['status', 'type', 'customer']
    ordering = ['id']
    raw_id_fields = ['customer', 'contact']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')

    def colored_status(self, project):
        if project.status.id in (models.PROJECT_STATUS_CLOSED,
                                 models.PROJECT_STATUS_DELETED):
            color = 'red'
        elif project.status.id == models.PROJECT_STATUS_OPEN:
            color = 'green'
        else:
            return project.status
        return '<span style="color: %s;">%s</span>' % (color, project.status)
    colored_status.allow_tags = True
    colored_status.admin_order_field = 'status'
    colored_status.short_description = _(u'Status')


    def save_model(self, request, obj, form, change):
        # Create a self reference if no master is given
        self_referenced = False
        if not request.POST.get('master', ''):
            self_referenced = True
        obj.save(user=request.user)
        if self_referenced:
            obj.master = obj
            obj.save(user=request.user)


class ProjectStatusAdmin(ModelAdmin):

    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    ordering = ['id']


class ProjectStepAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',
                       'description',
                       'project',
                       'status',
                       )}),
        (_(u'Billing information'), {
            'classes': ('collapse',),
            'fields': ('coefficient',
                       'duration',
                       'flat_rate',
                       'day_rate',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'project', 'name', 'position', 'status', 'created',
                    'updated')
    list_display_links = ('id', 'name')
    list_filter = ['project', 'status',]
    ordering = ('project', 'position')
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')

    def save_model(self, request, obj, form, change):
        # TODO: Only set if not given!
        if not change:
            # Determine the step`s next position
            obj.next_position()
        obj.save(user=request.user)


class ProjectStepTemplateAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',
                       'description',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'name', 'created', 'updated')
    list_display_links = ('id', 'name')
    ordering = ('name',)
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class ProjectStepStatusAdmin(ModelAdmin):

    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    ordering = ['id']


class ProjectTrackerForm(forms.ModelForm):
    """Form validation for :class:`ProjectTracker`"""

    class Meta:
        model = models.ProjectTracker

    def clean(self, *args, **kwds):
        data = self.cleaned_data
        # Validates, that project/tracker is unique
        query = models.ProjectTracker.objects.filter(
            project=data['project'],
            tracker=data['tracker'])
        if query.count() == 1 and self.instance.pk is None:
            # Raise only if it's a new data set
            raise forms.ValidationError(
                'The project "%s" is already assigned to the issue tracker "%s"'
                % (data['project'], data['tracker']))
        return data


class ProjectTrackerAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('project',
                       'tracker',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    form = ProjectTrackerForm
    list_display = ('id', 'project', 'tracker', 'created', 'updated')
    list_display_links = ('id',)
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class ProjectTypeAdmin(ModelAdmin):

    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    ordering = ['id']


class ProjectUserForm(forms.ModelForm):
    """Form validation for :class:`ProjectUserAdmin`"""

    class Meta:
        model = models.ProjectUser

    def clean(self, *args, **kwds):
        data = self.cleaned_data
        # Validates, that user/project is unique
        query = models.ProjectUser.objects.filter(
            project=data['project'],
            user=data['user'])
        if query.count() == 1 and self.instance.pk is None:
            # Raise only if it's a new data set
            raise forms.ValidationError(
                'The user "%s" is already a member in the project "%s".'
                % (data['user'], data['project']))
        return data


class ProjectUserAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('project',
                       'user',
                       'default_step',
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    form = ProjectUserForm
    list_display = ('id', 'project', 'user', 'default_step', 'created',
                    'updated')
    list_display_links = ('id',)
    list_filter = ['project', 'user']
    raw_id_fields = ['default_step']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class TimerAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('start_time',
                       'status',
                       'title',
                       'duration'
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'start_time', 'status', 'title', 'duration',
                    'created', 'updated')
    list_display_links = ('id',)
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


class UserProfileAdmin(ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('user',
                       'short_name',
                       'birthday'
                       )}),
        (_(u'Conact information'), {
            'fields': ('salutation',
                       'address',
                       'communication',
                       )}),
        (_(u'Company information'), {
            'fields': ('company',
                       'personnel_no',
                       'job',
                       'day_rate',
                       'hours_per_week'
                       )}),
        (_(u'Timestamp'), {
            'classes': ('collapse',),
            'fields': ('created',
                       'created_by',
                       'updated',
                       'updated_by'
                       )}),
    )
    list_display = ('id', 'personnel_no', 'user', 'short_name', 'birthday',
                    'address', 'company', 'job', 'day_rate', 'created',
                    'updated')
    list_display_links = ('id', 'user')
    list_filter = ('company',)
    raw_id_fields = ['address', 'communication', 'company']
    readonly_fields = ('created', 'created_by', 'updated', 'updated_by')


admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.AddressGroup, AddressGroupAdmin)
admin.site.register(models.BillingType, BillingTypeAdmin)
admin.site.register(models.Book, BookAdmin)
admin.site.register(models.Booking, BookingAdmin)
admin.site.register(models.BookingHistory, BookingHistoryAdmin)
admin.site.register(models.BookUser, BookUserAdmin)
admin.site.register(models.Communication, CommunicationAdmin)
admin.site.register(models.CommissionStatus, CommissionStatusAdmin)
admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Contact, ContactAdmin)
admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.Customer, CustomerAdmin)
# Day
# DefaultProject
admin.site.register(models.Department, DepartmentAdmin)
# DepartmentUser
admin.site.register(models.Hardware, HardwareAdmin)
admin.site.register(models.HardwareGroup, HardwareGroupAdmin)
admin.site.register(models.HardwareUser, HardwareUserAdmin)
admin.site.register(models.Language, LanguageAdmin)
admin.site.register(models.Manufacturer, ManufacturerAdmin)
admin.site.register(models.News, NewsAdmin)
# NewsGroup
admin.site.register(models.Project, ProjectAdmin)
# ProjectRate
admin.site.register(models.ProjectStatus, ProjectStatusAdmin)
admin.site.register(models.ProjectStep, ProjectStepAdmin)
admin.site.register(models.ProjectStepStatus, ProjectStepStatusAdmin)
admin.site.register(models.ProjectStepTemplate, ProjectStepTemplateAdmin)
admin.site.register(models.ProjectTracker, ProjectTrackerAdmin)
admin.site.register(models.ProjectType, ProjectTypeAdmin)
admin.site.register(models.ProjectUser, ProjectUserAdmin)
# ProjectUserRate
# Salutation
# Software
# SoftwareGroup
admin.site.register(models.Timer, TimerAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
