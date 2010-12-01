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
$Id: TemplatesProvider.py 227919 2010-12-01 11:43:20Z glenfant $
"""

__author__  = ''
__docformat__ = 'restructuredtext'


# Python imports
from AccessControl import ClassSecurityInfo

# CMF imports
from Products.CMFCore  import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.public import *

# Products imports
from Products.PloneSubscription.config import PROJECTNAME
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.interfaces.ISubscriber import ISubscriber


schema = BaseFolderSchema.copy()

class TemplatesProvider(BaseFolder):
    """Implement subscriber folder for user"""
    
    __implements__ = BaseFolder.__implements__, ISubscriber
    
    portal_type = meta_type = 'TemplatesProvider'
    archetype_name = 'TemplatesProvider'
    immediate_view = 'base_view'
    default_view   = 'base_view'
    global_allow = True
    schema =  schema
    allowed_content_types = ('SubscriptionTemplate',)
    include_default_actions = 0
    security = ClassSecurityInfo()

    actions = (
        {
        'id'            : 'view',
        'name'          : 'View',
        'action'        : 'string:${object_url}/base_view',
        'permissions'   : (SubscriptionPermissions.ManageSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
        {
        'id'            : 'edit',
        'name'          : 'Edit',
        'action'        : 'string:${object_url}/base_edit',
        'permissions'   : (SubscriptionPermissions.ManageSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
    )

registerType(TemplatesProvider, PROJECTNAME)
