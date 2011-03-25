# -*- coding: utf-8 -*-

"""Admin classes."""

# TODO: Saving an object via TabularInline causes an error, as the user is not
#       given within the kwargs.

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import widgets
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse
from django.db.models import Max, Q
from django.template.defaultfilters import truncatewords
from django.utils.translation import ugettext as _

from teagarden import models


class TabularInline(admin.TabularInline):

    def save_form(self, request, form, change):
        obj = form.save(commit=False)
        if not obj.id:
            obj.created_by = request.user
        obj.updated_by = request.user
        return obj


### Forms ###

class TableForm(forms.ModelForm):

    class Meta:
        model = models.Table

    def clean(self):
        name = self.cleaned_data.get("name")
        project = self.cleaned_data.get("project")
        tables = models.Table.objects.filter(name=name, project=project)
        tables = tables.exclude(id=self.instance.id)
        if tables.count() > 0:
            raise forms.ValidationError(_(u"The tablename '%(table)s' is already in"
                                          " use for project '%(project)s'.")
                                        % {"table": name, "project": project})
        prefix = self.cleaned_data.get("prefix")
        tables = models.Table.objects.filter(project=project, prefix=prefix)
        tables = tables.exclude(id=self.instance.id)
        if tables.count() > 0:
            raise forms.ValidationError(_(u"The prefix '%(prefix)s' is already in use"
                                          " for project '%(project)s'.")
                                          % {"prefix": prefix, "project": project})
        return self.cleaned_data


### Inline Tables ###

class FieldKeyInline(TabularInline):

    fields = ("position","key")
    model = models.FieldKey
    verbose_name = _(u"Key")
    verbose_name_plural = _(u"Keys")


class FieldPropertyInline(TabularInline):

    fields = ("position", "property", "value")
    model = models.FieldProperty
    verbose_name = _(u"Property")
    verbose_name_plural = _(u"Properties")


class TableFieldInline(TabularInline):

    fields = ("position", "name", "type")
    model = models.Field
    verbose_name = _(u"Field")
    verbose_name_plural = _(u"Fields")


class TableGroupInline(TabularInline):

    fields = ("table",)
    model = models.TableGroup
    verbose_name = _(u"Table")
    verbose_name_plural = _(u"Tables")


class ModelAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user.account)


# Widgets

class PrimaryKeyRawIdWidget(widgets.ForeignKeyRawIdWidget):

    def url_parameters(self):
        params = super(PrimaryKeyRawIdWidget, self).url_parameters()
        params["primary__exact"] = 1
        #print self.rel.get_related_field()
        #params["table__project__id__exact"] =
        return params


class ProjectAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": (
                       "name",
                       'short_description',
                       "description",)}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "name", "short_description", "created", "created_by",
                    "updated", "updated_by")
    list_display_links = ("id", "name",)
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]


class TableAdmin(ModelAdmin):

    actions = ["add_default_fields", "add_position_gaps"]
    date_hierarchy = "created"
    fieldsets = [
        (None, {
            "fields": ("name",
                       "project",
                       "prefix",
                       "type",)}),
        (_(u"Description"), {
            "fields": ("short_description", "description")}),
        (_(u"Database settings"), {
            "classes": ("collapse",),
            "fields": ["first_extension", "next_extension", "db_space",
                       "lock_mode", "storage_clause"]}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})

    ]
    form = TableForm
    inlines = [TableFieldInline]
    list_display = ("id", "name", "prefix", "type", "short_description",
                    "project", "count_fields", "created", "created_by",
                    "updated", "updated_by")
    list_display_links = ("id", "name",)
    list_filter = ["project", "type"]
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]
    search_fields = ("name", "short_description", "description")

    def add_default_fields(self, request, queryset):
        num = 0L
        for table in queryset:
            default_fields = models.DefaultField.objects.filter(
                project=table.project)
            for df in default_fields:
                fields = models.Field.objects.filter(table=table, name=df.name)
                if fields.count() > 0:
                    continue
                num += 1
                field = models.Field()
                field.name = df.name
                field.set_next_position(table)
                field.description = df.description
                field.short_description = df.short_description
                field.label = df.label
                field.type = df.type
                field.precision = df.precision
                field.scaling = df.scaling
                field.primary = df.primary
                field.foreign = df.foreign
                field.lookup = df.lookup
                field.nullable = df.nullable
                field.mask_length = df.mask_length
                field.default_value = df.default_value
                field.cascading_delete = df.cascading_delete
                field.table = table
                field.save(user=request.user)
        self.message_user(request, _("Added default fields for %s tables.")
                          % num)
        # New message system?
        #messages.error(request, _(u"Failure"))
    add_default_fields.short_description = _(u"Add default fields to selected"
                                             " tables")

    def add_position_gaps(self, request, queryset):
        """Repositions all table fields."""
        for table in queryset:
            gap = 10L
            for field in table.get_fields():
                field.position = gap
                field.save(user=request.user)
                gap += 10L
    add_position_gaps.short_description = _(u"Reposition fields of selected"
                                            u" tables.")

    def count_fields(self, obj):
        num = obj.count_fields()
        # admin/teagarden/field/?table__id__exact=1
        url = reverse("admin:teagarden_field_changelist")
        url += "?table__id__exact=%d" % obj.id
        return '<a href="%s">%s</a>' % (url, num)
    count_fields.allow_tags = True
    count_fields.short_description = _(u"Fields")

    def get_form(self, request, obj=None, **kwargs):
        form = super(TableAdmin, self).get_form(request, obj, **kwargs)
        if request.session.get("project", 0):
            form.base_fields["project"].initial = request.session["project"]
        return form

    def queryset(self, request):
        query = super(TableAdmin, self).queryset(request)
        if request.session.get("project", 0):
            project_id = request.session["project"]
            query = query.filter(project=int(project_id))
        return query


class TableTypeAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("name",
                       "short_name",)}),
    ]
    list_display = ("id", "name", "short_name",)
    list_display_links = ("id", "name",)
    ordering = ["name"]


class FieldAdmin(ModelAdmin):

    inlines = [FieldPropertyInline, FieldKeyInline]
    fieldsets = [
        (None, {
            "fields": ("name",
                       "table",
                       "position")}),
        (_(u"Datatype"), {
            "fields": ("type",
                       "precision",
                       "scaling",
                       "default_value")}),
        (_(u"Constraints"), {
            "fields": ("primary",
                       "nullable",
                       "foreign")}),
        (_(u"Description"), {
            "fields": ("short_description",
                       "description")}),
        (_(u"Frontend"), {
            "fields": ("label",
                       "mask_length")}),
        (_(u"Database settings"), {
            "fields": ("cascading_delete",
                       "lookup")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "name", "type", "position", "primary",
                    "nullable", "foreign_table", "project", "get_table_name", "created",
                    "created_by", "updated", "updated_by")
    list_display_links = ("id", "name",)
    list_filter = ["table__project", "table", "primary"]
    ordering = ["table__project", "table", "position"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]
    raw_id_fields = ["foreign", "table"]
    search_fields = ["name"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get("using")
        if db_field.name == "foreign":
            # Only display primary keys as possible foreign key connections
            fields = models.Field.objects.filter(primary=True)
            fields.order_by("table")
            kwargs["queryset"] = fields
            kwargs["to_field_name"] = "table"
            kwargs["widget"] = PrimaryKeyRawIdWidget(db_field.rel, using=db)
            return db_field.formfield(**kwargs)
            #return forms.ModelChoiceField(
                    #queryset=fields, required=not db_field.blank,
                    #initial=db_field.primary_key)
        return super(FieldAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    #def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #if db_field.name == "foreign":
            ## Only display primary keys as possible foreign key connections
            #fields = models.Field.objects.filter(primary=True)
            #fields.order_by("table")
            #kwargs["queryset"] = fields
            ##return db_field.formfield(**kwargs)
        #return super(FieldAdmin, self).formfield_for_foreignkey(
            #db_field, request, **kwargs)

    def foreign_table(self, obj):
        if obj.foreign:
            return obj.foreign.table
        else:
            return ""
    foreign_table.short_description = _(u"Foreign table")

    def full_name(self, obj):
        return obj.full_name()
    full_name.short_description = _(u"Full name")

    def get_table_name(self, obj):
        name = obj.table.name
        url = reverse("admin:teagarden_table_changelist")
        url += "%d" % obj.table.id
        return '<a href="%s">%s</a>' % (url, name)
    get_table_name.allow_tags = True
    get_table_name.short_description = _(u"Fields")
    get_table_name.admin_order_field = "table"

    def project(self, obj):
        return obj.table.project
    project.short_description = _(u"Project")

    def save_model(self, request, obj, form, change):
        # Automatically determine the fields new position
        obj.set_next_position()
        obj.save(user=request.user.account)

    def queryset(self, request):
        query = super(FieldAdmin, self).queryset(request)
        if request.session.get("project", 0):
            project_id = request.session["project"]
            query = query.filter(table__project=int(project_id))
        return query


class FieldTypeAdmin(ModelAdmin):

    list_display = ("id", "name", "short_name", "precision", "scaling")
    list_display_links = ("id", "name",)
    ordering = ["name"]


class GroupAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("name",)}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    inlines = (TableGroupInline,)
    list_display = ("id", "name", "created", "created_by", "updated",
                    "updated_by")
    list_display_links = ("id", "name",)
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]


class PropertyAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("name",)}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "name", "created", "created_by", "updated",
                    "updated_by")
    list_display_links = ("id", "name",)
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]
    search_fields = ["name"]


class KeyAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("unique",
                       "table",
                       "name")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "name", "unique", "table", "created", "created_by",
                    "updated", "updated_by")
    list_display_links = ("id", "name",)
    ordering = ["name"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]
    raw_id_fields = ["table"]


class DefaultFieldAdmin(ModelAdmin):

    #inlines = [FieldPropertyInline, FieldKeyInline]
    fieldsets = [
        (None, {
            "fields": ("name",
                       "project",
                       "position")}),
        (_(u"Datatype"), {
            "fields": ("type",
                       "precision",
                       "scaling",
                       "default_value")}),
        (_(u"Constraints"), {
            "fields": ("primary",
                       "nullable",
                       "foreign")}),
        (_(u"Description"), {
            "fields": ("short_description",
                       "description")}),
        (_(u"Frontend"), {
            "fields": ("label",
                       "mask_length")}),
        (_(u"Database settings"), {
            "fields": ("cascading_delete",
                       "lookup")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "name", "type", "position", "primary",
                    "nullable", "foreign_table", "project", "created",
                    "created_by", "updated", "updated_by")
    list_display_links = ("id", "name",)
    list_filter = ["project"]
    ordering = ["position"]
    raw_id_fields = ["foreign"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get("using")
        if db_field.name == "foreign":
            # Only display primary keys as possible foreign key connections
            fields = models.Field.objects.filter(primary=True)
            fields.order_by("table")
            kwargs["queryset"] = fields
            kwargs["to_field_name"] = "table"
            kwargs["widget"] = PrimaryKeyRawIdWidget(db_field.rel, using=db)
            return db_field.formfield(**kwargs)
            #return forms.ModelChoiceField(
                    #queryset=fields, required=not db_field.blank,
                    #initial=db_field.primary_key)
        return super(DefaultFieldAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def foreign_table(self, obj):
        if obj.foreign:
            return obj.foreign.table
        else:
            return None
    foreign_table.short_description = _(u"Foreign table")

    def get_form(self, request, obj=None, **kwargs):
        form = super(DefaultFieldAdmin, self).get_form(request, obj, **kwargs)
        if request.session.get("project", 0):
            form.base_fields["project"].initial = request.session["project"]
        return form

    def project(self, obj):
        return obj.project
    project.short_description = _(u"Project")

    def save_model(self, request, obj, form, change):
        fields = models.DefaultField.objects.filter(project=obj.project)
        # Automatically determine the fields new position
        max = fields.aggregate(Max("position"))["position__max"] or 0
        obj.position = max + 1
        obj.save(user=request.user.account)


class TableCommentAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("is_draft",
                       "text")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "table", "is_draft", "short_text", "created",
                    "created_by", "updated", "updated_by")
    ordering = ["created"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]

    def short_text(self, obj):
        return truncatewords(obj.text, 10)
    short_text.short_description = _(u"Text")


class FieldCommentAdmin(ModelAdmin):

    fieldsets = [
        (None, {
            "fields": ("is_draft",
                       "text")}),
        (_(u"Timestamp"), {
            "classes": ("collapse",),
            "fields": ["created", "created_by", "updated", "updated_by"]})
    ]
    list_display = ("id", "field", "is_draft", "short_text", "created",
                    "created_by", "updated", "updated_by")
    ordering = ["created"]
    readonly_fields = ["created", "created_by", "updated", "updated_by"]

    def short_text(self, obj):
        return truncatewords(obj.text, 10)
    short_text.short_description = _(u"Text")


admin.site.register(models.DefaultField, DefaultFieldAdmin)
admin.site.register(models.Field, FieldAdmin)
#admin.site.register(models.FieldComment, FieldCommentAdmin)
admin.site.register(models.FieldType, FieldTypeAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Key, KeyAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Property, PropertyAdmin)
admin.site.register(models.Table, TableAdmin)
#admin.site.register(models.TableComment, TableCommentAdmin)
admin.site.register(models.TableType, TableTypeAdmin)
