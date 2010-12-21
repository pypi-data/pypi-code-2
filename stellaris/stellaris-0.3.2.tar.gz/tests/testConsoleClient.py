# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import unittest, time
from tempfile import mkdtemp
from shutil import rmtree

from utils import file_to_str
from StringIO import StringIO

from stellaris.store import FrontendStore
from stellaris.graph import FileGraph
from stellaris.security import READ, READ_WRITE, ADMIN_GROUP
from stellaris.client.console import run

from stellaris.store.exceptions import GraphNotFound, Unauthorized, GroupAlreadyExists, GroupNotFound

class testConsoleClient(unittest.TestCase):

    def setUp(self):
        self.db_path = mkdtemp()
        self.spool_path = mkdtemp()
        
        self.baseuri = 'http://example.org/'
        self.graph_col = '/test_graphs/'
        
        self.bind = '127.0.0.1:9090'
        base_path = os.path.join(self.db_path, 'client')
        
        config = {'server': {'bind': self.bind}}
        config['service'] = {'graphs_prefix': self.graph_col}

        config['security'] = {'enabled': 'false',
                              'data_path': os.path.join(self.db_path, 'security')}
                              
        config['store'] = {'db_uri': 'sqlite:///%s' % (self.db_path + '/tmp.db'),
                           'spool_path': self.spool_path,
                           'num_workers': '2',
                           'gc_interval': 2.0,
                           'baseuri': urljoin(self.baseuri, self.graph_col)}  
        config['index:test'] = {'type':'rdflib-memory', 
                                'baseuri': self.baseuri}

        self.server = Server(config)
        self.server.start()
        
        # let server start
        time.sleep(1.0)
    
    def tearDown(self):
        self.server.stop()
        rmtree(self.db_path)
        rmtree(self.spool_path)

