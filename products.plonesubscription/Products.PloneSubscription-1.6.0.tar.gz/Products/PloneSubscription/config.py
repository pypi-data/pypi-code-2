# -*- coding: utf-8 -*-
## PloneSubscription
## A Plone tool supporting different levels of subscription and notification
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
"""
Base configuration data
"""
__version__ = "$Revision: 61095 $"
# $Source$
# $Id: config.py 241647 2011-06-29 16:54:05Z yboussard $
__docformat__ = 'restructuredtext'

# CMF imports
from Products.CMFCore import permissions as CMFCorePermissions
from App.config import getConfiguration

GLOBALS = globals()
PROJECTNAME = 'PloneSubscription'
SKINS_DIR = 'skins'
TOOL_ICON = 'subscription_icon.gif'
TOOL_META_TYPE = 'SubscriptionTool'
CATALOG_INDEXES = (
    # (index_id, index_type, is_metadata, attribute)
    ('id', 'FieldIndex', True, None),
    ('Title', 'FieldIndex', True, None),
    ('Description', 'TextIndex', False, None),
    ('path', 'PathIndex', True, None),
    ('allowedRolesAndUsers', 'KeywordIndex', False, None),
    ('getRpath', 'ExtendedPathIndex', True, "getRpath"),
    ('getLast_send', 'DateIndex', False, None),
    )
subscription_task_id = 'subscription_task'
subscription_script_id = 'subscriptionMailing'

# Dependencies
_base_zope_DEPS = (
    )
_base_plone_DEPS = (
    )

# Add your own dependencies here
_my_zope_DEPS = (
    )
_my_plone_DEPS = (
    'PloneMaintenance',
    'DataGridField',
    )

zope_DEPS= _base_zope_DEPS + _my_zope_DEPS
plone_DEPS = _base_plone_DEPS + _my_plone_DEPS

# Configlets
subscription_prefs_configlet = {
    'id': 'subscriptions_prefs',
    'appId': PROJECTNAME,
    'name': 'configlet_subscription_preferences',
    'action': 'string:$portal_url/portal_subscription/base_view',
    'category': 'Products',
    'permission': (CMFCorePermissions.ManagePortal,),
    'imageUrl': TOOL_ICON,
    }


# Check if we have to be in debug mode
import Log, os
if os.path.isfile(os.path.abspath(os.path.dirname(__file__)) + '/debug.txt'):
    Log.LOG_LEVEL = Log.LOG_DEBUG
else:
    Log.LOG_LEVEL = Log.LOG_NOTICE

from Log import *
Log = Log
Log(LOG_NOTICE, "Starting %s at %d debug level" % (os.path.dirname(__file__), LOG_LEVEL, ))
TRACE_SEND_MAIL = getConfiguration().product_config.get('plonesubscription',{}).get('debug_send_mail', False)
Log(LOG_NOTICE, "Trace send mail %s" %  (TRACE_SEND_MAIL and 'ON' or 'OFF'))
