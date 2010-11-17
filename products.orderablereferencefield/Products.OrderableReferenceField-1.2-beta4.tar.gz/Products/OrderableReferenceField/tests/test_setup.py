import unittest
from Products.OrderableReferenceField.tests.base import TestCase


PACKAGE = 'Products.OrderableReferenceField'
PACKAGE_DEPENDENCIES = ()


class TestSetup(TestCase):
    """Test the installation of this package
    Important: the name of all test-methods should start with test_
    """

    def afterSetUp(self):
        self.loginAsPortalOwner()

    def test_package_is_quickinstallable(self):
        #check if package is installable in portal_quickinstaller
        self.failUnless(self.portal.portal_quickinstaller.isProductInstallable(PACKAGE),
            '%s is not quickinstallable' % PACKAGE)

    def test_package_is_quickinstalled(self):
        #check if package actually has been installed in portal_quickinstaller
        self.failUnless(self.portal.portal_quickinstaller.isProductInstalled(PACKAGE),
           '%s is not quickinstalled' % PACKAGE)

    def test_package_is_quickinstalled_correctly(self):
        #check installation-status of the package in portal_quickinstaller
        for installed_product in self.portal.portal_quickinstaller.listInstalledProducts():
            if installed_product['id'] == PACKAGE:
                self.failIf(installed_product['hasError'], '%s is installed, but with errors' % PACKAGE)

    def test_deps_are_quickinstallable(self):
        #check if the dependencies are quickinstallable
        for product in PACKAGE_DEPENDENCIES:
            self.failUnless(self.portal.portal_quickinstaller.isProductInstalled(product),
             product + ' is not quickinstallable')

    def test_deps_are_quickinstalled(self):
        #check if the dependencies are actually quickinstalled
        for product in PACKAGE_DEPENDENCIES:
            self.failUnless(self.portal.portal_quickinstaller.isProductInstalled(product),
            product + ' is not quickinstalled')

    def test_deps_are_quickinstalled_correctly(self):
        #check installation-status of the dependencies in portal_quickinstaller
        for installed_product in self.portal.portal_quickinstaller.listInstalledProducts():
            for product in PACKAGE_DEPENDENCIES:
                if installed_product['id'] == product:
                    self.failIf(installed_product['hasError'], product+ ' is installed, but with errors')

    def testFail(self):
        #always passing dummy tests
        self.failIf(False)
        self.failUnless(True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
