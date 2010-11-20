import os
# Django settings for eyeswebapp project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
WEBAPP_ROOT = os.path.dirname(__file__)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

CACHE_BACKEND = "locmem:///?timeout=30&max_entries=400"

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'eyeswebapp'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/PST8PDT'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(WEBAPP_ROOT,"static_media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=ta)^k2cq$u*^5sk=)#rl4t9dd4w$dnp$aub^qh_auu71q%o^v'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth", # needed for /admin app
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "eyeswebapp.context_processors.common",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

CACHE_MIDDLEWARE_SECONDS = 60

ROOT_URLCONF = 'eyeswebapp.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(WEBAPP_ROOT,"templates")
)

INSTALLED_APPS = (
    'south',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'core',
    'util',
    'api',
    'django.contrib.markup', # to enable markup in templates
    #'django_extensions', # for extra commands in manage.py help
)

DEFAULT_FROM_EMAIL = 'alert@yourhost.com'
DEFAULT_CHARSET = "utf-8"
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_SUBJECT_PREFIX = "[EYES ALERT] "
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None

# base directory for storing RRD files supporting Eyes.
# directory *must* be writable to the web application
RRDFILE_ROOT = os.path.join(WEBAPP_ROOT,'tmp_rrd')
PNGFILE_ROOT = os.path.join(WEBAPP_ROOT,'tmp_png')

if not(os.path.exists(RRDFILE_ROOT)): # pragma: no cover
    os.mkdir(RRDFILE_ROOT)
if not(os.path.exists(PNGFILE_ROOT)): # pragma: no cover
    os.mkdir(PNGFILE_ROOT)

# requires installation of unittest-xml-reporting (pip install unittest-xml-reporting)
# to run the tests using this extra component - generates test output in JUnit XML format
# for parsing by continuous integration systems
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.run_tests'
#TEST_RUNNER = 'django_nose.run_tests'
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_VERBOSE = True
TEST_OUTPUT_DIR = 'testresults'
