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

import beyondskins.ploneday.site2011

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     beyondskins.ploneday.site2011)
    fiveconfigure.debug_mode = False
    ztc.installPackage('beyondskins.ploneday.site2011')

setup_product()

ptc.setupPloneSite(extension_profiles=['beyondskins.ploneday.site2011:default'])

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):

        @classmethod
        def tearDown(cls):
            pass



def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='beyondskins.ploneday.site2011',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='beyondskins.ploneday.site2011.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'README.txt', package='beyondskins.ploneday.site2011.docs',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | 
                         doctest.NORMALIZE_WHITESPACE | 
                         doctest.ELLIPSIS,
            test_class=TestCase),

        ztc.FunctionalDocFileSuite(
            'browser.txt', 
            package='beyondskins.ploneday.site2011.docs',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | 
                        doctest.NORMALIZE_WHITESPACE | 
                        doctest.ELLIPSIS,
            test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
