# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import unittest, time, os, signal

from shutil import rmtree
from cStringIO import StringIO
from subprocess import Popen, PIPE
from tempfile import mkdtemp, mktemp
from urlparse import urljoin

from stellaris.index.virtuoso import VirtuosoIndex, VirtuosoInstance
from stellaris.index.exceptions import IndexReplaceFailed, IndexDeleteFailed, IndexQueryFailed, IndexNotAvailable
from stellaris.client.parsers import SPARQLResults
from stellaris.graph import FileGraph
from stellaris.client import GraphClient, QueryClient
from utils import StellarisServerThread as Server
from stellaris.env import Environment
from benri.client.client import NotFound, Conflict

query = """
PREFIX exterms: <http://www.example.org/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT ?date ?lang ?g
#FROM NAMED <http://test.org/hello>
WHERE { GRAPH ?g {
<http://www.example.org/index.html> exterms:creation-date ?date .
<http://www.example.org/index.html> dc:language ?lang . 
}}
"""

#query = """
#PREFIX exterms: <http://www.example.org/terms/>
#PREFIX dc: <http://purl.org/dc/elements/1.1/>
#SELECT ?g 
#WHERE { GRAPH ?g { <http://www.example.org/index.html> ?p ?o } }
#"""

class TestVirtuosoIndex(unittest.TestCase):

    def setUp(self):
#        self.virtuoso = VirtuosoInstance('/usr/local/virtuoso-opensource', './tests/data/virtuoso.ini')
        self.bind = '127.0.0.1:9080'

#        dav_url = 'http://localhost:8891/DAV/home/dav/rdf_sink/'
        sparql_url = 'http://localhost:8891/sparql/'
        self.__tmp_dir = mkdtemp()

        self.index = VirtuosoIndex('/home/mikael/_install/', './tests/data/virtuoso.ini', sparql_url, self.__tmp_dir, isql_port=1112, baseuri='http://%s/' % self.bind)
        self.graph_name = '/hello'
        self.baseuri = ''

    def tearDown(self):
        self.index.close()
        rmtree(self.__tmp_dir)

    def testUpDown(self):
        pass

    def _query(self, query):
        query_res = self.index.query(query)
        
        # make sure that the query does not return only new values
        sparql = SPARQLResults()
        sparql.parse_xml(StringIO(query_res))
        
        return sparql

    def _replace(self, graph_name, g):
        self.index.replace(graph_name, g)

    def _delete(self, graph_name):
        self.index.delete(graph_name)

    def testReplace(self):
        # self.graph_name
        g = FileGraph(self.graph_name, './tests/data/add.rdf')
        self._replace(self.graph_name, g)

        sparql = self._query(query)
        print "\nresults: ", sparql.variables, len([r for r in sparql.rows])
        self.failUnlessEqual(sparql.variables, ['date', 'lang', 'g'])
        self.failUnlessEqual([(r['date'], r['lang'], r['g']) for r in sparql.rows], [('August 16, 1999', 'en', urljoin(self.baseuri, self.graph_name))])

        g2 = FileGraph(self.graph_name, './tests/data/update.rdf')
        self._replace(self.graph_name, g2)
        sparql = self._query(query)
        print sparql
        self.failUnlessEqual(sparql.variables, ['date', 'lang', 'g'])
        self.failUnlessEqual([(r['date'], r['lang'], r['g']) for r in sparql.rows], [('July 15, 1894', 'en', urljoin(self.baseuri, self.graph_name))])

    def testDelete(self):
        self.testReplace()
        self._delete(self.graph_name)

        sparql = self._query(query)
        print sparql
        self.failUnlessEqual(sparql.variables, ['date', 'lang', 'g'])
        self.failUnlessEqual([(r['date'], r['lang']) for r in sparql.rows], [])

class TestVirtuosoIndexWSGI(TestVirtuosoIndex):
    def setUp(self):
        self.env_path = mktemp()
        env = Environment(self.env_path, create=True)

        self.baseuri = 'http://example.org/'
        self.graph_col = '/'
        self.bind = '127.0.0.1:9080'
                
        env.config = {'store':{#'db_uri': 'sqlite://test_user:test_pass!@localhost:5432/stellaris',
#                               'data_path': env.data_dir,
                               'num_workers': '2',
                               'gc_interval': 2.0}}
        env.config['server'] = {'bind': self.bind}
        env.config['service'] = {'baseuri': self.baseuri,
                                 'prefix': self.graph_col,
                                 'stand_alone': "false"}
        env.config['index:virtuoso'] = {'type': 'virtuoso',
                                        'sparql_url': 'http://localhost:8891/sparql/',
                                        'install_prefix': '/home/mikael/_install/'}

        env.config['logging'] = {'type': 'file', 'level': 'debug'}

        base_path = os.path.join(env.data_dir, 'client')
        
        self.graph_client = GraphClient('http://%s' % self.bind, base_path=base_path, prefix=self.graph_col)
        
        self.query_client = QueryClient('http://%s' % self.bind, index_name='virtuoso', base_path=base_path, prefix=self.graph_col)

        self.server = Server(env)
        self.server.start()
        
        # let server start
        time.sleep(1.0)
        self.graph_name = '/hello'

    def tearDown(self):
        self.server.stop()
        #rmtree(self.env_path)

    def _query(self, query):
        query_res = self.query_client.query(query)
        
        # make sure that the query does not return only new values
        sparql = SPARQLResults()
        sparql.parse_xml(StringIO(query_res))
        
        return sparql

    def _replace(self, graph_name, g):
        try:
            self.graph_client.create(graph_name, g.serialized, 'application/rdf+xml')
        except Conflict, e:
            try:
                self.graph_client.update(graph_name, g.serialized, 'application/rdf+xml')
            except NotFound, e:
                print e

        time.sleep(10)

    def _delete(self, graph_name):
        try:
            self.graph_client.delete(graph_name)
        except NotFound, e:
            pass
        
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestVirtuosoIndex('testUpDown'))
    suite.addTest(TestVirtuosoIndex('testReplace'))
    suite.addTest(TestVirtuosoIndex('testDelete'))
    
    unittest.TextTestRunner(verbosity=2).run(suite)

#    wsgi_suite = unittest.TestSuite()
#    wsgi_suite.addTest(TestVirtuosoIndexWSGI('testUpDown'))
#    wsgi_suite.addTest(TestVirtuosoIndexWSGI('testReplace'))
#    wsgi_suite.addTest(TestVirtuosoIndexWSGI('testDelete'))
    
#    unittest.TextTestRunner(verbosity=2).run(wsgi_suite)
