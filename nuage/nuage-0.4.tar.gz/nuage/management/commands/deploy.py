import os
import tempfile
import tarfile
import base64
import urllib
import urllib2
from getpass import getpass
from django.core.management.base import BaseCommand
# from optparse import make_option
from django.conf import settings


class Command(BaseCommand):

    help = 'Deploy an application in nuage infrastructure'

    def handle(self, *args, **options):
        print "Start deploying."

        # User's email
        ask_write_email = False
        if hasattr(settings, 'NUAGE_EMAIL'):
            email = settings.NUAGE_EMAIL
        else:
            ask_write_email = True
            email = raw_input("Please enter your email: ")

        # User's deployment key
        ask_write_key = False
        if hasattr(settings, 'NUAGE_KEY'):
            key = settings.NUAGE_KEY
        else:
            ask_write_key = True
            key = getpass("Please enter your deployment key: ")

        # Application's name
        ask_write_application = False
        if hasattr(settings, 'NUAGE_APPLICATION'):
            application = settings.NUAGE_APPLICATION
        else:
            ask_write_application = True
            application = raw_input("Please enter the application's name: ")

        # application's version
        ask_write_version = False
        if hasattr(settings, 'NUAGE_VERSION'):
            version = settings.NUAGE_VERSION
        else:
            ask_write_version = True
            version = raw_input("Please enter the application's version: ")

        # Import settings.
        settings_module = __import__(settings.SETTINGS_MODULE)
        dirname = os.path.dirname(settings_module.__file__)

        if ask_write_email or ask_write_version or \
               ask_write_application or ask_write_key:

            ask_write = raw_input("Save this information for future "\
                                  "usage in settings.py? [y/N]: ")

            if ask_write == 'y':
                print "Information saved."
                fd = open(os.path.join(dirname, 'settings.py'), 'a')
                fd.write("\n# Information saved by Nuage.\n")
                if ask_write_email:
                    fd.write("NUAGE_EMAIL = '%s'\n" % (email, ))
                if ask_write_key:
                    fd.write("NUAGE_KEY = '%s'\n" % (key, ))
                if ask_write_application:
                    fd.write("NUAGE_APPLICATION = '%s'\n" % (application, ))
                if ask_write_version:
                    fd.write("NUAGE_VERSION = '%s'\n" % (version, ))
                fd.write("\n")
                fd.close()

        # Prepare
        print "Preparing to deploy in %(version)s."\
              "%(application)s.apps.cenuage.com ..." % {
            'version': version,
            'application': application,
            }

        # Start compressing
        tempfd = tempfile.NamedTemporaryFile()

        # Create tar.
        tar = tarfile.open(tempfd.name, mode='w:gz')

        def exclude_file(name):
            for ends in ['.pyc', '#', '~']:
                if name.endswith(ends):
                    return True
            return False

        tar.add(dirname, application, exclude=exclude_file)

        # Write to file.
        tar.close()

        # Send file
        # SSH or POST ?
        payload = base64.encodestring(tempfd.read())
        data = urllib.urlencode({
            'email': email,
            'key': key,
            'application': application,
            'version': version,
            'payload': payload,
            })

        # Make request.
        url = 'http://test.cenuage.com/upload'
        request = urllib2.Request(url, data)
        try:
            response = urllib2.urlopen(request)
            print response.read()
        except IOError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.Reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
