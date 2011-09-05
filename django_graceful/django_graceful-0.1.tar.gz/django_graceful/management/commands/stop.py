from django_graceful import Graceful
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

class Command(BaseCommand):
    help = "Stops specified backends."

    option_list = (
        make_option('--all', help='Stop all running backends', action='store_true'),
        make_option('--inactive', help='Stop all inactive backends', action='store_true'),
    ) + BaseCommand.option_list
    
    def handle(self, *args, **options):
        graceful = Graceful()
        all = options['all']
        inactive = options['inactive']
        if not (args and (not all) and (not inactive) or (not args) and all and (not inactive) or (not args) and (not all) and inactive):
            raise CommandError('Specify backend names to stop or give --all to stop every running backend or --inactive to stop all inactive running backends.')
        stoplist = []
        if all:
            stoplist = [b for b in graceful.backends if b.is_up()]
        elif inactive:
            stoplist = [b for b in graceful.backends if b.is_up() and (not b.is_active())]
        else:
            for a in args:
                try:
                    stoplist.append(graceful.map[a])
                except KeyError:
                    raise CommandError('Backend "%s" does not exist.' % a)
        for b in stoplist:
            b.stop()

