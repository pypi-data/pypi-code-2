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
# $Id: testUserSubscriber.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

from common import *
from Products.PloneSubscription.tests.ISubscriberTestCase import ISubscriberTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore  import permissions as CMFCorePermissions
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.config import *
from DateTime import DateTime

class TestUserSubscriber(ISubscriberTestCase, PloneSubscriptionTestCase.PloneSubscriptionTestCase):

    def afterSetUp(self):
        PloneSubscriptionTestCase.PloneSubscriptionTestCase.afterSetUp(self)
        self.loginAsPortalMember()
        self.security_context_setup()

        self.service_tool = getToolByName(self.portal, 'portal_subscription')
        self.service_provider = self.service_tool.getProvider()
        self.service_provider.invokeFactory('UserSubscriber', self.user_name)
        self.subscriber = getattr(self.service_provider, self.user_name)
        self.logout()

    def test_getUsers(self):
        """Return users concerned by the subscriber"""
        self.loginAsPortalMember()
        sub_id = 'f_sub'
        self.subscriber.invokeFactory('FolderSubscription', sub_id)
        self.logout()
        users = [user.getId() for user in self.subscriber.getUsers(sub_id)]
        users.sort()
        self.failIfEqual(len(users) > 1, True, "Too many users")
        self.failIfEqual(len(users) < 1, True, "Some users are missing")
        self.failUnlessEqual(users, [self.user_name], "Not the good user")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserSubscriber))
    return suite

if __name__ == '__main__':
    framework()

