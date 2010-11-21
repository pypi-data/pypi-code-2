from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
from django.utils.importlib import import_module
from django.core.management.color import no_style

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--overwrite', action='store_true', dest='overwrite',
            default=False, help='Overwrite existing templates'
               ),
    )
    help = "Copy's all templates from the appname"
    args = '[appname]'

    def handle(self, *args, **options):
      overwrite = options.get('overwrite')
      mod = import_module(args[0])
      templates_path = mod.__path__
      print mod.__path__
      
      print dir(mod)
      #app_name = app.__name__.split('.')[-2]
      #print app_name
      #print app
      #print app.__name__
      