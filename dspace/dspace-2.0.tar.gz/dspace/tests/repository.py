from os.path import dirname, join
import unittest

from oaipmh.common import Metadata, Header
from oaipmh.tests.fakeclient import FakeClient

from dspace import Repository



class TestOAI(unittest.TestCase):
    def setUp(self):
        self.repository = Repository(url='http://dspace.institution.edu/dspace-oai/request')
        old_oai = self.repository.oai
        self.repository.oai = FakeClient(join(dirname(__file__),'repository'))
        self.repository.oai._metadata_registry = old_oai._metadata_registry
    
    def test_getName(self):
        """ Get the repository name """
        self.assertEqual(self.repository.getName(),
                         'The DSpace Repository')
    
    def test_getCollections(self):
        """ Get the collections in the repository """
        self.assertEqual(list(self.repository.getCollections()),
                         [('hdl_1969.1_6069','Accomplishment Reports'),
                          ('hdl_1969.1_6459','Arant-Kaspar, Wendi'),
                          ('hdl_1969.1_86400','Bales, Stephen')])
    
    def test_getItemHandles_all(self):
        """ Get item handles (all)"""
        self.assertEqual(list(self.repository.getItemHandles()),
                         ['1969.1/8',
                          '1969.1/9',
                          '1969/10',
                          '1969/11'])
    
    def test_getItemHandles_collection(self):
        """ Get item handles (collection)"""
        self.assertEqual(list(self.repository.getItemHandles(collection='1969.1/91215')),
                         ['1969.1/91216',
                          '1969.1/91217',
                          '1969.1/91218',
                          '1969.1/91219',
                          '1969.1/91220',
                          '1969.1/91221'])
    
    def test_getItemHandles_invalid_collection(self):
        """ Get item handles (invalid collection)"""
        self.assertRaises(ValueError,
                          list,
                          self.repository.getItemHandles(collection=123))
    
    def test_getItemIdentifiers_all(self):
        """ Get item identifiers (all)"""
        self.assertEqual(list(map(lambda i:i.identifier(),
                                  self.repository.getItemIdentifiers())),
                         ['oai:dspace.institution.edu:1969.1/8',
                          'oai:dspace.institution.edu:1969.1/9',
                          'oai:dspace.institution.edu:1969/10',
                          'oai:dspace.institution.edu:1969/11'])
    
    def test_getItemIdentifiers_collection(self):
        """ Get item identifiers (collection)"""
        self.assertEqual(list(map(lambda i:i.identifier(),
                                  self.repository.getItemIdentifiers(collection='1969.1/91215'))),
                         ['oai:dspace.institution.edu:1969.1/91216',
                          'oai:dspace.institution.edu:1969.1/91217',
                          'oai:dspace.institution.edu:1969.1/91218',
                          'oai:dspace.institution.edu:1969.1/91219',
                          'oai:dspace.institution.edu:1969.1/91220',
                          'oai:dspace.institution.edu:1969.1/91221'])
        
        
            
    
    def test_getItemIdentifiers_invalid_collection(self):
        """ Get item identifiers (invalid collection)"""
        self.assertRaises(ValueError,
                          self.repository.getItemIdentifiers,
                          collection=123)
    
    def test_getItems_all(self):
        """ Get items (all)"""
        items = list(self.repository.getItems())
        self.assertEqual(len(items), 20)
    
    def test_getItems_collection(self):
        """ Get items (collection)"""
        items = list(self.repository.getItems(collection='1969.1/91215'))
        self.assertEqual(len(items), 5)
    
    def test_getItems_invalid_collection(self):
        """ Get items (invalid collection)"""
        self.assertRaises(ValueError,
                          self.repository.getItems,
                          collection=123)
    
    def test_getItem_handle(self):
        """ Get item by handle """
        header, metadata, other = self.repository.getItem(handle='1969.1/91480')
        
        self.assert_(isinstance(header, Header))
        self.assert_(isinstance(metadata, Metadata))
    
    def test_getItem_identifier(self):
        """ Get item by identifier """
        header, metadata, other = self.repository.getItem(identifier='oai:dspace.institution.edu:1969.1/91480')
        
        self.assert_(isinstance(header, Header))
        self.assert_(isinstance(metadata, Metadata))
    
    def test_getItem_invalid(self):
        """ Get item (invalid input) """
        self.assertRaises(ValueError,
                          self.repository.getItem)
        self.assertRaises(ValueError,
                          self.repository.getItem,
                          handle='test',
                          identifier='test')
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestOAI))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
