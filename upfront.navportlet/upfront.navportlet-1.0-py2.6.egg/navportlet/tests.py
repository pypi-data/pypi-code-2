from plone.app.portlets.tests import test_navigation_portlet

from Products.CMFPlone.tests import dummy

class TestPortlet(test_navigation_portlet.TestPortlet):
    """ Extend navigation portlet tests to install upfront.navportlet
    """
    
    def afterSetUp(self):
        self.addProfile('upfront.navportlet:default')
        super(TestPortlet, self).afterSetUp()


class TestRenderer(test_navigation_portlet.TestRenderer):
    """ Extend navigation portlet tests to install upfront.navportlet
    """

    def afterSetUp(self):
        self.addProfile('upfront.navportlet:default')
        super(TestRenderer, self).afterSetUp()

    def testCreateNavTreeWithLink(self):
        """ Override and disable this test since the nav_catalog doesn't
            provide getRemoteUrl as metadata. The purpose of this test
            is not clear and it doesn't have a docstring so we are not
            going to include the metadata in the catalog without good
            reason.
        """
        pass

    def testNonStructuralFolderHidesChildren(self):
        """ Override and fix to using nav_catalog for indexing
        """
        # Make sure NonStructuralFolders act as if parentMetaTypesNotToQuery
        # is set.
        f = dummy.NonStructuralFolder('ns_folder')
        self.portal.folder1._setObject('ns_folder', f)
        self.portal.nav_catalog.reindexObject(self.portal.folder1.ns_folder)
        self.portal.nav_catalog.reindexObject(self.portal.folder1)
        view = self.renderer(self.portal.folder1.ns_folder)
        tree = view.getNavTree()
        self.assertEqual(tree['children'][3]['children'][3]['item'].getPath(),
                                '/plone/folder1/ns_folder')
        self.assertEqual(len(tree['children'][3]['children'][3]['children']), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
