from django.contrib import admin

from fromagerie.models import Package, Release, ReleaseFile, Role, Classifier

admin.site.register(Package)
admin.site.register(Release)
admin.site.register(ReleaseFile)
admin.site.register(Role)
admin.site.register(Classifier)
