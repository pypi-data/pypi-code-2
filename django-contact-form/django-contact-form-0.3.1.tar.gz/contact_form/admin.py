from django.contrib import admin
from models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
    date_hierarchy = "sent_time"
    list_display = ('user', 'name', 'email', 'sent_time')
    fields = ('user', 'name', 'email', 'body')
    search_fields = ('name', 'email', 'body')
    
    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

admin.site.register(Feedback, FeedbackAdmin)
