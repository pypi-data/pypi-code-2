from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from datetime import datetime

from events.models import Event
from events.forms import EventForm

class EventAdmin(admin.ModelAdmin):
    form = EventForm
    list_filter = 'frecuency',
    list_display = 'beginning', 'time', 'duration', 'frecuency', 'repetitions', 'end'
    fields = 'beginning', 'time', 'duration', 'frecuency', 'repetitions', 'end'
    actions = 'finish',
    date_hierarchy = 'beginning'

    def finish(self, request, queryset):
        queryset.update(end=datetime.now())
    finish.short_description = _('Finish selected events')
admin.site.register(Event, EventAdmin)

class EventInline(generic.GenericTabularInline):
    model = Event
    form = EventForm
    extra = 0
