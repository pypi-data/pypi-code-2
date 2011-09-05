from django_graceful import Graceful
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Ensures there is a running backend and it's active."
    
    def handle_noargs(self, **options):
        graceful = Graceful()
        up = []
        for b in graceful.backends:
            if b.is_up():
                if b.is_active():
                    return
                else:
                    up.append(b)
        if up:
            up[0].switch()
        else:
            graceful.backends[0].start()
            if not graceful.backends[0].is_active():
                graceful.backends[0].switch()

