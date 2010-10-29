# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS
#
# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE
#
# More details in the ``LICENSE`` file included in this package.
"""
$Id: __init__.py 225402 2010-10-27 16:03:38Z glenfant $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

from AccessControl import allow_module
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from config import *
import retrievers

# Configlet validation requires the "codecs" package
allow_module('codecs')

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    """CMF registration"""

    from PloneFilesZipTool import PloneFilesZipTool

    utils.ToolInit(
        PROJECTNAME + ' Tool',
        tools=(PloneFilesZipTool,),
        product_name=PROJECTNAME,
        icon='fileszip_icon.png').initialize(context)
