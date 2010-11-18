from django.contrib import admin
from django.conf import settings

from django.http import HttpResponse
from django.utils.text import capfirst
from django.template.defaultfilters import title, escape, force_escape, escapejs
from django.forms import CharField

from cms.models.pluginmodel import CMSPlugin
from cms.forms.widgets import PlaceholderPluginEditorWidget
from cms.admin.placeholderadmin import PlaceholderAdmin

def get_or_create_placeholders(obj, model):
    if obj:
        for placeholder_name in model._meta.get_field('placeholders').placeholders:
            placeholder, created = obj.placeholders.get_or_create(slot=placeholder_name)
            yield (placeholder, placeholder_name)
    else:
        for placeholder_name in model._meta.get_field('placeholders').placeholders:
            yield (None, placeholder_name)    
            
def get_m2mplaceholderadmin(modeladmin):
    class RealM2MPlaceholderAdmin(modeladmin):
        
        def get_form(self, request, obj=None, **kwargs):
            """
            Get PageForm for the Page model and modify its fields depending on
            the request.
            """
            form = super(RealM2MPlaceholderAdmin, self).get_form(request, obj, **kwargs)
            
            for placeholder, slot in get_or_create_placeholders(obj, self.model):

                defaults = {'label': capfirst(slot), 'help_text': ''}
                defaults.update(kwargs)
                    
                widget = PlaceholderPluginEditorWidget(request, self.placeholder_plugin_filter)
                widget.choices = []
                    
                form.base_fields[slot] = CharField(widget=widget, required=False)
                
                if placeholder:   
                    form.base_fields[slot].initial = placeholder.pk
                    
            return form
            
        def get_fieldsets(self, request, obj=None):
            """
            Add fieldsets of placeholders to the list of already existing
            fieldsets.
            """
            given_fieldsets = super(RealM2MPlaceholderAdmin, self).get_fieldsets(request, obj=None)

            for placeholder_name in self.model._meta.get_field('placeholders').placeholders:
                given_fieldsets += [(title(placeholder_name), {'fields':[placeholder_name], 'classes':['plugin-holder']})]
    
            return given_fieldsets
                
        def move_plugin(self, request):
            
            def get_placeholder(plugin, request):
                
                return plugin.placeholder
                
            if request.method == "POST":    
                if 'plugin_id' in request.POST:
                    plugin = CMSPlugin.objects.get(pk=int(request.POST['plugin_id']))
                    if "placeholder" in request.POST:
                        obj = plugin.placeholder._get_attached_model().objects.get(placeholders__cmsplugin=plugin)
                        placeholder = obj.placeholders.get(slot=request.POST["placeholder"])
                    else:
                        placeholder = plugin.placeholder
                    # plugin positions are 0 based, so just using count here should give us 'last_position + 1'
                    position = CMSPlugin.objects.filter(placeholder=placeholder).count()
                    plugin.placeholder = placeholder
                    plugin.position = position
                    plugin.save()
                pos = 0
                if 'ids' in request.POST:
                    for id in request.POST['ids'].split("_"):
                        plugin = CMSPlugin.objects.get(pk=id)
                        if plugin.position != pos:
                            plugin.position = pos
                            plugin.save()
                        pos += 1
                else:
                    HttpResponse(str("error"))
                return HttpResponse(str("ok"))
            else:
                return HttpResponse(str("error"))
    return RealM2MPlaceholderAdmin

M2MPlaceholderAdmin = get_m2mplaceholderadmin(PlaceholderAdmin)