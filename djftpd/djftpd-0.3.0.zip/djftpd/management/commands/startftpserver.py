from django.core.management.base import NoArgsCommand
from django.conf import settings

from djftpd.authorizer import create_django_ftpserver

class Command(NoArgsCommand):
    help = "Starts the django FTP server"

    def handle_noargs(self, **options):
        print "options", options
        ftpd = create_django_ftpserver()
        ftpd.serve_forever()
