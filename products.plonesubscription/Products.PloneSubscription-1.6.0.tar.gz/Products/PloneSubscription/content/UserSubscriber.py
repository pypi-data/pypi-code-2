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
This module implement a simple user subscriber.
"""
__version__ = "$Revision: 60972 $"
# $Source$
# $Id: UserSubscriber.py 227919 2010-12-01 11:43:20Z glenfant $
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
from Products.PloneSubscription.content.schemata import BaseSubscriberSchema
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.interfaces.ISubscriber import ISubscriber
from Products.Archetypes.ArchetypeTool import listTypes

schema = BaseSubscriberSchema.copy()

class UserSubscriber(BaseFolder):
    """Implement subscriber folder for user"""

    __implements__ = BaseFolder.__implements__, ISubscriber

    listOfTypes = listTypes()

    portal_type = meta_type = 'UserSubscriber'
    archetype_name = 'UserSubscriber'
    immediate_view = 'subscriber_view'
    default_view   = 'subscriber_view'
    content_icon = 'usersubscriber_icon.gif'
    global_allow = False
    schema =  schema
    filter_content_types = True
    allowed_content_types = ('FolderSubscription',
                             'KeywordsSubscription',
                             'ContentSubscription',
                             'ExactSearchSubscription',)
    # XXX use property with Zope 2.8 and ZODB 3.4 only
    #allowed_content_types = property(getSubscriberAllowedContentTypes())
    include_default_actions = 0
    security = ClassSecurityInfo()

    actions = (
        {
        'id'            : 'view',
        'name'          : 'View',
        'action'        : 'string:${object_url}/subscriber_view',
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

    def getUsers(self, subscription_id):
        """Return the users concerned by the subscriber"""
        if hasattr(self, subscription_id):
            return (getattr(self, subscription_id).getOwner(),)
        else:
            from zLOG import LOG, INFO
            LOG("PloneSubscription.UserSubscriber.getUsers /!\\ ", INFO,
                "subscription %s not found" % subscription_id)
            return ()

    security.declarePublic('getSubscriberInfo')
    def getSubscriberInfo(self, additional_fields=()):
        """
        Return 'harmless' info of a subscriber. Fullname and email are required
        information.
        For members of the site, the information is taken from the id of
        the UserSubscriber object, which is expected to have the same id
        as the member.
        you may add fields other than username, fullname and email in aditional_fields
        """
        mtool = getToolByName(self, 'portal_membership')
        memberId = self.getId()
        member = mtool.getMemberById(memberId)
        if member is None:
            return None
        subscriberinfo = { 'type' : 'User',
                           'username' : memberId,
                           'fullname' : member.getProperty('fullname'),
                           'email': member.getProperty('email'),
                         }
        for field_name in additional_fields:
            try:
                subscriberinfo[field_name] = member.getProperty(field_name)
            except ValueError, e:
                # No such property
                subscriberinfo[field_name] = 'Unknown member property'
        return subscriberinfo

registerType(UserSubscriber, PROJECTNAME)
