import datetime

from django.conf import settings
from django.core import management
from django.utils.translation import ugettext as _

from svnlit import models


class Command(management.BaseCommand):
    help = _('Clean up expired cached files')
    
    def handle(self, *args, **options):
        threshold = datetime.datetime.now() - datetime.timedelta(
            0, settings.SVNLIT_CACHE_TIMEOUT)
        nodes = models.Node.objects.filter(cached__lte=threshold)
        if nodes.count():
            print _('Deleting %s nodes...') % nodes.count()
            nodes.delete()
