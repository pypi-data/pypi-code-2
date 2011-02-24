import os
import logging
from pyftpdlib import ftpserver

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings

#
# Configuration, read from settings.py
#
SETTINGS_MODULE_NAME = os.environ['DJANGO_SETTINGS_MODULE']
custom_settings = __import__(SETTINGS_MODULE_NAME, globals(), locals(), [], -1)

read_perms = "elr"
if hasattr(custom_settings.settings, 'read_perms'):
    read_perms = custom_settings.settings.read_perms

write_perms = "adfmw"
if hasattr(custom_settings.settings, 'write_perms'):
    read_perms = custom_settings.settings.write_perms

if hasattr(custom_settings.settings, 'ftp_handler'):
    logging.debug('Using custom ftp_handler-method defined in settings.py.')
    ftp_handler = custom_settings.settings.ftp_handler
else:
    ftp_handler = ftpserver.FTPHandler

if hasattr(custom_settings.settings, 'FTP_PORT'):
    FTP_PORT = custom_settings.settings.FTP_PORT
else:
    FTP_PORT = 21

if hasattr(custom_settings.settings, 'FTP_ADDRESS'):
    FTP_ADDRESS = custom_settings.settings.FTP_ADDRESS
else:
    FTP_ADDRESS = '127.0.0.1'

if hasattr(custom_settings.settings, 'get_ftp_home_dir'):
    logging.debug('Using custom get_ftp_home_dir-method defined in settings.py.')
    get_ftp_home_dir = custom_settings.settings.get_ftp_home_dir
else:
    get_ftp_home_dir = lambda username: settings.MEDIA_ROOT and settings.MEDIA_ROOT or os.path.abspath('.')

FTP_WELCOME_MSG = 'Welcome to the Django-FTP Server'
if hasattr(custom_settings.settings, 'FTP_WELCOME_MSG'):
    FTP_WELCOME_MSG = custom_settings.settings.FTP_WELCOME_MSG

"""
Authorizer class: upon login users will be authenticated against the user
database created and maintained in django.
"""
class DjangoFtpAuthorizer:

    def has_user(self, username):
        try:
            u = User.objects.get(username = username)
            return True
        except:
            return False

    def get_home_dir(self, username):
        try:
            return get_ftp_home_dir(username)
        except Exception, e:
            logging.warning("Error getting home dir for user %s. Exception was %s." % (username, e))
            return None

    def get_msg_login(self, username):
        return FTP_WELCOME_MSG

    def get_msg_quit(self, username):
        return 'Please come again'

    def r_perm(self, username, obj=None):
        try:
            return read_perms
        except:
            return False

    def w_perm(self, username, obj=None):
        try:
            return write_perms
        except:
            return False

    def has_perm(self, username, perm, path=None):
        u = User.objects.get(username = username)
        if u.is_superuser:
            return write_perms+read_perms
        else:
            return perm in read_perms
    
    def impersonate_user(self, username, password):
        """Impersonate another user (noop).

        It is always called before accessing the filesystem.
        By default it does nothing.  The subclass overriding this
        method is expected to provide a mechanism to change the
        current user.
        """
        pass

    def terminate_impersonation(self, dummy):
        """Terminate impersonation (noop).

        It is always called after having accessed the filesystem.
        By default it does nothing.  The subclass overriding this
        method is expected to provide a mechanism to switch back
        to the original user.
        """
        pass

    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except:
            raise

    def validate_authentication(self, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                return True
        return False

def create_django_ftpserver(authorizer = None, handler = None):
    ftp_handler.authorizer = authorizer and authorizer or DjangoFtpAuthorizer()
    if handler:
        ftp_handler.ftp_handler = handler
    ftpd = ftpserver.FTPServer((FTP_ADDRESS, FTP_PORT), ftp_handler)
    return ftpd