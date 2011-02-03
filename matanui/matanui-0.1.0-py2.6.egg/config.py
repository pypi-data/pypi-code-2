# -*- coding: utf-8 -*-
'''
Configuration of MataNui server.

TODO: Should this be replaced by ConfigObj?
'''

## Created: 2010-09-11 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

# Configuration for using GridFS on MongoDB.
STORAGE_BACKEND = 'matanui.mongogridfs.MongoGridFS'

# Configuration parameters for GridFS on MongoDB.
GRIDFS_HOST = 'localhost' # MongoDB default
GRIDFS_PORT = 27017       # MongoDB default
GRIDFS_DB_NAME = 'test'
GRIDFS_BUCKET = 'fs'
GRIDFS_USER = None
GRIDFS_PASSWORD = None

# User permission settings (UN*X style permissions as octal integer).
# (Should only allow R and W, and ignore X privilege.)
UMASK = 0111
DEFAULT_PERMISSIONS = 0644

# Be verbose with server information on the "info" request.
VERBOSE_INFO = True
