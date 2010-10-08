from django.contrib import admin
from photos.models import Photo, Album
from django.utils.translation import ugettext as _
from django.template.loader import get_template
from django.template import Context

class BaseAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = super(BaseAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class PhotoAdmin(BaseAdmin):
    list_filter = ('display', 'timestamp_created', )
    list_display = ('name', 'display', 'timestamp_created', 'get_thumbnail', )
    date_hierarchy = 'timestamp_created'
    description = _('Manage your uploaded photos.')
    
    def get_thumbnail(self, obj):
        template = get_template('photos/admin_thumbnail.html')
        context = Context({'photo': obj})
        return template.render(context)
    
    get_thumbnail.allow_tags = True
    get_thumbnail.short_description = _('Thumbnail')

admin.site.register(Photo, PhotoAdmin)

class AlbumAdmin(BaseAdmin):
    list_filter = ('display', 'timestamp_created', )
    date_hierarchy = 'timestamp_created'
    description = _('Manage your galleries.')
    filter_horizontal = ('photos', )
    
admin.site.register(Album, AlbumAdmin)

