from demo.models import SessionDatabase
from django.contrib import admin

def kill(modeladmin, request, queryset):
    for obj in queryset:
        obj.kill(False)
    queryset.delete()
kill.short_description = "Kill databases"

class SessionDatabaseAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'death')
    actions = [kill]
    

admin.site.register(SessionDatabase, SessionDatabaseAdmin)