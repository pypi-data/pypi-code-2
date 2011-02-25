from optparse import make_option
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import loader, Context

from django_vhost import settings as v_settings
from django_vhost.utils import get_amedia_dir


class Command(BaseCommand):
    help = "Generate nginx fastcgi virtualhost configuration."
    base_options = (
        make_option('-d', '--directory', action='store', dest='directory',
        default=v_settings.PROJECT_ROOT,
        help='Directory where project will be placed.'
        ),
        make_option('-p', '--port', action='store', type='int', dest='port',
            default=v_settings.BACKEND_PORT,
            help='Port backend instance will be running on.'
        ),
        make_option('-n', '--hostname', action='store', type='string',
            dest='hostname', default=v_settings.HOST_DOMAIN,
            help='Main domain for project'
        ),
        make_option("-o", "--outputfile", action="store", type="string",
            dest="outputfile",
            help='If provided, directs output to a file instead of stdout.'
        ))
    option_list = BaseCommand.option_list + base_options

    def handle(self, **options):
        """Generate nginx fastcgi virtualhost configuration."""

        # Get options context
        context = Context({
            'directory': options.get('directory'),
            'port': options.get('port'),
            'hostname': options.get('hostname'),
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
            'admin_media': get_amedia_dir(),
            'media_url': settings.MEDIA_URL,
            'media_root': settings.MEDIA_ROOT
        })

        host_config = self.build_template(context)

        # Store nginx configuration in file
        if options.get('outputfile'):
            self.write_file(options.get('outputfile'), host_config)
        else:
            self.print_stdout(host_config)

    def build_template(self, context):
        t = loader.get_template('django_vhost/nginx-fastcgi.conf')
        return t.render(context)

    def print_stdout(self, host_config):
        sys.stderr.write("\n")
        sys.stderr.write("Save the following output " +
            "and place it in your Nginx configuration directory.\n")
        sys.stderr.write("=" * 100 + "\n")
        sys.stderr.write("\n")
        print host_config

    def write_file(self, filename, host_config):
        schema_file = open(filename, 'w')
        schema_file.write(host_config)
        schema_file.close()
