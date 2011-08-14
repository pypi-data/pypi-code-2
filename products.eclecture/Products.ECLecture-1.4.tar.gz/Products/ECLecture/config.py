# -*- coding: utf-8 -*-
# $Id: config.py 1568 2011-06-28 22:31:28Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.
from Products.CMFCore import permissions
from Products.ATContentTypes.config import zconf

product_globals = globals()

# Project
PROJECTNAME = "ECLecture"
# i18n 
I18N_DOMAIN = 'eduComponents'

# Dependencies of products to be installed by quick-installer
DEPENDENCIES = ['DataGridField']

# Dependend products - not quick-installed
PRODUCT_DEPENDENCIES = []

# supported mime types for textfields
#EC_MIME_TYPES = ('text/plain', 'text/structured', 'text/x-rst', 'text/x-web-intelligent', 'text/html', )
ALLOWED_CONTENT_TYPES = zconf.ATDocument.allowed_content_types

# default mime type for textfields
#EC_DEFAULT_MIME_TYPE = 'text/plain'
DEFAULT_CONTENT_TYPE = zconf.ATDocument.default_content_type

# default output format of textfields
DEFAULT_OUTPUT_TYPE = 'text/x-html-safe'
#DEFAULT_OUTPUT_TYPE = zconf.ATDocument.default_content_type

ALLOW_DOCUMENT_UPLOAD = zconf.ATDocument.allow_document_upload


# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
ADD_CONTENT_PERMISSIONS = {'ECLecture': 'ECLecture: Add ECLecture', }
permissions.setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
permissions.setDefaultRoles('ECLecture: Add ECLecture', ('Manager','Owner'))
