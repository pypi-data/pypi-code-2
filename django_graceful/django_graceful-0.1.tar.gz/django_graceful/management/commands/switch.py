from django_graceful import Graceful
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Switches to specified backend."

    def handle(self, *args, **options):
        graceful = Graceful()
        if len(args) > 1 or not args:
            raise CommandError('You should specify ONE backend name to switch to.')
        try:
            graceful.map[args[0]].switch()
        except KeyError:
            raise CommandError('Backend "%s" does not exist.' % a)

