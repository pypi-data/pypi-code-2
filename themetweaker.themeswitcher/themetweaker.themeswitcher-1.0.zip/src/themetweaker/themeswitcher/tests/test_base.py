import unittest


from Testing import ZopeTestCase

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite()

import themetweaker.themeswitcher

class TestCase(PloneTestCase.PloneTestCase):


    def afterSetUp(self):
        fiveconfigure.debug_mode = True
        zcml.load_config('configure.zcml',
                            themetweaker.themeswitcher)
        zcml.load_config('overrides.zcml',
                            themetweaker.themeswitcher)
        zcml.load_config('configure.zcml',
                            themetweaker.themeswitcher.tests)
        fiveconfigure.debug_mode = False
        # Register the product profiles (GenericSetup junk).
        self.addProfile('themetweaker.themeswitcher:default')
        self.addProfile('themetweaker.themeswitcher.tests.skin_one:default')
        self.addProfile('themetweaker.themeswitcher.tests.skin_two:default')
        # Install the packages.
        self.addProduct('themetweaker.themeswitcher')
        self.addProduct('themetweaker.themeswitcher.tests.skin_one')
        self.addProduct('themetweaker.themeswitcher.tests.skin_two')


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='themetweaker.themeswitcher',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='themetweaker.themeswitcher.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ZopeTestCase.ZopeDocFileSuite(
        #    'README.txt', package='themetweaker.themeswitcher',
        #    test_class=TestCase),

        ZopeTestCase.FunctionalDocFileSuite(
           'form.txt', package='themetweaker.themeswitcher',
           test_class=TestCase),

        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
