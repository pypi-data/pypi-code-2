import pkg_resources
import unittest

from z3c.suds import get_suds_client

class Dummy(object):
    pass

class TestCase(unittest.TestCase):

    def setUp(self):
        test_wsdl = pkg_resources.resource_filename('z3c.suds', 'test.wsdl')
        self.test_wsdl = 'file://%s' % test_wsdl
    
    def tearDown(self):
        pkg_resources.cleanup_resources()
    
    def test_get_suds_client(self):
        client = get_suds_client(self.test_wsdl, context=Dummy())
        self.assertTrue(client)
    
    def test_get_suds_client_persistent_context(self):
        dummy_connection = Dummy()
        dummy_context = Dummy()
        dummy_context._p_jar = dummy_connection
        dummy_context._p_oid = 0
        
        get_suds_client(self.test_wsdl, dummy_context)
        self.assertTrue(hasattr(dummy_connection, 'foreign_connections'))
        self.assertTrue('suds_%s' % self.test_wsdl in dummy_connection.foreign_connections)
    
    def test_get_suds_client_default_context(self):
        import z3c.suds
        old_get_default_context = z3c.suds._get_default_context
        dummy = Dummy()
        z3c.suds._get_default_context = lambda: dummy
        
        get_suds_client(self.test_wsdl)
        self.assertTrue(hasattr(dummy, '_v_suds_client_cache'))
        
        z3c.suds._get_default_context = old_get_default_context
    
    def test_get_suds_client_missing_default_context(self):
        client = get_suds_client(self.test_wsdl)
        self.assertTrue(client)

def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
