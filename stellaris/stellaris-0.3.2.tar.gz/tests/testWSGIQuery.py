# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# integration tests using the client and the WSGI frontend

import unittest, time, os
from tempfile import mktemp
from shutil import rmtree
from mimetypes import guess_type
from urlparse import urljoin
from utils import file_to_str, dump_to_file, StellarisServerThread as Server
from benri.client.client import NotFound
from cStringIO import StringIO

from stellaris.store.exceptions import GraphNotFound, Unauthorized
from stellaris.client import GraphClient, QueryClient, SystemClient
from stellaris.client.parsers import SPARQLResults
from stellaris.graph import Graph, FileGraph
from stellaris.env import Environment

class TestWSGIQuery(unittest.TestCase):

    def setUp(self):
        self.env_path = mktemp()
        env = Environment(self.env_path, create=True)

        self.baseuri = 'http://example.org/'
        self.graph_col = '/'
        
        self.bind = '127.0.0.1:9091'
        
        env.config = {'store':{'db_uri': 'sqlite:///%s' % (env.db_dir + '/tmp.db'),
#                               'data_path': env.data_dir,
                               'num_workers': '2',
                               'gc_interval': 2.0}}
        env.config['server'] = {'bind': self.bind}
        env.config['service'] = {'baseuri': self.baseuri,
                                 'prefix': self.graph_col,
                                 'stand_alone': "false"}
        env.config['index:test'] = {'type':'rdflib-memory'}
        env.config['logging'] = {'type': 'console', 'level': 'debug'}

        base_path = os.path.join(env.data_dir, 'client')
        
        self.graph_client = GraphClient('http://%s' % self.bind, base_path=base_path, prefix=self.graph_col)

        self.system_client = SystemClient('http://%s' % self.bind, base_path=base_path, prefix=self.graph_col)
        
        self.query_client = QueryClient('http://%s' % self.bind, index_name='test', base_path=base_path, prefix=self.graph_col)

        self.server = Server(env)
        self.server.start()
        
        # let server start
        time.sleep(1.0)
    
    def tearDown(self):
        self.server.stop()
        rmtree(self.env_path)

    def create_graph(self, name, file_name):
        f = file(file_name, 'r')
        mime, _ = guess_type(file_name)
        stat, resp = self.graph_client.create(name, f, mime)
        f.close()
        return stat, resp
        
    def testUpDown(self):
        pass

    def testListIndices(self):
        self.failUnless(['test', 'query'], self.system_client.indices())
        
    def testSPARQLXML(self):
        self.create_graph('test', './tests/data/add.rdf')

        query = """PREFIX exterms: <http://www.example.org/terms/>
                   PREFIX dc: <http://purl.org/dc/elements/1.1/>
                   SELECT ?date ?lang
                   WHERE { <http://www.example.org/index.html> exterms:creation-date ?date .
                           <http://www.example.org/index.html> dc:language ?lang . }"""
        
        query_res = self.query_client.query(query)
        
        sparql = SPARQLResults()
        sparql.parse_xml(StringIO(query_res))
        
        self.failUnlessEqual(sparql.variables, ['date', 'lang'])
        self.failUnlessEqual([(r['date'], r['lang']) for r in sparql.rows], [('August 16, 1999', 'en')])

    def testSPARQLJSON(self):
        self.create_graph('test', './tests/data/add.rdf')

        query = """PREFIX exterms: <http://www.example.org/terms/>
                   PREFIX dc: <http://purl.org/dc/elements/1.1/>
                   SELECT ?date ?lang
                   WHERE { <http://www.example.org/index.html> exterms:creation-date ?date .
                           <http://www.example.org/index.html> dc:language ?lang . }"""
        
        query_res = self.query_client.query(query, format='json')
        
        sparql = SPARQLResults()
        sparql.parse_json(StringIO(query_res))

        self.failUnlessEqual(sparql.variables, ['date', 'lang'])
        self.failUnlessEqual([(r['date'], r['lang']) for r in sparql.rows], [('August 16, 1999', 'en')])

    def testSPARQLFromNamed(self):
        stat, resp = self.create_graph('test', './tests/data/add.rdf')        
        graph_attrs = self.system_client.graph_retrieve('test')
                
        query = """PREFIX exterms: <http://www.example.org/terms/>
                   PREFIX dc: <http://purl.org/dc/elements/1.1/>
                   SELECT ?date ?lang
                   FROM NAMED <%s>
                   WHERE { <http://www.example.org/index.html> exterms:creation-date ?date .
                           <http://www.example.org/index.html> dc:language ?lang . }
                """ % graph_attrs['graph-name']
        
        query_res = self.query_client.query(query)
        
        sparql = SPARQLResults()
        sparql.parse_xml(StringIO(query_res))
        
        self.failUnlessEqual(sparql.variables, ['date', 'lang'])
        self.failUnlessEqual([(r['date'], r['lang']) for r in sparql.rows], [('August 16, 1999', 'en')])

    def testSPARQLCollections(self):
        stat, resp = self.create_graph('/a/add', './tests/data/add.rdf')
        stat, resp = self.create_graph('/a/update', './tests/data/update.rdf')
        stat, resp = self.create_graph('/b/replace', './tests/data/replace.rdf')        
        
        graph_attrs = self.system_client.graph_retrieve('/a/add')
        query = """PREFIX exterms: <http://www.example.org/terms/>
                   PREFIX dc: <http://purl.org/dc/elements/1.1/>
                   SELECT DISTINCT ?date ?lang
                   FROM NAMED <%s>
                   WHERE { <http://www.example.org/index.html> exterms:creation-date ?date .
                           <http://www.example.org/index.html> dc:language ?lang . }
                """ % (os.path.dirname(graph_attrs['graph-name']) + '/')
        
        query_res = self.query_client.query(query)
        sparql = SPARQLResults()
        try:
            sparql.parse_xml(StringIO(query_res))
        except:
            print query_res 
        
        self.failUnlessEqual(sparql.variables, ['date', 'lang'])
        self.failUnlessEqual([(r['date'], r['lang']) for r in sparql.rows], [('August 16, 1999', 'en'), ('July 15, 1894', 'en')])
         
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestWSGIQuery('testUpDown'))
#    suite.addTest(TestWSGIQuery('testListIndices'))
#    suite.addTest(TestWSGIQuery('testSPARQLXML'))
#    suite.addTest(TestWSGIQuery('testSPARQLJSON'))
#    suite.addTest(TestWSGIQuery('testSPARQLFromNamed'))
#    suite.addTest(TestWSGIQuery('testSPARQLCollections'))
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestWSGISystem)
#    unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()

