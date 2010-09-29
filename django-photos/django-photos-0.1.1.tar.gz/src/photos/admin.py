from django.contrib import admin
from photos.models import Photo, Album
from django.utils.translation import ugettext as _

class BaseAdmin():
    def queryset(self, request):
        qs = super(PhotoAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class PhotoAdmin(admin.ModelAdmin, BaseAdmin):
    list_filter = ('display', 'timestamp_created', )
    date_hierarchy = 'timestamp_created'
    description = _('Manage your uploaded photos.')

admin.site.register(Photo, PhotoAdmin)

class AlbumAdmin(admin.ModelAdmin, BaseAdmin):
    list_filter = ('display', 'timestamp_created', )
    date_hierarchy = 'timestamp_created'
    description = _('Manage your galleries.')
    
admin.site.register(Album, AlbumAdmin)