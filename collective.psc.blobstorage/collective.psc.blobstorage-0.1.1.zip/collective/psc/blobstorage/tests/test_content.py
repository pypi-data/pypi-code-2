import unittest, os

from zope.testing import doctestunit, doctest
from zope.component import testing
from zope.component import getUtility
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from zope.formlib import form
from Products.PloneTestCase.layer import onsetup


from zope.publisher.browser import TestRequest

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

@onsetup
def setup_product():
   fiveconfigure.debug_mode = True
   import collective.psc.blobstorage
   zcml.load_config('configure.zcml',
                    collective.psc.blobstorage)
   fiveconfigure.debug_mode = False
   ztc.installPackage('collective.psc.blobstorage')

setup_product()
ptc.setupPloneSite(products=["collective.psc.blobstorage"])

from Products.PloneSoftwareCenter.tests.base import PSCTestCase

class TestCase(PSCTestCase):
    def afterSetUp(self):
        super(TestCase, self).afterSetUp()
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.setStorageStrategy('blobstorage')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.portal.psc.proj.releases.invokeFactory('PSCRelease', '1.0')

    def test_adding_blob_download(self):
        self.portal.psc.proj.releases['1.0'].invokeFactory('PSCFile', 'file')
        self.file = self.portal.psc.proj.releases['1.0'].file
        
def test_suite(): 
        return unittest.TestSuite((unittest.makeSuite(TestCase),))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
