# -*- coding: utf-8 -*-
# $Id: testAliasTool.py 123908 2010-08-20 10:27:22Z glenfant $


from Products.SimpleAlias.tests import SimpleAliasTC
from DateTime import DateTime
from Testing.ZopeTestCase import transaction

# A test class defines a set of tests
class TestAliasCreation(SimpleAliasTC.SimpleAliasTestCase):

    # The afterSetUp method can be used to define test class variables
    # and perform initialisation before tests are run. The beforeTearDown()
    # method can also be used to clean up anything set up in afterSetUp(),
    # though it is less commonly used since test always run in a sandbox
    # that is cleared after the test is run.
    def afterSetUp(self):
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


    def testGetAliasIcon(self):
        self.f1.invokeFactory('Alias', 'alias')
        self.f1.invokeFactory('Document', 'doc') # used for the target
        doc   = self.f1.doc
        alias = self.f1.alias
        alias.setAlias(doc)

        self.failUnlessEqual(self.portal.simplealias_tool.getAliasIcon(doc), 'document_icon_alias.gif')


    def testGetLinkableTypes(self):
        # hardly impossible to test this but let's test the exclusion
        # now build up a filter
        self.portal.simplealias_tool.portal_type_filters = ['Document', 'File']

        types = self.portal.simplealias_tool.getLinkableTypes()
        self.failIf('Document' in types)
        self.failIf('File' in types)

    def testManagePasteAsAlias(self):
        self.f1.invokeFactory('Document', 'doc') # used for the target
        doc   = self.f1.doc
        doc.setTitle('target doc')
        doc.setDescription('target description')

        self.portal.invokeFactory('Folder', 'f2')
        self.f2 = self.portal.f2


        #transaction.commit(1)
        transaction.savepoint(1)
        clipboard = self.f1.manage_copyObjects(['doc',])
        result = self.portal.simplealias_tool.manage_pasteAsAlias(self.f2, cb_copy_data=clipboard)
        # now test the stuff
        supposed_alias = doc.getBRefs('linksTo')

        self.failIf(len(supposed_alias)==0)

        alias = self.f2.objectValues()[0]

        self.failUnlessEqual(alias.Title(), 'target doc')
        self.failUnlessEqual(alias.Description(), 'target description')

# This boilerplate method sets up the test suite
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # Add our test class here - you can add more test classes if you wish,
    # and they will be run together.
    suite.addTest(makeSuite(TestAliasCreation))
    return suite
