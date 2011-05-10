from django.contrib import admin
from models import Photo

class PhotoAdmin(admin.ModelAdmin):
    date_hierarchy = 'exif_date'
    fields = ('title', 'image')
    list_filter = ('camera_model', 'fnumber', 'iso_speed',)
    list_display = ('thumbnail_url', 'title', 'width', 'height', 'camera_model', 'fnumber', 'iso_speed',)

admin.site.register(Photo, PhotoAdmin)
