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
This module implements subscription to keywords search
"""
__version__ = "$Revision: 18686 $"
# $Source$
# $Id: KeywordsSubscription.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

# Python imports
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent

# Zope imports
from DateTime import DateTime

# CMF imports
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.public import *

# Products imports
from Products.PloneSubscription.config import PROJECTNAME
from Products.PloneSubscription.content.schemata import BaseSubscriptionSchema
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.interfaces.ISubscription import ISubscription

schema = BaseSubscriptionSchema.copy() + Schema ((
    StringField(
        'keywords',
        multiValued=False,
        required=True,
        searchable=False,
        default='',
        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
        write_permission=SubscriptionPermissions.ViewSubscriptionContent,
        widget=StringWidget(
            label="Keywords",
            label_msgid="label_subscription_keywords",
            description="Keywords search in the site.",
            description_msgid="help_subscription_keywords",
            i18n_domain="plonesubscription",
            ),
        ),
    ),)


class KeywordsSubscription(BaseContent):
    """Implement keywords subscription"""
    
    __implements__ = BaseContent.__implements__, ISubscription
    
    portal_type = meta_type = 'KeywordsSubscription'
    archetype_name = 'KeywordsSubscription'
    immediate_view = 'base_view'
    default_view = 'base_view'
    content_icon = 'keywordssubscription_icon.gif'
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
        'permissions'   : (SubscriptionPermissions.ViewSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
        {
        'id'            : 'edit',
        'name'          : 'Edit',
        'action'        : 'string:${object_url}/base_edit',
        'permissions'   : (SubscriptionPermissions.EditSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
    )

    # Interface related methods

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getTitle')
    def getTitle(self):
        """Overload rpath accessor to synchronise reference"""
        return self.getKeywords()

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getSubscriber')
    def getSubscriber(self):
        """Return the subscriber"""
        return aq_parent(aq_inner(self))

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getQuery')
    def getQuery(self):
        """Return the request used for catalog query"""
        return {
            'SearchableText': self.getKeywords(),
            'path': self.getRpath(),
            'modified': {
                'query': [self.getLast_send(),],
                'range': 'min'
                },
            }

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getQueryBrains')
    def getQueryBrains(self):
        """Return the list of brains concerned by the mailing"""
        stool = getToolByName(self, 'portal_subscription')
        return stool.getQueryBrains(self.getQuery())

    def afterQueryFilters(self, brains):
        """Filter query results with subscription options"""
        return brains

    def getSubscriptionUrl(self):
        """Return the url of the object or concept subscribed on"""
        rpath = self.getRpath()
        url = rpath
        if rpath=='/':
            url='/search?SearchableText=' + self.getKeywords()
        else:
            url = rpath + '/search?SearchableText=' + self.getKeywords()
        return url
        
registerType(KeywordsSubscription, PROJECTNAME)
