from difflib import unified_diff
import os

from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe

from reversion.admin import VersionAdmin

from models import Group, Template


MEDIA_PREFIX = getattr(settings, "MAGNETO_MEDIA_DIRECTORY",
    os.path.join(settings.MEDIA_URL, "magneto/"))


class CodeMirrorTextArea(forms.Textarea):

    class Media:
        css = dict(screen=[os.path.join(MEDIA_PREFIX,
            "codemirror/css/editor.css")])
        js = [os.path.join(MEDIA_PREFIX, "codemirror/js/codemirror.js")]

    def render(self, name, value, attrs=None):
        result = []
        result.append(super(CodeMirrorTextArea,
            self).render(name, value, attrs))

        result.append(u"""<p>View the Django <a href="http://docs.djangoproject.com/en/dev/ref/templates/builtins/">built-in tags and filters</a>.</p>""")

        result.append(u"""
<script type="text/javascript">
  var editor = CodeMirror.fromTextArea('id_%(name)s', {
    path: "%(media_url)scodemirror/js/",
    parserfile: "parsedjango.js",
    stylesheet: "%(media_url)scodemirror/css/django.css",
    continuousScanning: 500,
    height: "40.2em",
    tabMode: "shift",
    indentUnit: 2,
    lineNumbers: true
  });
</script>
""" % dict(media_url=MEDIA_PREFIX, name=name))
        return mark_safe(u"".join(result))


class GroupAdmin(admin.ModelAdmin):
    pass
admin.site.register(Group, GroupAdmin)


class TemplateAdminForm(forms.ModelForm):
    content = forms.CharField(
        widget=CodeMirrorTextArea(dict(rows=24))
    )

    class Meta:
        model = Template


class TemplateAdmin(VersionAdmin):
    actions = ("copy_templates", )
    date_hierarchy = "date_created"
    form = TemplateAdminForm
    list_display = ("name", "content_type", "group", "site", "visible", )
    list_filter = ("content_type", "group", "visible", "site", )
    list_per_page = 100
    object_history_template = "magneto/object_history.html"
    ordering = ("name", )
    readonly_fields = ("date_created", "date_changed",
        "last_modified_by", )
    search_fields = ("name", )

    def __init__(self, *args, **kwargs):
        self.message = "Changed content."
        super(TemplateAdmin, self).__init__(*args, **kwargs)

    def copy_templates(self, request, queryset):
        for obj in queryset:
            Template.objects.create(
                name="%s-copy" % obj.name,
                content_type=obj.content_type,
                content=obj.content,
                group=obj.group,
                site=obj.site,
                visible=obj.visible,
            )
    copy_templates.short_description = "Copy selected templates"

    def log_change(self, request, obj, message=""):
        message = message or self.message
        super(TemplateAdmin, self).log_change(request, obj, self.message)

    def save_model(self, request, obj, form, change):
        if obj.pk:
            self.message = generate_diff(
                Template.objects.get(pk=obj.pk), obj)
        obj.last_modified_by = request.user
        obj.save()
admin.site.register(Template, TemplateAdmin)


def generate_diff(old, new):
    c1 = old.content.split("\n")
    c2 = new.content.split("\n")
    return "\n".join(list(unified_diff(c1, c2)))
