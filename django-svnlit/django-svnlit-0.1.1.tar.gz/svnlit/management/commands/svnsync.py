from django.core import management
from django.utils.translation import ugettext as _

from svnlit import models


class Command(management.BaseCommand):
    help = _('Get repository changes')
    args = _('<repository repository ...>')
    
    def handle(self, *args, **options):
        if args:
            try:
                rlist = map(
                    lambda r: models.Repository.objects.get(label=r), args)
            except models.Repository.DoesNotExist, error:
                raise management.CommandError(error)
        else:
            rlist = models.Repository.objects.all()
        
        for r in rlist:
            print _('Syncing %(label)s...') % {'label': r.label}
            r.sync()
