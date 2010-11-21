from optparse import make_option

from django.conf import settings
from django.core.management.base import AppCommand, CommandError
from django.core.management.color import no_style

class Command(AppCommand):
    option_list = AppCommand.option_list + (
        make_option('--overwrite', action='store_true', dest='overwrite',
            default=False, help='Overwrite existing templates'
               ),
    )
    help = "Copy's all templates from the appname(s)"
    args = '[appname ...]'

    def handle_app(self, app, **options):
      overwrite = options.get('database')
      app_name = app.__name__.split('.')[-2]
      print app_name
      print app
      print app.__name__
      