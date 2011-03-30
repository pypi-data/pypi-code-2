import unittest

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from zope.component import queryUtility

from betahaus.memberprofile.interfaces import IMemberProfileSettingsAdapter
from betahaus.memberprofile.tests.layer import MemberProfileLayer


class TestInstallation(ptc.PloneTestCase):
    """
    """
    layer = MemberProfileLayer
    
    def afterSetUp(self):
        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test 
        should be done in that test method.
        """

    def beforeTearDown(self):
        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """

    def testInstalled(self):
        qi = self.portal.portal_quickinstaller
        self.assertEquals(qi.isProductInstalled('betahaus.memberprofile'),True)
    
    def testSettingsAdapter(self):
        settings = IMemberProfileSettingsAdapter(self.portal)
        self.assertEqual(settings.get('title_as'),'username')
        settings.set('title_as', 'firstname_lastname')
        self.assertEqual(settings.get('title_as'),'firstname_lastname')
        
        self.assertEqual(settings.get('nonexistent_key'),None)

    def testTinyMCESettings(self):
        mce = getToolByName(self.portal, 'portal_tinymce', None)
        #Only run tests if TinyMCE is installed
        if mce is not None:
            self.failUnless('MemberProfile' in mce.containsobjects.split())
            self.failUnless('MemberProfile' in mce.containsanchors.split())
            self.failUnless('MemberProfile' in mce.linkable.split())
            self.failUnless('MemberProfile' in mce.imageobjects.split())
        

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
