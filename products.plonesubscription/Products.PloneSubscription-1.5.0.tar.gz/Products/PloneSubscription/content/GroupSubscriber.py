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
This modules implements a group subscriber.

It depends on GRUF groups implementation
"""
__version__ = "$Revision: 60972 $"
# $Source$
# $Id: GroupSubscriber.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

# Zope imports
from AccessControl import ClassSecurityInfo
from zLOG import LOG, INFO

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

schema = BaseSubscriberSchema + Schema((
    StringField(
        'group_names',
        required=True,
        searchable=False,
        default=[],
        multiValued=True,
        vocabulary='getGroupsVocabulary',
        enforceVocabulary=True,
        read_permission=SubscriptionPermissions.ViewSubscriptionContent,
        write_permission=SubscriptionPermissions.ViewSubscriptionContent,
        widget=MultiSelectionWidget(
            visible={ 'view': 'visible', 'edit': 'visible',},
            label="Group name",
            label_msgid="label_subscriber_group_names",
            description="Groups that members are subscribed to subscriptions",
            description_msgid="help_subscriber_group_names",
            i18n_domain="plonesubscription",
            ),
        ),
    ),)

class GroupSubscriber(BaseFolder):
    """Implement subscriber folder for user"""

    __implements__ = BaseFolder.__implements__, ISubscriber

    portal_type = meta_type = 'GroupSubscriber'
    archetype_name = 'GroupSubscriber'
    immediate_view = 'subscriber_view'
    default_view   = 'subscriber_view'
    content_icon = 'groupsubscriber_icon.gif'
    global_allow = False
    schema = schema
    allowed_content_types = ('FolderSubscription',)
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
        'permissions'   : (SubscriptionPermissions.EditSubscriptionContent, ),
        'category'      : 'object',
        'visible'       : 1,
        },
    )

    # archetypes overloaded methods

    def setGroup_names(self, value, **kwargs):
        """ Set field data and security

        value is multi valued
        Take care to reindex security for all sub-objects
        """
        field = self.getField('group_names')
        old_value = field.get(self)
        field.set(self, value, **kwargs)
        member_tool = getToolByName(self, 'portal_membership')
        member_tool.deleteLocalRoles(obj=self, member_ids=old_value)
        member_tool.setLocalRoles(obj=self, member_ids=value,
                                  member_role=SubscriptionPermissions.ViewSubscriptionRole)
        self.reindexObjectSecurity()
        for object in self.objectValues():
            object.reindexObjectSecurity()

    security.declareProtected(SubscriptionPermissions.ManageSubscriptionContent, 'getGroupsVocabulary')
    def getGroupsVocabulary(self):
        """Return a vocabulary with couple (id, name) for groups"""
        groups_tool = getToolByName(self, 'portal_groups')
        ids = groups_tool.listGroupIds()
        try:
            names = groups_tool.listGroupNames()
        except:
            names = ids # GroupUserFolder 2.0.1
        group_list = []
        for i in range(len(names)):
            group_list.append((names[i], ids[i], names[i]))
        # sort groups by names
        group_list.sort()

        return Vocabulary(DisplayList([(el[1], el[2]) for el in group_list]), self, 'plone')

    security.declareProtected(SubscriptionPermissions.ManageSubscriptionContent, 'getUsers')
    def getUsers(self, subscription_id):
        if not hasattr(self, subscription_id):
            return ()
        groups_tool = getToolByName(self, 'portal_groups')
        acl_users = getToolByName(self, 'acl_users')
        members = []
        for group_name in self.getGroup_names():
            group = groups_tool.getGroupById(group_name)
            if group is None:
                LOG("PloneSubscription.GroupSubscriber.getUsers /!\\ ", INFO,
                    "group %s not found" % group_name)
            else:
                for member in group.getGroupMembers():
                    user = acl_users.getUser(member.getId())
                    if user not in members:
                        members.append(user)
        return tuple(members)

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
        subscriberinfo = { 'type' : 'Group',
                           'username' : '',
                           'fullname' : '',
                           'email': '',
                         }
        for field_name in additional_fields:
            subscriberinfo[field_name] = ''
        return subscriberinfo

registerType(GroupSubscriber, PROJECTNAME)
