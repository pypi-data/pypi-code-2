from django.contrib import admin
from models import LogEntry
from context import get_singleton_context

class LogEntryAdmin(admin.ModelAdmin):
    fields = ('loglevel',  'text', 'context_name', 'user',)
    list_display = ('date_added', 'loglevel',  'short_text', 'context_name', 'user_text', 'content_link','view_details',)
    list_filter = ('loglevel', 'context_name', 'user', 'content_type',)
    date_hierarchy = 'date_added'

    def queryset(self, request):
        ctx = get_singleton_context("admin_context")
        ctx.flush()
        return super(LogEntryAdmin, self).queryset(request)


admin.site.register(LogEntry, LogEntryAdmin)
