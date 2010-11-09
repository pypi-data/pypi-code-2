# -*- coding: utf-8 -*-
## Copyright (C) 2006 - 2007 Ingeniweb

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
"""
Global FileSystemStorage configuration data
$Id: config.py 69081 2008-07-28 13:39:24Z b_mathieu $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

PROJECTNAME = 'iw.fss'
GLOBALS = globals()
I18N_DOMAIN = PROJECTNAME.lower()
PROPERTYSHEET = 'filesystemstorage_properties'

ZCONFIG, dummy_handler, CONFIG_FILE = None, None, None

def loadConfig():
    """Loads configuration from a ZConfig file"""
    from customconfig import ZOPETESTCASE

    global ZCONFIG, dummy_handler, CONFIG_FILE

    import os
    from Globals import INSTANCE_HOME
    from ZConfig.loader import ConfigLoader
    from iw.fss.configuration.schema import fssSchema

    # Configuration directories
    INSTANCE_ETC = os.path.join(INSTANCE_HOME, 'etc')
    _this_directory = os.path.abspath(os.path.dirname(__file__))
    FSS_ETC = os.path.join(_this_directory, 'etc')

    def filePathOrNone(file_path):
        return os.path.isfile(file_path) and file_path or None

    # (Potential) configuration files
    CONFIG_FILENAME = 'plone-filesystemstorage.conf'
    INSTANCE_CONFIG = filePathOrNone(os.path.join(INSTANCE_ETC, CONFIG_FILENAME))
    FSS_CONFIG = filePathOrNone(os.path.join(FSS_ETC, CONFIG_FILENAME))
    FSS_CONFIG_IN = filePathOrNone(os.path.join(FSS_ETC, CONFIG_FILENAME + '.in'))

    # We configure on the first available config file
    CONFIG_FILE = [fp for fp in (INSTANCE_CONFIG, FSS_CONFIG, FSS_CONFIG_IN)
                   if fp is not None][0]

    # We ignore personal configuration on unit tests
    if ZOPETESTCASE:
        ZCONFIG, dummy_handler = ConfigLoader(fssSchema).loadURL(FSS_CONFIG_IN)
    else:
        ZCONFIG, dummy_handler = ConfigLoader(fssSchema).loadURL(CONFIG_FILE)


    # Dirty but we need to reinit datatypes control globals since this
    # initialisation seems to be called more than once with Zope 2.8
    # (why ???)
    #from iw.fss.configuration import datatypes
    #datatypes._paths = []
    #return

loadConfig()
