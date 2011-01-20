from django.contrib import admin
from django import forms
from models import Panorama, PanoramaExternalLink, PanoramaNote
from django.core.urlresolvers import reverse
from multilingual.admin import MultilingualModelAdmin
from multilingual.admin import MultilingualModelAdminForm

class PanoramaWidget(forms.Select):
    class Media:
        js = ('panorama/js/jquery.js','panorama/js/panorama_admin.js',)

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(PanoramaWidget,self).build_attrs(extra_attrs,**kwargs)
        json_url = reverse('panorama.views.panorama_json',kwargs={'pk':999999})
        attrs['onchange']="update_panorama_widget(this,map,'%s')" % json_url
        return attrs

class PanoramaInfoAdmin(admin.ModelAdmin):
    """
      Base ModelAdmin for models inheriting PanoramaInfo.

      Defines common values such as list_display and list_filter.
    """
    base_list_display = ('title','panorama',)
    base_list_filter = ('panorama',)

    def __init__(self, *args, **kwargs):
        self.list_display = self.base_list_display + self.list_display
        self.list_filter = self.base_list_filter + self.list_filter
        super(PanoramaInfoAdmin,self).__init__(*args, **kwargs)

class PanoramaExternalLinkForm(MultilingualModelAdminForm):
    panorama = forms.ModelChoiceField(queryset=Panorama.objects.all(),widget=PanoramaWidget())
    class Meta:
        model = PanoramaExternalLink

class PanoramaExternalLinkAdmin(MultilingualModelAdmin, PanoramaInfoAdmin):
    form = PanoramaExternalLinkForm
    #TODO: this use_fieldests don't work in django 1.3-beta-1, watch multilingual_ng
    #use_fieldsets = (
    #        (None, {'fields': (('title', 'panorama', 'url'),),}),
    #        ('Advanced options', {
    #            'classes':('collapse',),
    #            'fields':(('x0','x1','y0','y1'),),
    #            }),
    #        )
    list_display = ('url',)

class PanoramaNoteForm(MultilingualModelAdminForm):
    panorama = forms.ModelChoiceField(queryset=Panorama.objects.all(),widget=PanoramaWidget())
    class Meta:
        model = PanoramaNote

class PanoramaNoteAdmin(MultilingualModelAdmin, PanoramaInfoAdmin):
    form = PanoramaNoteForm
    #use_fieldsets = (
    #        (None, {'fields': (('title',), ('description',), ('panorama' ),),}),
    #        ('Advanced options', {
    #            'classes':('collapse',),
    #            'fields':(('x0','x1','y0','y1'),),
    #            }),
    #        )


admin.site.register(Panorama, MultilingualModelAdmin)
admin.site.register(PanoramaExternalLink, PanoramaExternalLinkAdmin)
admin.site.register(PanoramaNote, PanoramaNoteAdmin)
