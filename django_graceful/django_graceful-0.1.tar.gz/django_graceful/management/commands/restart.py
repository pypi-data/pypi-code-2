from django_graceful import Graceful
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

class Command(BaseCommand):
    help = "Restarts specified backends, even stopped ones."

    option_list = (
        make_option('--all', help='Restart all running backends', action='store_true'),
        make_option('--inactive', help='Restart all inactive backends', action='store_true'),
    ) + BaseCommand.option_list
    
    def handle(self, *args, **options):
        graceful = Graceful()
        all = options['all']
        inactive = options['inactive']
        if not (args and (not all) and (not inactive) or (not args) and all and (not inactive) or (not args) and (not all) and inactive):
            raise CommandError('Specify backend names to restart or give --all to restart every backend or --inactive to restart all inactive backends.')
        restartlist = []
        if all:
            restartlist = list(graceful.backends)
        elif inactive:
            restartlist = [b for b in graceful.backends if not b.is_active()]
        else:
            for a in args:
                try:
                    restartlist.append(graceful.map[a])
                except KeyError:
                    raise CommandError('Backend "%s" does not exist.' % a)
        for b in restartlist:
            if b.is_up():
                b.stop()
            b.start()

