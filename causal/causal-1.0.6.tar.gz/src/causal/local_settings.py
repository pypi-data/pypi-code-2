"""
"""
#from os import umask

# Enabling DEBUG will also enable TEMPLATE_DEBUG
DEBUG = True
# Enabling these admin features will automatically enable
# the corresponding apps
ENABLE_ADMIN = True
ENABLE_ADMIN_DOCS = True
SERVE_STATIC = True
USE_GOOGLE_CDN = False

# REMEMBER: if you do use sqlite3 below, you'll need
# to re-run ./configure in causal after ./deploy.sh like so:
# ./configure -m pysqlite
# to add in the pysqlite2 module dependency, and then re-run buildout too
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'causal_refactor',                      # Or path to database file if using sqlite3.
        'USER': 'wes',                      # Not used with sqlite3.
        'PASSWORD': 'jkirby',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
}

# By default if you enable caching, it will use memcached on 127.0.0.1:11211
ENABLE_CACHING = False

ENABLE_REGISTRATION = True

# Same rules apply as in django's INSTALLED_APPS
# adding any here will also add them to INSTALLED_APPS
INSTALLED_SERVICES = (
    'causal.twitter',
    'causal.facebook',
    'causal.foursquare',
    'causal.github',
    'causal.flickr',
    'causal.googlereader',
    'causal.lastfm',
    'causal.delicious',
)
SERVICE_CONFIG = {
    'causal.twitter': {
        'auth': {
            'consumer_key': '22UK2mEKmmYVE0CEgHnbQ',
            'consumer_secret': 'G3xCbGc1sEL1i54mMyoOx0gmxGln7toAs0yCQOO2XI'
        }
    },
    'causal.facebook': {
        'auth': {
            'consumer_key': '145205425503901',
            'consumer_secret': '4a0cb2d5ab65fe60a92b37f46f2c8b57'
        }
    },
    'causal.foursquare': {
        'auth': {
            'consumer_key': 'BFHOR1PJBMR1ECSIGIJNJJXTACZBNBIOWA0C5UVZ4OM35WBM',
            'consumer_secret': 'GA2WA2KP1FUS50N04TCQXLZPEB2UXTVSWUPNQXLG1STM2ANT'
        }
    },
    'causal.flickr': {
        'auth': {
            'api_key': '5a9f072044abc0026e5225f36e600969'
        }
    },
    'causal.lastfm': {
        'auth': {
            'api_key': '9e98ca7d1c9e63dc551e9dc0061419ae'
        }
    }
}

# *Don't* use the below example, generate your own random string of chars
SECRET_KEY = '''}F!\;*pd~+CB~udvAth_h+N`wao'LNlez~`z$[p#n!!H}tSs%C%l0'@=l+gQnod'''

# Logging
#import logging
#from logging.handlers import RotatingFileHandler
#LOG_FILENAME = '/home/wes/projects/causal/logs/causal.log'
#LOG_SIZE = 8388608 # 8 Mb
#LOG_BACKUP_COUNT = 5 # Keep the main .log file, plus .log.[1-5]
#GLOBAL_LOG_LEVEL = logging.ERROR
#oumask = umask(002)
#handler = RotatingFileHandler(LOG_FILENAME, maxBytes=LOG_SIZE, backupCount=LOG_BACKUP_COUNT)
#GLOBAL_LOG_HANDLERS = [
#    {
#        'handler': handler,
#        'level': GLOBAL_LOG_LEVEL,
#        'format': "%(asctime)s %(source)s: %(message)s"
#        },
#]
#umask(oumask)

# Make sure we use secure=true on session cookies to we don't hemorage
# user session data over vanilla HTTP
# 09/01/2011 - Wes - turning this off while twitter et al are tards
SESSION_COOKIE_SECURE = False

DEFAULT_FROM_EMAIL = 'donotreply@localhost'
