from django.core.management.base import NoArgsCommand
from api_auth.models import Nonce

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        Nonce.objects.delete_old()
