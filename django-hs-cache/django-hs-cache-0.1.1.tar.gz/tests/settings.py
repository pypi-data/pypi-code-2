DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

INSTALLED_APPS = (
    'cache_test',
)

# import sys, os
# 
# print "__name__ =", __name__
# print "__file__ =", __file__
# print "os.getpid() =", os.getpid()
# print "os.getcwd() =", os.getcwd()
# print "os.curdir =", os.curdir
# print "sys.path =", repr(sys.path)
# print "sys.modules.keys() =", repr(sys.modules.keys())
# print "sys.modules.has_key('tests') =", sys.modules.has_key('tests')
# if sys.modules.has_key('tests'):
#   print "sys.modules['tests'].__name__ =", sys.modules['tests'].__name__
#   print "sys.modules['tests'].__file__ =", sys.modules['tests'].__file__
#   print "os.environ['DJANGO_SETTINGS_MODULE'] =", os.environ.get('DJANGO_SETTINGS_MODULE', None)