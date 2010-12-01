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
This module implements unit test for PloneSubscription
"""
__version__ = "$Revision: 60972 $"
# $Source$
# $Id: testGroupSubscriber.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

from common import *
from Products.PloneSubscription.tests.ISubscriberTestCase import ISubscriberTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore  import permissions as CMFCorePermissions
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.config import *
from DateTime import DateTime

class TestGroupSubscriber(ISubscriberTestCase, PloneSubscriptionTestCase.PloneSubscriptionTestCase):

    def afterSetUp(self):
        PloneSubscriptionTestCase.PloneSubscriptionTestCase.afterSetUp(self)
        self.loginAsPortalOwner()
        self.security_context_setup()

        self.user1 = self.portal.acl_users.getUser('u1')
        self.user2 = self.portal.acl_users.getUser('u2')

        self.service_tool = getToolByName(self.portal, 'portal_subscription')
        self.service_provider = self.service_tool.getProvider()
        self.service_provider.invokeFactory('GroupSubscriber', 'group_test')
        self.subscriber = getattr(self.service_provider, 'group_test')
        self.logout()

    def test_setGroup_names(self):
        """ Test if security behavior is correct"""
        # Only u1 user is subscribed
        self.loginAsPortalOwner()
        self.subscriber.setGroup_names(('g1',))
        self.logout()
        u1_roles = self.user1.getRolesInContext(self.subscriber)
        self.failUnlessEqual('SubscriptionViewer' in u1_roles, True,
                             "Subscribed user doesn't have SubscriptionViewer role.")
        u2_roles = self.user2.getRolesInContext(self.subscriber)
        self.failIfEqual('SubscriptionViewer' in u2_roles, True,
                         "Unsubscribed user have SubscriptionViewer role.")
        # Both users are subscribed
        self.loginAsPortalOwner()
        self.subscriber.setGroup_names(('g1', 'g2'))
        self.logout()
        u1_roles = self.user1.getRolesInContext(self.subscriber)
        self.failUnlessEqual('SubscriptionViewer' in u1_roles, True,
                             "Subscribed user haven't SubscriptionViewer role.")
        u2_roles = self.user2.getRolesInContext(self.subscriber)
        self.failUnlessEqual('SubscriptionViewer' in u2_roles, True,
                             "Subscribed user haven't SubscriptionViewer role.")

    def test_getUsers(self):
        """Return users concerned by the subscriber"""
        self.loginAsPortalOwner()
        self.subscriber.setGroup_names(('g1', 'g2'))
        sub_id = 'f_sub'
        self.subscriber.invokeFactory('FolderSubscription', sub_id)
        self.logout()
        users = [user.getId() for user in self.subscriber.getUsers(sub_id)]
        users.sort()
        self.failIfEqual(len(users) > 2, True, "Too many users")
        self.failIfEqual(len(users) < 2, True, "Some users are missing")
        self.failUnlessEqual(users, ['u1', 'u2'], "Not the good users")

    def test_getGroupVocabulary(self):
        """Test group vocabulry display list construction"""
        group_vocab = self.subscriber.getGroupsVocabulary()
        self.failUnlessEqual(group_vocab.items(), (('g1', 'g1'), ('g2', 'g2')),
                             "Something wrong in group vocabulary")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGroupSubscriber))
    return suite

if __name__ == '__main__':
    framework()
