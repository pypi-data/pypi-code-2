# Django settings for PyEvo project.

import os
import os.path
import site_logging

PROJECT_DIR = os.path.dirname(__file__)

DEBUG = False

dbName = "evo"
if os.environ.has_key("EVO_DATABASE"):
   dbName = os.environ["EVO_DATABASE"]

# Base backends are 'django.db.backends.*' where '*' is replaced by
# 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
dbBackend = 'django.db.backends.postgresql_psycopg2'
if os.environ.has_key("EVO_SQLITE"):
   dbBackend = 'django.db.backends.sqlite3'
   if dbName != ':memory:':
      dbName = os.path.join(os.environ["EVO_SQLITE"], dbName + ".db")
elif os.environ.has_key("EVO_BACKEND"):
   dbBackend = os.environ["EVO_BACKEND"]

print "using db: ", dbName

DATABASES = {
    'default': {
        'ENGINE': dbBackend, 
        'NAME': dbName,                      # Or path to database file if using sqlite3.
        'USER': 'evo',                      # Not used with sqlite3.
        'PASSWORD': 'evo',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gdh7f5x(&e*t#3#)qv5blw%)qmkc*q0v_(ni)868mira9vqtl-'


INSTALLED_APPS = (
    'pyec.db',
)
