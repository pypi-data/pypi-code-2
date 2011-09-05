from django_graceful import Graceful
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Shows backends list with running/active status."
    
    def handle_noargs(self, **options):
        for b in Graceful().backends:
            print b

