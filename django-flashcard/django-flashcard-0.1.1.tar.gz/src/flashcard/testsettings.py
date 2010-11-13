# -*- mode: python; coding: utf-8; -*-

"""
Run the test suite without a manage.py file.
"""

# A minimal settings.py
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/shorturls.db'
INSTALLED_APPS = ['flashcard']
ROOT_URLCONF = ['flashcard.urls']
