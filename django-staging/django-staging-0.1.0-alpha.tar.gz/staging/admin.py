from django.contrib import admin

from staging.models import StagingServer


admin.site.register(StagingServer, admin.ModelAdmin)
