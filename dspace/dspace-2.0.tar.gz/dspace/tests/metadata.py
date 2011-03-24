import os.path
import unittest

from lxml import etree

from oaipmh.common import Metadata
from oaipmh.metadata import MetadataRegistry

from dspace.metadata import *




class DspaceMetsMods(unittest.TestCase):
    def setUp(self):
        self.registry = MetadataRegistry()
        self.registry.registerReader('mets',dspace_mets_reader)
        self.element = etree.parse(os.path.join(os.path.dirname(__file__),
                                                'dspace_mets.xml')).getroot()
        self.item = self.registry.readMetadata('mets',self.element)

class DspaceMetsModsItem(DspaceMetsMods):
    
    def testDescription(self):
        """ Extract descriptions """
        self.assertEqual(self.item['description'],[u'A narrative history of the squadron.'])
    
    def testCreator(self):
        """ Extract creators """
        self.assertEqual(self.item['creator'],[u'United States Army Air Corps'])
    
    def testIssued(self):
        """ Extract issued dates """
        self.assertEqual(self.item['issued'],[u'1946'])
    
    def testTitle(self):
        """ Extract titles """
        self.assertEqual(self.item['title'],[u'42nd Bombardment Squadron (Heavy).'])
    
    def testSubject(self):
        """ Extract subjects """
        self.assertEqual(self.item['subject'],[u'Seventh Air Force',
                                                 u'South Pacific'])
    
    def testBundles(self):
        """ Extract bitstream bundles """
        self.assertEqual(len(self.item['bundles']),1)
        bundle = self.item['bundles'][0]
        self.assertEqual(bundle['name'], u'ORIGINAL')
        self.assertEqual(len(bundle['bitstreams']),1)
    

class DspaceMetsModsBitstream(DspaceMetsMods):
    def setUp(self):
        super(DspaceMetsModsBitstream, self).setUp()
        self.bitstream = self.item['bundles'][0]['bitstreams'][0]
    
    def testIdentifier(self):
        """ Extract bitstream identifier """
        self.assertEqual(self.bitstream['identifier'],u'1969.1_90570_1')
    
    def testMimetype(self):
        """ Extract bitstream mimetype """
        self.assertEqual(self.bitstream['mimetype'],u'application/pdf')
    
    def testSize(self):
        """ Extract bitstream size """
        self.assertEqual(self.bitstream['size'],u'2562574')
    
    def testChecksum(self):
        """ Extract bistream checksum """
        self.assertEqual(self.bitstream['checksum'],u'aa4c5cd2ac01ea0010a68a6b5633139e')
    
    def testChecksumType(self):
        """ Extract bitstream checksum type """
        self.assertEqual(self.bitstream['checksum_type'],u'MD5')
    
    def testUrl(self):
        """ Extract bitstream URL """
        self.assertEqual(self.bitstream['url'],u'http://dspace.intstitution.edu/bitstream/1969.1/90570/1/1%2042ndBS-History-1940-44.pdf')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(DspaceMetsModsItem))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(DspaceMetsModsBitstream))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
