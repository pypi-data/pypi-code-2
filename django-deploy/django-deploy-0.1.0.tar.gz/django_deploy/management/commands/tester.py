from django.core.management.base import BaseCommand, CommandError
from django_deploy.system import postgis_database
from django_deploy.utils import fab_task

class Command(BaseCommand):
    
    @fab_task
    def handle(self, *args, **kwargs):
        postgis_database()

