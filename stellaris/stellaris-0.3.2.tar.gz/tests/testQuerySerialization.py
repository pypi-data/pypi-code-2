from rdflib import ConjunctiveGraph, plugin
from rdflib.store import Store
from StringIO import StringIO
import unittest, httplib2, urllib
from testNativeBackend import TestMemoryBackend

class TestQuerySerialization(TestMemoryBackend):

    def testExtraVariable(self):
        self.insert('./tests/data/add.rdf')

        query = """
        PREFIX exterms: <http://www.example.org/terms/>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?date ?lang ?blub
        WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . 
        }
        """
        
        res = self.store.query(query)
        correct = """<?xml version="1.0" encoding="utf-8"?><?xml-stylesheet type="text/xsl" href="/static/sparql-xml-to-html.xsl"?><ns0:sparql xmlns:ns0="http://www.w3.org/2005/sparql-results#"><ns0:head><ns0:variable name="date" /><ns0:variable name="lang" /><ns0:variable name="blub" /></ns0:head><ns0:results><ns0:result><ns0:binding name="date"><ns0:literal>August 16, 1999</ns0:literal></ns0:binding></ns0:result></ns0:results></ns0:sparql>"""
        
        self.failUnlessEqual(res, correct)

    def testXMLOptional(self):
        self.insert('./tests/data/add.rdf')

        query = """
        PREFIX exterms: <http://www.example.org/terms/>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?date ?lang
        WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . 
                OPTIONAL { <http://www.example.org/index.html> dc:language ?lang . }
        }
        """
        
        res = self.store.query(query)
        correct = """<?xml version="1.0" encoding="utf-8"?><?xml-stylesheet type="text/xsl" href="/static/sparql-xml-to-html.xsl"?><ns0:sparql xmlns:ns0="http://www.w3.org/2005/sparql-results#"><ns0:head><ns0:variable name="date" /><ns0:variable name="lang" /></ns0:head><ns0:results><ns0:result><ns0:binding name="date"><ns0:literal>August 16, 1999</ns0:literal></ns0:binding><ns0:binding name="lang"><ns0:literal>en</ns0:literal></ns0:binding></ns0:result></ns0:results></ns0:sparql>"""
        
        self.failUnlessEqual(res, correct)

if __name__ == "__main__":    
    suite = unittest.TestSuite()
    suite.addTest(TestQuerySerialization('testXMLOptional'))
    suite.addTest(TestQuerySerialization('testExtraVariable'))    

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestStorage)
    unittest.TextTestRunner(verbosity=2).run(suite)
