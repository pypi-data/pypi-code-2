# -*- coding: utf-8 -*-
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
ptc.setupPloneSite()

import beyondskins.pythonbrasil.site

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', beyondskins.pythonbrasil.site)
    fiveconfigure.debug_mode = False

setup_product()
ptc.setupPloneSite(products=['beyondskins.pythonbrasil.site'],
                   extension_profiles=['beyondskins.pythonbrasil.site:default',])

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             beyondskins.pythonbrasil.site)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='beyondskins.pythonbrasil.site',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='beyondskins.pythonbrasil.site.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='beyondskins.pythonbrasil.site.doc',
        #    test_class=TestCase),

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='beyondskins.pythonbrasil.site.doc',
            test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
