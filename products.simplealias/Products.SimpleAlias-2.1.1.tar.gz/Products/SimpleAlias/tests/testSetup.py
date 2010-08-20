# -*- coding: utf-8 -*-
# $Id: testSetup.py 123908 2010-08-20 10:27:22Z glenfant $


from Products.SimpleAlias.tests import SimpleAliasTC
from Products.CMFCore.utils import getToolByName

# A test class defines a set of tests
class TestInstallation(SimpleAliasTC.SimpleAliasTestCase):

    # The afterSetUp method can be used to define test class variables
    # and perform initialisation before tests are run. The beforeTearDown()
    # method can also be used to clean up anything set up in afterSetUp(),
    # though it is less commonly used since test always run in a sandbox
    # that is cleared after the test is run.
    def afterSetUp(self):
        self.css = self.portal.portal_css
        self.skins = self.portal.portal_skins
        # FIXME: Why kupu fails (test framework bug ?)
        # self.kupu = self.kupu_library_tool
        self.types = self.portal.portal_types
        self.factory = self.portal.portal_factory
        self.workflow  = self.portal.portal_workflow
        self.properties = self.portal.portal_properties
        self.siteprops = self.properties.site_properties
        self.nav_props  = self.portal.portal_properties.navtree_properties
        self.actions = self.portal.portal_actions
        self.icons = self.portal.portal_actionicons
        self.metaTypes = ('Alias',)

    def testSkinLayersInstalled(self):
        self.failUnless('SimpleAlias' in self.skins.objectIds())

    def testTypesInstalled(self):
        for t in self.metaTypes:
            self.failUnless(t in self.types.objectIds())

    def testPortalFactorySetup(self):
        self.failUnless('Alias' in self.factory.getFactoryTypes())

    def testToolInstalled(self):
        self.failUnless('simplealias_tool' in self.portal.objectIds())

    def testToolConfigured(self):
        expected = (
            'ATBooleanCriterion', 'ATCurrentAuthorCriterion', 'ATDateCriteria',
            'ATDateRangeCriterion', 'ATListCriterion', 'ATPathCriterion', 'ATPortalTypeCriterion',
            'ATReferenceCriterion', 'ATRelativePathCriterion', 'ATSelectionCriterion',
            'ATSimpleIntCriterion', 'ATSimpleStringCriterion', 'ATSortCriterion', 'Alias',
            'ChangeSet', 'Discussion Item', 'Favorite', 'Link', 'Plone Site', 'TempFolder')
        tool = getToolByName(self.portal, 'simplealias_tool')
        ptf = tool.getProperty('portal_type_filters')
        self.failUnlessEqual(set(ptf), set(expected))



# This boilerplate method sets up the test suite
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # Add our test class here - you can add more test classes if you wish,
    # and they will be run together.
    suite.addTest(makeSuite(TestInstallation))
    return suite

