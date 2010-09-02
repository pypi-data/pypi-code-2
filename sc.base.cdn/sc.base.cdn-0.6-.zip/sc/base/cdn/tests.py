import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc

from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.Five.testbrowser import Browser

from Products.CMFCore.utils import getToolByName

import sc.base.cdn

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     sc.base.cdn)
    fiveconfigure.debug_mode = False
    ztc.installPackage('sc.base.cdn')

setup_product()
ptc.setupPloneSite(products=['sc.base.cdn',])

class TestCase(FunctionalTestCase):
    
    def afterSetUp(self):
        super(TestCase, self).afterSetUp()
                
        self.browser = Browser()
        
        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('root', 'secret', ['Manager'], [])
        
        self.ptool = getToolByName(self.portal, 'portal_properties')
        self.site_props = self.ptool.site_properties
        
    def loginAsManager(self, user='root', pwd='secret'):
        """points the browser to the login screen and logs in as user root with Manager role."""
        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = user
        self.browser.getControl('Password').value = pwd
        self.browser.getControl('Log in').click()
        
class BaseTestCase(ptc.PloneTestCase):
    def afterSetUp(self):
        super(BaseTestCase, self).afterSetUp()
                
        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('root', 'secret', ['Manager'], [])
        
        self.ptool = getToolByName(self.portal, 'portal_properties')
        self.site_props = self.ptool.site_properties



def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='sc.base.cdn',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='sc.base.cdn.providers.coralcdn',
            setUp=testing.setUp, tearDown=testing.tearDown),
            
        doctestunit.DocTestSuite(
            module='sc.base.cdn.providers.hostname',
            setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='sc.base.cdn.providers.multiplehostnames',
            setUp=testing.setUp, tearDown=testing.tearDown),

        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'CDN.txt', package='sc.base.cdn.docs',
            test_class=BaseTestCase),
        ztc.FunctionalDocFileSuite(
            'CoralCDN.txt', package='sc.base.cdn.docs',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
            test_class=TestCase),
        ztc.FunctionalDocFileSuite(
            'AlternateHostname.txt', package='sc.base.cdn.docs',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
            test_class=TestCase),
        ztc.FunctionalDocFileSuite(
            'MultipleHostnames.txt', package='sc.base.cdn.docs',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
            test_class=TestCase),
        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='sc.base.cdn',
        #    test_class=TestCase),
        # 
        #Not really a test
        #ztc.ZopeDocFileSuite(
        #    'Benchmark.txt', package='sc.base.cdn.docs',
        #    test_class=TestCase),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
