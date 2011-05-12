import unittest

from zope.testing import doctestunit
from zope.component import testing
from zope.component import getUtility
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from zope.formlib import form

from collective.psc.mirroring.interfaces import IFSMirrorConfiguration

ptc.setupPloneSite(products=["collective.psc.mirroring"])

from zope.publisher.browser import TestRequest

import collective.psc.mirroring

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.psc.mirroring)
            fiveconfigure.debug_mode = False
            ztc.installPackage('collective.psc.blobstorage')

        @classmethod
        def tearDown(cls):
            pass
            


def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestCase),))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
