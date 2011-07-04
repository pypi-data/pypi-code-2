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
# $Id: testPloneSubscription.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

from common import *
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore  import permissions as CMFCorePermissions
from Products.PloneSubscription import SubscriptionPermissions
from Products.PloneSubscription.config import *
from DateTime import DateTime

class TestPloneSubscription(PloneSubscriptionTestCase.PloneSubscriptionTestCase):
    # Subscriptions tool tests

    def testAddPortalSubscriptionTool(self):
        """Test adding of portal_subscription tool"""
        self.failUnless('portal_subscription' in self.portal.objectIds(),
                        "portal_subscription tool was not installed")

    def testAddPortalSubscriptionCatalog(self):
        """Test adding of subscription_catalog"""
        self.failUnless('subscription_catalog' in self.portal.objectIds(),
                        "subscription_catalog was not installed")

    def testAddSubscriptionProvider(self):
        """Adding a subscription provider"""
        id= 'subscription_provider_test'
        self.loginAsPortalOwner()
        self.portal.addSubscriptionProvider(id=id)
        self.failUnless(id in self.portal.objectIds(),
                        "Subscription provider was not installed")
        self.logout()

    def testAddTemplatesProvider(self):
        """Adding a templates provider"""
        id = 'subscription_templates_test'
        self.loginAsPortalOwner()
        self.portal.addTemplatesProvider(id=id)
        self.failUnless(id in self.portal.objectIds(),
                        "Subscription provider was not installed")
        self.logout()

    def testGetProvider(self):
        """Test provider assignment"""
        self.loginAsPortalMember()
        self.failUnless(self.stool.getProvider() == self.sp,
                        "getProvider fails to reach provider")
        self.logout()

    def testAddSubscriptionTemplate(self):
        """Adding a subscription template"""
        self.loginAsPortalOwner()
        self.tp.invokeFactory('SubscriptionTemplate', 'test_template')
        self.failUnless('test_template' in self.tp.objectIds(),
                        "SubscriptionTemplate not created or bad id :\n"+repr(self.tp.objectIds()))
        self.tp.test_template.setMail_body("%(content)s)")
        self.logout()

    def testGetSubscriptionTemplate(self):
        """Test subscription template assignement"""
        self.loginAsPortalMember()
        home_folder = self.portal.portal_membership.getHomeFolder(self.user_name)
        home_folder.invokeFactory('Folder', 'member_folder')
        home_folder.member_folder.addSubscription(id='folder')
        self.logout()
        self.loginAsPortalOwner()
        self.tp.invokeFactory('SubscriptionTemplate', 'test_template')
        self.tp.test_template.setMail_body("%(content)s)")
        self.stool.setFolderTemplate(self.tp.test_template.UID())
        template = self.stool.getSubscriptionTemplate(getattr(self.sp, self.user_name).folder)
        self.failUnless(template == "%(content)s)",
                        "Bad template for this subscription")
        self.logout()

    def testTemplates(self):
        """Test templates"""
        templates = self.stool.getTemplates()
        self.failUnless(templates.meta_type == 'TemplatesProvider', "TemplateProvider not found")
        self.failUnless(templates.objectIds() == ['default_template'], "Contained default template not found")

    def testGetSubscriptionCatalog(self):
        """Test catalog accessor"""
        self.failUnless(self.stool.getCatalog() == getattr(self.portal, 'subscription_catalog'), "catalog unreachable")

    def testGetUserSubscriptions(self):
        """Test get user subscriptions """
        self.loginAsPortalMember()
        home_folder = self.portal.portal_membership.getHomeFolder(self.user_name)
        home_folder.invokeFactory('Folder', 'member_folder')

        home_folder.member_folder.addSubscription()
        kw = {
            'rpath': '/',
            'keywords': 'test_folder',
            }
        self.stool.setSubscription(ptype='KeywordsSubscription', **kw)
        home_folder.member_folder.invokeFactory('Folder', 'test_kw')
        self.logout()
        self.loginAsPortalOwner()
        for id in self.portal.subscription_provider.objectIds():
            print id
        self.failUnless(len(self.stool.getSubscriptions()) == 2,
                        "Fail to get all subscriptions. Found %s instead of 2" % len(self.stool.getSubscriptions()))
        self.logout()

    def testFolderSubscriptionCreation(self):
        """Adding a folder subscription"""
        self.loginAsPortalMember()
        home_folder = self.portal.portal_membership.getHomeFolder(self.user_name)
        home_folder.invokeFactory('Folder', 'member_folder')
        home_folder.member_folder.addSubscription()
        home_folder.member_folder.invokeFactory('Folder', 'test_kw')
        # XXX
        self.logout()

    def testKeywordsSubscriptionCreation(self):
        """Adding a keywords subscription"""
        self.loginAsPortalMember()
        home_folder = self.portal.portal_membership.getHomeFolder(self.user_name)
        home_folder.invokeFactory('Folder', 'member_folder')
        kw = {
            'rpath': '/',
            'keywords': 'test_folder',
            }
        self.stool.setSubscription(ptype='KeywordsSubscription', **kw)
        home_folder.member_folder.invokeFactory('Folder', 'test_kw')
        # XXX
        self.logout()

    def testMemberSubscribptions(self):
        """ test member subscriptions creation """
        pass

    def testSetsubscription(self):
        """SubscriptionTool.setSubscription"""
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'folder001')
        self.portal.folder001.invokeFactory('Document', 'test_folder')
        self.sp.invokeFactory('GroupSubscriber', 'group')
        self.failUnless(self.stool.getSubscriber("group"), "Group subscriber exists")
        # test add in GroupSubscriber
        folder_kw = {
            'rpath': self.portal.folder001.absolute_url_path(),
            'title': 'Folder1',
            }
        subscription=self.stool.setSubscription(id='folder1',
                                                ptype='FolderSubscription',
                                                subscriber_id='group',
                                                **folder_kw)
        self.failUnless(subscription is not None, "Adding a subscription with ptype implementing ISubscription to return subscription object")
        self.logout()
        self.loginAsPortalMember()
        # test add in UserSubscriber
        home_folder = self.portal.portal_membership.getHomeFolder(self.user_name)
        home_folder.invokeFactory('Folder', 'member_folder')
        folder_kw = {
            'rpath': '/'.join(home_folder.member_folder.getPhysicalPath()),
            'title': 'Folder1',
            }
        keywords_kw = {
            'rpath': '/',
            'title': 'my keywords to search',
            }
        self.failUnless(self.stool.setSubscription(id='sub_id1', ptype='Inexsistant', **folder_kw) is None,
                        "Adding a subscription with non-existant ptype have to return None")
        self.failUnless(self.stool.setSubscription(id='sub_id2', ptype='NewsItem', **folder_kw) is None,
                        "Adding a subscription with ptype doesn't implementing ISubscription have to return None")
        self.failUnless(self.stool.setSubscription(id='folder1', ptype='FolderSubscription', **folder_kw) is not None,
                        "Adding a subscription with ptype implementing ISubscription to return subscription object")
        self.failUnless(self.stool.setSubscription(id='keywords1', ptype='KeywordsSubscription', **keywords_kw) is not None,
                        "Adding a subscription with ptype implementing ISubscription to return subscription object")
        self.logout()

    def testGetUpdatedSubscriptions(self):
        """Test updated subscriptions recuperation"""
        self.loginAsPortalMember()
        home_folder = self.portal.portal_membership.getHomeFolder(self.user_name)
        home_folder.invokeFactory('Folder', 'member_folder')
        home_folder.member_folder.addSubscription()
        kw = {
            'rpath': '/',
            'keywords': 'test_folder',
            }
        self.stool.setSubscription(ptype='KeywordsSubscription', **kw)
        self.logout()
        self.loginAsPortalOwner()
        self.failUnless(len(self.stool.getUpdatedSubscriptions(DateTime())) == 2,
                        "Fail to get updated subscriptions")
        home_folder.invokeFactory('Folder', 'test_kw')
        # XXX
        self.logout()


    def testMailing(self):
        """Test mass mailing"""
        self.loginAsPortalMember()
        home_folder = self.portal.portal_membership.getHomeFolder(self.user_name)
        home_folder.invokeFactory('Folder', 'member_folder')
        now = DateTime()
        home_folder.member_folder.addSubscription()
        keyword = 'test_kw'
        kw = {
            'rpath': '/',
            'keywords': keyword,
            }
        self.stool.setSubscription(id='kwsub', ptype='KeywordsSubscription', **kw)
        # searchResults don't return id result: don't forget to set title
        home_folder.member_folder.invokeFactory('Folder', 'test_kw', title=keyword)
        self.logout()
        self.loginAsPortalOwner()
        subscriptions = self.stool.getUpdatedSubscriptions(now)
        self.failUnless(len(subscriptions)==2, "Number of updated subscriptions not correct.")
        old_sendmail = self.stool.sendMail

        # XXX unittests monkey patches
        # unittests are not installing a good user but we know it's a good one.
        def validate_mailing_by_user(now, subscription, user):
            return True
        self.stool.validate_mailing_by_user = validate_mailing_by_user

        # test mail sent when subscriptions are ready to be sent
        def sendMail(messageText, mto=None, mfrom=None, subject=None, encode=None):
            return True
        self.stool.sendMail = sendMail

        now = DateTime()
        self.stool.mailing()
        self.failIf(getattr(self.sp, self.user_name).kwsub.getLast_send() < now,
                    "Subscription not updated")

        # Now all our subscriptions are update, we must wait before update them again
        now = DateTime()
        self.stool.mailing()
        self.failIf(getattr(self.sp, self.user_name).kwsub.getLast_send() > now,
                    "Subscription updated too early")
        self.stool.sendMail = old_sendmail

        # XXX TODO change last_send date and test delay between activation
        self.logout()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneSubscription))
    return suite

if __name__ == '__main__':
    framework()
