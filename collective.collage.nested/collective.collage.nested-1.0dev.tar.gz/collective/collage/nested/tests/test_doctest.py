import unittest

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

# Do not remove next import as it is required to be able to create Collage objects
from Products.Collage.tests.base import CollageFunctionalTestCase

from collective.collage.nested.tests import base

ztc.installProduct('collective.collage.nested')
ptc.setupPloneSite(products=['collective.collage.nested'])

import collective.collage.nested

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.collage.nested)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='collective.collage.nested',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='collective.collage.nested.browser.helper',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'docs/vocabulary.txt', package='collective.collage.nested',
        #    test_class=base.FunctionalTestCase),
            
        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'docs/browser.txt', package='collective.collage.nested',
            test_class=base.FunctionalTestCaseWithContent),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='collective.collage.nested',
        #    test_class=base.FunctionalTestCase),


        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='collective.collage.nested',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
