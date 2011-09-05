from django_graceful import Graceful
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

class Command(BaseCommand):
    help = "Starts specified backends."

    option_list = (
        make_option('--all', help='Start all available backends', action='store_true'),
    ) + BaseCommand.option_list
    
    def handle(self, *args, **options):
        graceful = Graceful()
        all = options['all']
        if not (args and (not all) or (not args) and all):
            raise CommandError('Specify backend names to start or give --all to start everyone available.')
        startlist = []
        if all:
            startlist = list(graceful.backends)
        else:
            for a in args:
                try:
                    startlist.append(graceful.map[a])
                except KeyError:
                    raise CommandError('Backend "%s" does not exist.' % a)
        for b in startlist:
            b.start()

