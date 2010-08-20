# -*- coding: utf-8 -*-
# $Id: testAliasCreation.py 123908 2010-08-20 10:27:22Z glenfant $

import os, sys, logging
import zope.event
from zope.publisher.browser import TestRequest
from DateTime import DateTime
from Products.Archetypes.utils import shasattr
from Products.Archetypes.event import ObjectInitializedEvent, ObjectEditedEvent
from Products.SimpleAlias.interfaces import IAliasLinkedTo
from Products.SimpleAlias.tests import SimpleAliasTC

# A test class defines a set of tests
class TestAliasCreation(SimpleAliasTC.SimpleAliasTestCase):

    # The afterSetUp method can be used to define test class variables
    # and perform initialisation before tests are run. The beforeTearDown()
    # method can also be used to clean up anything set up in afterSetUp(),
    # though it is less commonly used since test always run in a sandbox
    # that is cleared after the test is run.
    def afterSetUp(self):
        from Products.CMFPlone.log import logger
        logger.root.setLevel(logging.INFO)
        logger.root.addHandler(logging.StreamHandler(sys.stdout))
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 1
        self.addMember('fred', 'Fred Flintstone', 'fred@bedrock.com', ['Member', 'Manager'], '2002-01-01')
        self.login('fred')
        self.portal.invokeFactory('Folder', 'f1')
        self.f1 = self.portal.f1


    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})

    def testAddAlias(self):
        self.f1.invokeFactory('Alias', 'alias')
        self.failUnless(shasattr(self.f1, 'alias'))

    def testAliasEdit(self):
        self.f1.invokeFactory('Alias', 'alias')
        self.f1.invokeFactory('Document', 'doc') # used for the target
        doc   = self.f1.doc
        alias = self.f1.alias

        doc.setTitle('target doc')
        doc.setDescription('target description')
        alias.setShowTarget(False)
        alias.setShowHint(False)

        self.failUnlessEqual(alias.getShowTarget(), False)
        self.failUnlessEqual(alias.getShowHint(), False)

        # first with autoTitle=True
        alias.setTitle('some title')
        alias.setDescription('some description')
        alias.setAutoTitle(True)

        # without an alias it should show this:
        self.failUnlessEqual(alias.getAutoTitle(), True)
        self.failUnlessEqual(alias.Title(), 'Alias not set')
        self.failUnlessEqual(alias.Description(), 'Object is removed or deleted.')

        # now set an alias
        alias.setAlias(doc)
        self.failUnlessEqual(alias.Title(), 'target doc')
        self.failUnlessEqual(alias.Description(), 'target description')

        # now set autoTitle = False
        alias.setAutoTitle(False)
        alias.setTitle('some title')
        alias.setDescription('some description')
        self.failUnlessEqual(alias.getAutoTitle(), False)
        self.failUnlessEqual(alias.Title(), 'some title')
        self.failUnlessEqual(alias.Description(), 'some description')
        
        # now we update the doc title/desc and
        # confirm the alias title/desc is reindexed
        alias.reindexObject() # ensure the objects are indexed (which would be the case TTW)
        doc.reindexObject()
        # firstly lets confirm this doesn't work
        # when autoTitle is turned off
        alias.setAutoTitle(False)
        # Simulate first edit
        alias._at_creation_flag = True
        alias.processForm(REQUEST=TestRequest())
        # and subsequent edits
        alias.processForm(REQUEST=TestRequest())
        # Now lets edit the doc
        req=TestRequest()
        req.form['title'] = 'target doc 2'
        req.form['description'] = 'target description 2'
        doc._at_creation_flag = False # ensure it doesn't think this is first edit
        doc.processForm(REQUEST=req)
        result = self.portal.portal_catalog(path='/plone/f1/alias')
        self.failUnlessEqual('some title', result[0].Title)
        self.failUnlessEqual('some description', result[0].Description)
        # now lets confirm it works
        # when we turn autoTitle on
        alias.setAutoTitle(True)
        alias.processForm(REQUEST=TestRequest())
        doc.processForm(REQUEST=req)
        result = self.portal.portal_catalog(path='/plone/f1/alias')
        self.failUnlessEqual('target doc 2', result[0].Title)
        self.failUnlessEqual('target description 2', result[0].Description)
        
        # Lets now remove a reference and confirm
        # the marker interface is removed from the doc
        alias.setAlias(None)
        alias.processForm(REQUEST=TestRequest())
        self.failUnless(IAliasLinkedTo.providedBy(doc) == False)
        
        # And lets ensure the marker interfaces are removed
        # when we delete the alias
        alias.setAlias(doc)
        alias.processForm(REQUEST=TestRequest())
        self.failUnless(IAliasLinkedTo.providedBy(doc))
        self.f1.manage_delObjects(['alias'])
        self.failUnless(IAliasLinkedTo.providedBy(doc) == False)

    def testGetIcon(self):
        self.f1.invokeFactory('Alias', 'alias')
        self.f1.invokeFactory('Document', 'doc') # used for the target
        doc   = self.f1.doc
        alias = self.f1.alias
        alias.setAlias(doc)

        self.failUnlessEqual(alias.getIcon(), 'document_icon_alias.gif')

    def testTargetObjectLayout(self):
        self.f1.invokeFactory('Alias', 'alias')
        self.f1.invokeFactory('Document', 'doc') # used for the target
        doc   = self.f1.doc
        alias = self.f1.alias
        alias.setAlias(doc)
        macro = alias.targetMainMacro()
        sourcefile = dict(macro)['setSourceFile']
        self.failUnlessEqual(os.path.basename(sourcefile), 'document_view.pt')

# This boilerplate method sets up the test suite
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # Add our test class here - you can add more test classes if you wish,
    # and they will be run together.
    suite.addTest(makeSuite(TestAliasCreation))
    return suite
