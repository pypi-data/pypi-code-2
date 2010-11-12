from demo.models import SessionDatabase
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        SessionDatabase.objects.kill()