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
This module implements subscription to a catalog search
"""
__version__ = "$Revision: 20967 $"
# $Source$
# $Id: ExactSearchSubscription.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

# Python imports
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
import urllib

# Zope imports
from DateTime import DateTime

# CMF imports
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.public import *

# Products imports
from Products.PloneSubscription.config import PROJECTNAME, Log, LOG_DEBUG
from Products.PloneSubscription.content.schemata import BaseSubscriptionSchema
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.interfaces.ISubscription import ISubscription
from Products.DataGridField import DataGridField, DataGridWidget

schema = BaseSubscriptionSchema.copy() + Schema ((
    DataGridField(
        'exactSearch',
        required=True,
        searchable=False,
#        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
#        write_permission=SubscriptionPermissions.ViewSubscriptionContent,
        columns=('Index','Value'),
        widget=DataGridWidget(
            label="Exact Search",
            label_msgid="label_subscription_exactsearch",
            description="Exact search in the site.",
            description_msgid="help_subscription_exactsearch",
            i18n_domain="plonesubscription",
            ),
        ),
    ),)

class ExactSearchSubscription(BaseContent):
    """Implement exact search subscription"""
    
    __implements__ = BaseContent.__implements__, ISubscription
    
    portal_type = meta_type = 'ExactSearchSubscription'
    archetype_name = 'ExactSearchSubscription'
    immediate_view = 'base_view'
    default_view = 'base_view'
    content_icon = 'exactsearchsubscription_icon.gif'
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
        return self.getExactSearch()

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getSubscriber')
    def getSubscriber(self):
        """Return the subscriber"""
        return aq_parent(aq_inner(self))

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getQuery')
    def getQuery(self):
        """Return the request used for catalog query"""
        search = {
            'path': self.getRpath(),
            'modified': {
                'query': [self.getLast_send(),],
                'range': 'min'
                },
            }
        for item in self.getExactSearch():
            index = item["Index"]
            value = item["Value"]
            if search.has_key(index):
                # We allow multiple values and combine them in a list
                if type(search[index])==type([]):
                    # We already have a list, so append
                    search[index]=search[index] + [value]
                else:
                    # We create the list from the existing search value and append
                    search[index]=[search[index]] + [value]
            else:
                search[index]=value
        Log(LOG_DEBUG, 'Search query:\n', search)
        return search

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
        portal_url = getToolByName(self, 'portal_url')
        parts = []
        for exact_search in self.getExactSearch():
            parts.append('%s=%s' % (urllib.quote(exact_search['Index']), urllib.quote(exact_search['Value'])))
        return portal_url() + '/search?' + '&'.join(parts)

registerType(ExactSearchSubscription, PROJECTNAME)

