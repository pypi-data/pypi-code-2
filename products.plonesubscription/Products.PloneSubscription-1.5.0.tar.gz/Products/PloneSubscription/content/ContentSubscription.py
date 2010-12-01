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
This module implement a content subscription with workflow options
"""
__version__ = "$Revision: 60972 $"
# $Source$
# $Id: ContentSubscription.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'


# Python imports
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent

# Zope imports
from DateTime import DateTime

# CMF imports
from Products.CMFCore  import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.public import *
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *

# Products imports
from Products.PloneSubscription.config import PROJECTNAME
from Products.PloneSubscription.content.schemata import BaseSubscriptionSchema
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.interfaces.ISubscription import ISubscription

schema = BaseSubscriptionSchema.copy() + Schema ((
    ReferenceField(
        'content',
        multiValued=False,
        required=True,
        searchable=False,
        relationship='subscriptionContentOf',
        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
        write_permission=SubscriptionPermissions.EditSubscriptionContent,
        widget=ReferenceBrowserWidget(
            addable=True,
            visible={ 'view': 'hidden', 'edit': 'visible',},
            label="Content subscribed",
            label_msgid="label_subscription_content",
            description="The document on which the subscription is done.",
            description_msgid="help_subscription_content",
            i18n_domain="plonesubscription",
            default_search_index='Title',
            available_indexes={'Title': 'title',}
            ),
        ),
    BooleanField(
        'workflow',
        multiValued=False,
        required=False,
        searchable=False,
        default=False,
        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
        write_permission=SubscriptionPermissions.EditSubscriptionContent,
        widget=BooleanWidget(
            addable=True,
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Workflow transition",
            label_msgid="label_subscription_workflow",
            description="Only return documents which passed a workflow transition",
            description_msgid="help_subscription_workflow",
            i18n_domain="plonesubscription",
            ),
        ),
    ),)

class ContentSubscription(BaseContent):
    """Implement content subscription"""

    __implements__ = BaseContent.__implements__, ISubscription

    portal_type = meta_type = 'ContentSubscription'
    archetype_name = 'ContentSubscription'
    immediate_view = 'base_view'
    default_view   = 'base_view'
    content_icon = 'contentsubscription_icon.gif'
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
        'permissions'   : (SubscriptionPermissions.ViewSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
    )

    # Fields related methods

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getRpath')
    def getRpath(self):
        """Overload rpath accessor to synchronise reference"""
        content = self.getContent()
        if content is None:
            return self.getField('rpath').get(self)
        else:
            return '/'.join(content.getPhysicalPath())

    security.declareProtected(SubscriptionPermissions.EditSubscriptionContent, 'setRpath')
    def setRpath(self, rpath='/'):
        """Overload rpath mutator"""
        content = self.getField('content').get(self)
        if content is None:
            self.getField('rpath').set(self, rpath)
        else:
            self.getField('rpath').set(self, '/'.join(content.getPhysicalPath()))

    # Interface related methods

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getSubscriber')
    def getSubscriber(self):
        """Return the subscriber"""
        return aq_parent(aq_inner(self))

    security.declareProtected(SubscriptionPermissions.ViewSubscriptionContent, 'getQuery')
    def getQuery(self):
        """Return the request used for catalog query"""
        path_arg = None
        # customizing request for limited path search
        path_arg = {
                    'query': self.getRpath(),
                    'depth': 0,
                    }

        return {
            'path': path_arg,
            'ModificationDate': {
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
        if hasattr(self, 'getWorkflow') and self.getWorkflow():
            stool = getToolByName(self, 'portal_subscription')
            brains= stool.afterQueryWorkflowFilter(brains, self.getLast_send())
        return brains

    def getSubscriptionUrl(self):
        """Return the url of the object or concept subscribed on"""
        return self.getRpath()

registerType(ContentSubscription, PROJECTNAME)

