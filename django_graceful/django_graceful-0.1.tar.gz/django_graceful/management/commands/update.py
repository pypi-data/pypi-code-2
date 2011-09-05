from django_graceful import Graceful
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Restarts inactive backend and switches to it."
    
    def handle_noargs(self, **options):
        graceful = Graceful()
        j = 0
        for i in range(len(graceful.backends)):
            if graceful.backends[i].is_active():
                j = (i + 1) % len(graceful.backends)
                break
        if graceful.backends[j].is_up():
            graceful.backends[j].stop()
        graceful.backends[j].start()
        if not graceful.backends[j].is_active():
            graceful.backends[j].switch()

