
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.SimpleBlog.tests import SimpleBlogTC
from Products.SimpleBlog.config import ENTRY_IS_FOLDERISH

# A test class defines a set of tests
class TestInstallation(SimpleBlogTC.SimpleBlogTestCase):

    # The afterSetUp method can be used to define test class variables
    # and perform initialisation before tests are run. The beforeTearDown()
    # method can also be used to clean up anything set up in afterSetUp(),
    # though it is less commonly used since test always run in a sandbox
    # that is cleared after the test is run.
    def afterSetUp(self):
        self.css        = self.portal.portal_css
        self.kupu       = self.portal.kupu_library_tool
        self.skins      = self.portal.portal_skins
        self.types      = self.portal.portal_types
        self.factory    = self.portal.portal_factory
        self.workflow   = self.portal.portal_workflow
        self.properties = self.portal.portal_properties
        self.siteprops = self.properties.site_properties
        self.nav_props  = self.portal.portal_properties.navtree_properties
        self.actions = self.portal.portal_actions
        self.icons = self.portal.portal_actionicons
        self.metaTypes = ('Blog', 'BlogFolder', 'BlogEntry')


    def testSkinLayersInstalled(self):
        self.failUnless('SimpleBlog' in self.skins.objectIds())

    def testNewPermissions(self):
        managerPermission = [n['name'] for n in self.portal.permissionsOfRole('Manager')]
        self.failUnless('SimpleBlog: Cross-post' in managerPermission)
        self.failUnless('SimpleBlog: Add BlogEntry' in managerPermission)
        self.failUnless('SimpleBlog: Add Blog' in managerPermission)
        self.failUnless('SimpleBlog: Add BlogFolder' in managerPermission)

    def testTypesInstalled(self):
        for t in self.metaTypes:
            self.failUnless(t in self.types.objectIds())

    def testPortalFactorySetup(self):
        for t in self.metaTypes:
            self.failUnless(t in self.factory.getFactoryTypes())

    def testToolInstalled(self):
        self.failUnless('simpleblog_tool' in self.portal.objectIds())

    def testUseFolderTabs(self):
        self.failUnless('Blog' in self.siteprops.use_folder_tabs)
        self.failUnless('BlogFolder' in self.siteprops.use_folder_tabs)
        if ENTRY_IS_FOLDERISH:
            self.failUnless('BlogEntry' in self.siteprops.use_folder_tabs)
        else:
            self.failIf('BlogEntry' in self.siteprops.use_folder_tabs)

    def testUserFolderContents(self):
        self.failUnless('Blog' in self.siteprops.use_folder_contents)
        self.failUnless('BlogFolder' in self.siteprops.use_folder_contents)
        if ENTRY_IS_FOLDERISH:
            self.failUnless('BlogEntry' in self.siteprops.use_folder_contents)
        else:
            self.failIf('BlogEntry' in self.siteprops.use_folder_contents)

    def testEntriesNotInNavtree(self):
        self.failUnless('BlogEntry' in self.nav_props.metaTypesNotToList)

    def testCSSRegistration(self):
        self.failUnless('SimpleBlogCSS.css' in self.css.getResourceIds())

    def testDefaultPage(self):
        self.failUnless('Blog' in self.siteprops.default_page_types)

    def testDiscussionEnabled(self):
        self.failUnlessEqual(self.portal.portal_types.BlogEntry.allow_discussion, 1)

    def testControlPanel(self):
        actions = self.portal.portal_controlpanel.listActions()
        self.failUnless('SimpleBlogSetup' in [a.id for a in actions])

    def testWorkflowInstalled(self):
        self.failUnless('simpleblog_workflow' in self.workflow.getWorkflowIds())

    def testWorkflowAssignments(self):
        self.assertEqual(self.workflow.getChainForPortalType('Blog'), ('folder_workflow',))
        self.assertEqual(self.workflow.getChainForPortalType('BlogFolder'), ('folder_workflow',))
        self.assertEqual(self.workflow.getChainForPortalType('BlogEntry'), ('simpleblog_workflow',))

    def testIndices(self):
        indices = self.portal.portal_catalog.indexes()
        test_indices = ['getAlwaysOnTop',
                        'EntryCategory']
        for i in test_indices:
            self.failUnless(i in indices)



# This boilerplate method sets up the test suite
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # Add our test class here - you can add more test classes if you wish,
    # and they will be run together.
    suite.addTest(makeSuite(TestInstallation))
    return suite

if __name__ == '__main__':
    framework()

