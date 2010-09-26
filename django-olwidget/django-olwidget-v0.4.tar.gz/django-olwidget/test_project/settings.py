# Django settings for test_project project.

import os
SETTINGS_ROOT = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEST_RUNNER = "django.contrib.gis.tests.run_tests"
POSTGIS_TEMPLATE = "template_postgis"

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'olwidget_dev' # Or path to database file if using sqlite3.
DATABASE_USER = 'django_dev'   # Not used with sqlite3.
DATABASE_PASSWORD = 'django_dev'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SETTINGS_ROOT, "media/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'j2i1*i)uh*-&cdn^+0*i3^cw9gx-^jrc2&yfn!o-xy)$ij154j'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'test_project.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.gis',

    'testolwidget',
    'olwidget'
)

GOOGLE_API_KEY = "ABQIAAAARaukg-vCnyMKCmf7W1mdOhQCULP4XOMyhPd8d_NrQQEO8sT8XBTLlWMmpTlKIHpKhd2GXLaZc6gHJA" # localhost:8000
#GOOGLE_API_KEY = "ABQIAAAARaukg-vCnyMKCmf7W1mdOhTUM1TfCWCpQbByeYgbUi08Ugq4ShQ2qaNvdgbJz36kf2mKYgbUTR6R7A" # 18.85.23.189:8000
YAHOO_APP_ID = "JNrvOMXV34Ft.LUs2zzCI9yVPrIX1KDJ1tiNHFam9mLWl64qgtbSjenTP.ua1UWbPCbp0w6r.A--" # olwidget documentation

