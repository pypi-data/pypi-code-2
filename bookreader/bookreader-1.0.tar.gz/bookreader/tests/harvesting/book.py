from datetime import datetime
import unittest

#from django.test import TestCase

#from bookreader.models import Book, Link, Annotation, Page
from bookreader.harvesting.book import BookHarvester
from bookreader.tests.oai import BaseRepositoryTest



class BaseTest(BaseRepositoryTest):
    fixtures = ['tests/repository','tests/collection','tests/harvesting/book']
    
    def setUp(self):
        super(BaseTest, self).setUp()
        
        if self.book_identifier:
            self.harvester = BookHarvester(self.book)
        else:
            self.harvester = None
    
class TestSetAdditionalMetadata(BaseTest):
    book_identifier = 'oai:dspace.institution.edu:1969.1/0003'
    
    def test_listValue(self):
        """ BookHarvester._set_additional_metadata: Set a list additional metadata value """
        self.harvester._set_additional_metadata('test',[' value '])
        
        self.assertEqual(self.book.additional_metadata.getlist('test'),
                         ['value'])
    
    def test_falseValues(self):
        """ BookHarvester._set_additional_metadata: Set a false additional metadata value """
        self.harvester._set_additional_metadata('test',False)
        self.assertFalse('test' in self.book.additional_metadata)
        
        self.harvester._set_additional_metadata('test',0)
        self.harvester._set_additional_metadata('test',False)
        
        self.harvester._set_additional_metadata('test','')
        self.harvester._set_additional_metadata('test',False)
        
        self.harvester._set_additional_metadata('test',[])
        self.harvester._set_additional_metadata('test',False)

class TestSetCanonicalHandles(BaseTest):
    book_identifier = 'oai:dspace.institution.edu:1969.1/0003'
    field = 'canonical'
    default = 'oai:dspace.institution.edu:1969.1/0002'
    
    def test_setValid(self):
        """ BookHarvester._set_reference_handle: Set a valid reference """
        self.harvester._set_reference_handle(self.field,
                                             'http://dspace.institution.edu/handle/1969.1/0005')
        
        self.assertEqual(getattr(self.book,self.field).identifier,
                         'oai:dspace.institution.edu:1969.1/0005')
    
    def test_setNull(self):
        """ BookHarvester._set_reference_handle: Remove the reference """
        self.harvester._set_reference_handle(self.field,'')
        self.assertEqual(getattr(self.book,self.field,True), None)
    
    def test_setCircular(self):
        """ BookHarvester._set_reference_handle: Set a circular reference """
        
        self.assertRaises(ValueError,
                          self.harvester._set_reference_handle,
                          self.field,
                          'http://dspace.institution.edu/handle/1969.1/0003')
        self.assertEqual(getattr(self.book,self.field).identifier,
                         self.default)
    
    def test_setNonExistant(self):
        """ BookHarvester._set_reference_handle: Set a non-existant reference """
        self.assertRaises(ValueError,
                          self.harvester._set_reference_handle,
                          self.field,
                          'http://dspace.institution.edu/handle/1969.1/0000')
        self.assertEqual(getattr(self.book,self.field).identifier,
                         self.default)

class TestSetWorkHandles(TestSetCanonicalHandles):
    field = 'work'
    default = 'oai:dspace.institution.edu:1969.1/0001'

class TestUpdateMetadata(BaseTest):
    """ This needs to be more comprehensive, test single values, different dates
    invalid values, etc """
    
    book_identifier = 'oai:dspace.institution.edu:1969.1/0003'
    core = {'title': 'An existing copy of a work, harvested from OAI',
            'creator': 'The Author, harvested, The Second Author, harvested',
            'created': '1556',
            'thumbnail': 'http://dspace.institution.edu/bitstream/handle/1969.1/003/thumbs/pl_tamu_001_00712.jpg',
            'issued': datetime(2010,7,12,17,04,42)}
    
    additional = {'alternate title': ['A Work', 'An existing copy of a work'],
                  'description': ['Description 1','Description 2'],
                  'contributor': ['Contributor 1','Contributor 2'],
                  'subject': ['Subject 1','Subject 2'],
                  'other subject': ['Other Subject 1','Other Subject 2'],
                  'publisher': ['Publisher 1, Year','Publisher 2, Year']}
    
    def setUp(self):
        super(TestUpdateMetadata, self).setUp()
        self.harvester.update_metadata()
    
    def test_core(self):
        """ BookHarvester.update_metadata: core metadata fields """
        for key, value in self.core.items():
            self.assertEqual(getattr(self.book, key),value,
                             'Invalid value for %s, expecting %s and received '
                             '%s' % (key, str(value), str(getattr(self.book,key)),))
        
    
    def test_additional(self):
        """ BookHarvester.update_metadat: additional metadata fields """
        self.assertEqual(len(self.additional),
                         len(self.book.additional_metadata),
                         "Number of fields in additional_metadata don't match "
                         "expected: %d != %d" % (len(self.additional),
                                                 len(self.book.additional_metadata)))
        for key,value in self.additional.items():
            self.assert_(key in self.book.additional_metadata,
                         'The field, %s, is missing' % (str(key),))
            self.assertEqual(self.book.additional_metadata.getlist(key),
                             value,
                             'Invalid value for %s, expecting %s and received '
                             '%s' % (key, str(value),
                                     str(self.book.additional_metadata.getlist(key)),))
    
class TestBundles(BaseTest):
    book_identifier = 'oai:dspace.institution.edu:1969.1/0003'
    
    def setUp(self):
        super(TestBundles, self).setUp()
        self.bundles = self.harvester.bundles
    
    
    def test_bundles(self):
        """ BookHarvester.bundles: all bundles retrieved """
        self.assertEqual(len(self.bundles), 3)
        self.assert_('ORIGINAL' in self.bundles)
        self.assert_('THUMBNAIL' in self.bundles)
        self.assert_('METADATA' in self.bundles)
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSetAdditionalMetadata))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSetCanonicalHandles))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSetWorkHandles))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestUpdateMetadata))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBundles))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())