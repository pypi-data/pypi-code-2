from indeed_contactForm.models import Message
from django.contrib import admin


class MessageAdmin(admin.ModelAdmin):
	list_display = ('subject', 'mail', 'date', 'new')
	date_hierarchy = 'date'
	list_filter = ('date','new',)
	ordering = ('-new', '-date',)


admin.site.register(Message, MessageAdmin)
