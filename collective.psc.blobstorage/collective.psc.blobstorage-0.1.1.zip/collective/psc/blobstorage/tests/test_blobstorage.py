import unittest
from zope.testing import doctestunit
from zope.component import testing
from zope.interface import implements
from zope.component import getUtility, provideAdapter, adapts
from zope.interface.verify import verifyObject

from Products.PloneSoftwareCenter.storage.interfaces import IPSCFileStorage
from collective.psc.blobstorage import BlobStorage

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.adapters.stringio import BlobbableStringIO

from StringIO import StringIO

class Dummy: pass

class DummyBlobbableStringIO(BlobbableStringIO):
    """ adapter for StringIO instance to work with blobs """
    implements(IBlobbable)
    adapts(StringIO)

    def mimetype(self):
        return 'fake/mimetype'
        
provideAdapter(factory=DummyBlobbableStringIO)

class TestCase(unittest.TestCase):            
    def setUp(self):
        self.blobstorage = BlobStorage(Dummy())
        
    def test_implements_interface(self):
        assert verifyObject(IPSCFileStorage, self.blobstorage)
    
    def test_get_set_works(self):
        bs = self.blobstorage
        instance = Dummy()
        self.blobstorage.set('test', instance, 'test_value')
        v = self.blobstorage.get('test', instance)
        # see BlobWrapper.__str__
        assert str(v) == 'test_value'
        
def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestCase),))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
