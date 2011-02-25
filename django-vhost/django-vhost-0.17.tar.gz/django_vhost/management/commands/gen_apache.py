from optparse import make_option
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import loader, Context

from django_vhost import settings as v_settings
from django_vhost.utils import get_amedia_dir


class Command(BaseCommand):
    help = "Generate apache wsgi virtualhost configuration."
    base_options = (
        make_option('-d', '--directory', action='store', dest='directory',
        default=v_settings.PROJECT_ROOT,
        help='Directory where project will be placed.'
        ),
        make_option('-n', '--hostname', action='store', type='string',
            dest='hostname', default=v_settings.HOST_DOMAIN,
            help='Main domain for project'
        ),
        make_option("-o", "--outputfile", action="store", type="string",
            dest="outputfile",
            help='If provided, directs output to a file instead of stdout.'
        ),
        make_option("-u", "--wsgi_user", action="store", type="string",
            dest="wsgi_user", default=v_settings.WSGI_USER,
            help='WSGI user.'
        ),
        make_option("-g", "--wsgi_group", action="store", type="string",
            dest="wsgi_group", default=v_settings.WSGI_GROUP,
            help='WSGI group.'
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
            'media_root': settings.MEDIA_ROOT,
            'wsgi_user': options.get('wsgi_user'),
            'wsgi_group': options.get('wsgi_group'),
            'wsgi_path': v_settings.WSGI_PATH
        })

        host_config = self.build_template(context)

        # Store nginx configuration in file
        if options.get('outputfile'):
            self.write_file(options.get('outputfile'), host_config)
        else:
            self.print_stdout(host_config)

    def build_template(self, context):
        t = loader.get_template('django_vhost/apache-wsgi.conf')
        return t.render(context)

    def print_stdout(self, host_config):
        sys.stderr.write("\n")
        sys.stderr.write("Save the following output " +
            "and place it in your Apache configuration directory.\n")
        sys.stderr.write("=" * 100 + "\n")
        sys.stderr.write("\n")
        print host_config

    def write_file(self, filename, host_config):
        schema_file = open(filename, 'w')
        schema_file.write(host_config)
        schema_file.close()
