
#from django_tools.utils import info_print;info_print.redirect_stdout()

DEBUG = True
#DEBUG = False

MESSAGE_DEBUG = True

SQL_DEBUG = False
#TEMPLATE_DEBUG = True
TEMPLATE_DEBUG = False

#PYLUCID_OBJECTS_DEBUG = True

from pylucid_project.apps.pylucid import app_settings as PYLUCID
PYLUCID.I18N_DEBUG = False

# Serve static files for the development server?
# Using this method is inefficient and insecure.
# Do not use this in a production setting. Use this only for development.
SERVE_STATIC_FILES = True

# Database connection info.
# see: http://docs.djangoproject.com/en/dev/ref/settings/#setting-DATABASES
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db3'
#        'NAME': '/home/jens/PyLucid_env/PyLucid v0.8.7full.db3'
    }
}

# external plugins
from kurs_anmeldung import kurs_anmeldung_settings as KURS_ANMELDUNG
from weave import app_settings as WEAVE

DEFAULT_FROM_EMAIL = "test@jensdiemer.de"

FILEBROWSER_DEBUG = True
FILEBROWSER_DIRECTORY = ""
FILEBROWSER_MEDIA_ROOT = "/home/jens/PyLucid_env/src/pylucid/pylucid_project/media/"
FILEBROWSER_MEDIA_URL = "/media/"

ADMINS = (
    ('jens', 'pylucid_test@jensdiemer.de'),
)





#CACHE_BACKEND = 'dummy://'


if DEBUG:
    # Display invalid (e.g. misspelled, unused) template variables
    # http://www.djangoproject.com/documentation/templates_python/#how-invalid-variables-are-handled
    # http://www.djangoproject.com/documentation/settings/#template-string-if-invalid
    # But note: Some django admin stuff is broken if TEMPLATE_STRING_IF_INVALID != ""
    # see also: http://code.djangoproject.com/ticket/3579
    # A work-a-round for this lives in ./pylucid_project/apps/pylucid_admin/admin.py 
    TEMPLATE_STRING_IF_INVALID = "XXX INVALID TEMPLATE STRING '%s' XXX"
