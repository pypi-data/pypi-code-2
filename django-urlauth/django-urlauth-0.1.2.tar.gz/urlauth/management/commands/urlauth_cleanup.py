from datetime import datetime

from django.core.management.base import BaseCommand

from account.models import AuthKey

class Command(BaseCommand):
    help = 'Remove expired keys from database'

    def handle(self, *args, **kwargs):
        qs = AuthKey.objects.filter(expired__lt=datetime.now())
        count = qs.count()
        qs.delete()
        print '%d keys deleted' % count
