import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from Testing.ZopeTestCase import installProduct
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

ptc.setupPloneSite()
from Products.PloneTestCase.layer import onsetup

import hc.am.base
import hc.am.products.ifma.fmp

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml', hc.am.base)
            ztc.installPackage('hc.am.base')
            ptc.setupPloneSite(products=['hc.am.base'])

        @classmethod
        def tearDown(cls):
            pass


class FunctionalTestCase(ptc.FunctionalTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml', hc.am.base)
            ztc.installPackage('hc.am.base')
            ptc.setupPloneSite(products=['hc.am.base',
                                         'hc.am.products.ifma.fmp',
                                         'hc.am.templates.ifma',])
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([


        ztc.FunctionalDocFileSuite(
            'README.txt', package='hc.am.products.ifma.fmp',
            test_class=TestCase,
            #optionflags=OPTIONFLAGS,
            ),

        #ztc.FunctionalDocFileSuite(
        #    'browser/README.txt', package='hc.am.products.ieee_cbp',
        #    test_class=FunctionalTestCase),
        
        ])

ptc.setupPloneSite(products=['hc.am.base',
                             'hc.am.products.ifma.fmp'])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

