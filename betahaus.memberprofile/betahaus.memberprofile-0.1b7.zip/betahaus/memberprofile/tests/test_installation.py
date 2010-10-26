"""This is an integration "unit" test. It uses PloneTestCase because I'm lazy
"""
import unittest
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from betahaus.memberprofile.tests import base

#Test imports
from zope.component import queryUtility
from betahaus.memberprofile.interfaces import IProfileUtils
from betahaus.memberprofile.interfaces import IMemberProfileSettingsAdapter

ptc.setupPloneSite()


class TestInstallation(base.TestCase):
    """Test usage of the social catalog.
    """
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
    
    def testProfileUtility(self):
        util = queryUtility(IProfileUtils)
        self.failUnless(util,"ProfileUtils not found")
        self.failUnless(IProfileUtils.providedBy(util),"ProfileUtils doesn't provide the correct interface")
        
    def testSettingsAdapter(self):
        settings = IMemberProfileSettingsAdapter(self.portal)
        self.assertEqual(settings.get('title_as'),'username')
        settings.set('title_as', 'firstname_lastname')
        self.assertEqual(settings.get('title_as'),'firstname_lastname')
        
        self.assertEqual(settings.get('nonexistent_key'),None)

    def testKupuSettings(self):
        klt = self.portal.kupu_library_tool
        self.failUnless('MemberProfile' in klt.getPortalTypesForResourceType('collection'))
        self.failUnless('MemberProfile' in klt.getPortalTypesForResourceType('linkable'))
        

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """ 
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstallation))
    return suite
