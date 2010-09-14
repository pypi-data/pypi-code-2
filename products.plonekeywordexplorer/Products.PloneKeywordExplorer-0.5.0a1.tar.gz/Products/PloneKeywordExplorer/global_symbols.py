# -*- coding: utf-8 -*-
## PloneKeywordExplorer
## Alternative search facility using keywords
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Plone Keyword Explorer"""

## The following lines are only useful with the Log.py module
## (which is out of scope from this product)

PROJECTNAME = "PloneKeywordExplorer"
SKIN_NAME = "PloneKeywordExplorer"
ICON = 'keyword_explorer_icon.gif'

from Products.CMFPlone.utils import getFSVersionTuple
PLONE_VERSION = getFSVersionTuple()
del getFSVersionTuple

LAYERS_PATH = None
def findLayersPath():
    # Choose a layer depending on Plone version
    global LAYERS_PATH
    main_version = PLONE_VERSION[:2]
    version_to_layer = {
        # Plone version : layer
        (2, 0): 'skins',
        (2, 1): 'skins',
        (2, 5): 'skins',
        (3, 0): 'plone3skins'
        }
    LAYERS_PATH = version_to_layer.get(main_version, 'plone3skins')
findLayersPath()
del findLayersPath
SKIN_PATH = LAYERS_PATH + '/' + SKIN_NAME

import os
try:
    # Check if we have to be in debug mode
    if os.path.isfile(os.path.abspath(os.path.dirname(__file__)) + '/debug.txt'):
        DEBUG_MODE = 1
    else:
        DEBUG_MODE = 0


    # Set log options correctly
    import Log
    if DEBUG_MODE:
        Log.LOG_LEVEL = Log.LOG_DEBUG
    else:
        Log.LOG_LEVEL = Log.LOG_NOTICE

    from Log import *
    Log = Log
    Log(LOG_NOTICE, "Starting %s at %d debug level" % (os.path.dirname(__file__), LOG_LEVEL, ))

except:
    LOG_DEBUG = None
    LOG_NOTICE = None
    LOG_WARNING = None
    LOG_ERROR = None
    LOG_CRITICAL = None
    def Log(*args, **kw):
        pass

del os
