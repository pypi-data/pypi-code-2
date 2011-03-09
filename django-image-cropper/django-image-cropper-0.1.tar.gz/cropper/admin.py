from django.contrib import admin
from cropper.models import Original, Cropped

class OriginalAdmin(admin.ModelAdmin):
    ''

class CroppedAdmin(admin.ModelAdmin):
    ''
    
admin.site.register(Original, OriginalAdmin)
admin.site.register(Cropped, CroppedAdmin)