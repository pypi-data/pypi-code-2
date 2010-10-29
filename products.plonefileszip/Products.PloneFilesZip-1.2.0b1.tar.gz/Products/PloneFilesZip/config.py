# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS

# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

# More details in the ``LICENSE`` file included in this package.

"""
Instance wide configuration data for this package
$Id: config.py 225402 2010-10-27 16:03:38Z glenfant $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

GLOBALS = globals()
PROJECTNAME = "PloneFilesZip"
SKINS_DIR = 'skins'
TOOL_ID = 'portal_fileszip'

# Support for other products
HAS_PLONE_FILES_ZIP = True

# Size of each block in the response stream
# just to have a good balance speed/memory
RESPONSE_BLOCK_SIZE = 32768

try:
    # From CMF 1.5
    from Products.CMFCore import permissions as cmf_permissions
except ImportError, e:
    # Up to CMF 1.4
    from Products.CMFCore import CMFCorePermissions as cmf_permissions

# Configlet
CONFIGLET_DEFINITION = {
    'id': 'plonefileszip_prefs',
    'appId': PROJECTNAME,
    'name': 'PloneFilesZip Settings',
    'action': 'string:$portal_url/prefs_files_zip_form',
    'category': 'Products',
    'permission': (cmf_permissions.ManagePortal,),
    'imageUrl': 'files_zip_icon.png',
    }
del cmf_permissions

DEFAULT_ZIP_STRUCTURE_POLICY = 'deep_inner_zip_structure'
