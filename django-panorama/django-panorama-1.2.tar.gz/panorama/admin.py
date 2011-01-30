"Admin interface for django-panorama"
from django.contrib import admin
from django import forms
from panorama.models import Panorama, ExternalLink, Note, Link
from django.core.urlresolvers import reverse
from multilingual.admin import (MultilingualModelAdmin,
                                MultilingualModelAdminForm)

class PanoramaWidget(forms.Select):
    "Select widget for panorama admin"
    class Media:
        js = ('panorama/js/jquery.js', 'panorama/js/panorama_admin.js',)

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(PanoramaWidget, self).build_attrs(extra_attrs, **kwargs)
        json_url = reverse('panorama.views.panorama_json', kwargs={'pk':999999})
        attrs['onchange'] = "update_panorama_widget(this,map,'%s')" % json_url
        return attrs

class PanoramaInfoAdmin(admin.ModelAdmin):
    """
      Base ModelAdmin for models inheriting PanoramaInfo.

      Defines common values such as list_display and list_filter.
    """
    base_list_display = ('title', 'panorama',)
    base_list_filter = ('panorama',)

    def __init__(self, *args, **kwargs):
        self.list_display = self.base_list_display + self.list_display
        self.list_filter = self.base_list_filter + self.list_filter
        super(PanoramaInfoAdmin, self).__init__(*args, **kwargs)

class ExternalLinkForm(MultilingualModelAdminForm):
    "Admin form for Panorama ExternalLink"
    panorama = forms.ModelChoiceField(queryset=Panorama.objects.all(),
                                      widget=PanoramaWidget())
    class Meta:
        model = ExternalLink

class ExternalLinkAdmin(MultilingualModelAdmin, PanoramaInfoAdmin):
    "Administration of Panorama ExternalLinks"
    form = ExternalLinkForm
    #TODO: use_fieldests don't work in django 1.3-beta-1, watch multilingual_ng
    #use_fieldsets = (
    #        (None, {'fields': (('title', 'panorama', 'url'),),}),
    #        ('Advanced options', {
    #            'classes':('collapse',),
    #            'fields':(('x0', 'x1', 'y0', 'y1'),),
    #            }),
    #        )
    list_display = ('url',)

class NoteForm(MultilingualModelAdminForm):
    "Admin form for Panorama Note"
    panorama = forms.ModelChoiceField(queryset=Panorama.objects.all(),
                                      widget=PanoramaWidget())
    class Meta:
        model = Note

class NoteAdmin(MultilingualModelAdmin, PanoramaInfoAdmin):
    "Administration of Panorama Notes"
    form = NoteForm
    #use_fieldsets = (
    #        (None, {'fields': (('title',),
    #                           ('description',),
    #                           ('panorama' ),),}),
    #        ('Advanced options', {
    #            'classes':('collapse',),
    #            'fields':(('x0', 'x1', 'y0', 'y1'),),
    #            }),
    #        )

class LinkForm(forms.ModelForm):
    "Admin form for Panorama Link"
    panorama = forms.ModelChoiceField(queryset=Panorama.objects.all(),widget=PanoramaWidget())
    class Meta:
        model = Link

class LinkAdmin(admin.ModelAdmin):
    form = LinkForm
    fieldsets = (
            (None, {'fields': (('panorama', 'target_panorama'),),}),
            ('Advanced options', {
                'classes':('collapse',),
                'fields':(('x0','x1','y0','y1'),),
                }),
            )



#class PanoramaAdmin(MultilingualModelAdmin):
#    use_fieldsets = (
#            (None, {'fields': (('title', 'image'),),}),
#            ('Display options', {
#                'classes':('collapse',),
#                'fields':(('viewport_width',),
#                          ('speed',),
#                          ('direction',),
#                          ('control_display',),
#                          ('start_position',),
#                          ('auto_start',),
#                          ('mode_360',),
#                         ),
#            }),
#    )


#admin.site.register(Panorama, PanoramaAdmin)
admin.site.register(Panorama, MultilingualModelAdmin)
admin.site.register(ExternalLink, ExternalLinkAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Link, LinkAdmin)
