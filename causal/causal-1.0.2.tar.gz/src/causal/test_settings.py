"""
"""
from settings import *

# REMEMBER: if you do use sqlite3 below, you'll need
# to re-run ./configure in causal after ./deploy.sh like so:
# ./configure -m pysqlite
# to add in the pysqlite2 module dependency, and then re-run buildout too
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/home/wes/projects/causal/testing.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
