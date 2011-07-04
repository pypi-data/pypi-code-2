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
This module implements mail template document.
"""
__version__ = "$Revision: 60972 $"
# $Source$
# $Id: SubscriptionTemplate.py 227919 2010-12-01 11:43:20Z glenfant $
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


schema = BaseSchema.copy() +  Schema ((
    TextField(
        'mail_body',
        multiValued=False,
        required=True,
        searchable=False,
        default="""
A change related to your subscription to "%(subscription_title)s" was found:

%(content)s
""",
        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
        write_permission=SubscriptionPermissions.ViewSubscriptionContent,
        widget=TextAreaWidget(
            cols=50,
            rows=30,
            label="Body",
            label_msgid="label_subscription_mail_body",
            description="Body template use to generate subscription mail.",
            description_msgid="help_subscription_mail_body",
            i18n_domain="plonesubscription",
            ),
        ),
    ),)

class SubscriptionTemplate(BaseContent):
    """Implement keywords subscription"""
    
    portal_type = meta_type = 'SubscriptionTemplate'
    archetype_name = 'SubscriptionTemplate'
    immediate_view = 'base_edit'
    default_view   = 'base_edit'
    global_allow = False
    schema =  schema
    allowed_content_types = ()
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

registerType(SubscriptionTemplate, PROJECTNAME)
