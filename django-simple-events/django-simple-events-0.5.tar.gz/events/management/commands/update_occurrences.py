from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.db.models import Q

from events.models import Event

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        q = Q(end__isnull=True)
        q |= Q(repetitions__isnull=True)
        for event in Event.objects.filter(q):
            print(_('Updating occurrences for %s') % event)
            event.save()
