# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# integration tests using the client and the WSGI frontend

import unittest, time, os, random
from tempfile import mktemp
from shutil import rmtree
from mimetypes import guess_type
from urlparse import urljoin
from utils import file_to_str, dump_to_file, StellarisServerThread as Server, memory, resident, stacksize, memory_usage, child_pids
from benri.client.client import NotFound
from threading import Thread, currentThread

from stellaris.store.exceptions import GraphNotFound, Unauthorized
from stellaris.client import GraphClient, QueryClient, SystemClient
from stellaris.client.parsers import SPARQLResults
from stellaris.graph import Graph, FileGraph
from stellaris.env import Environment

def dump_tsv(path, data):
    f = file(path, 'a')
    f.write('%s\n' % '\t'.join([str(a) for a in data]))
    f.close()

def dump_tsv_bulk(path, entries):
    f = file(path, 'a')

    for entry in entries:
        f.write('%s\n' % '\t'.join([str(a) for a in entry]))

    f.close()

def dump_mem_stats(dir_name, c_time, pid):
    path = '%s/pid_%d.csv' % (dir_name,pid)
    
    if not os.path.exists(path):
        headers = ['time', 'size', 'resident', 'share', 'text', 'lib', 'data/stack']
        dump_tsv(path, headers)

    data = [c_time] + memory_usage(pid)
    dump_tsv(path, data)

def dump_op_record(dir_name, record):
    path = '%s/ops_record.csv' % (dir_name)

    if not os.path.exists(path):
        headers = ['time', 'op', '"graph name"', '"data set"', '"exec time"', 'thread']
        dump_tsv(path, headers)    

    t = currentThread()
    record.append(t.getName())
    dump_tsv(path, record)

def dump_op_records(dir_name, records):
    path = '%s/ops_record.csv' % (dir_name)

    if not os.path.exists(path):
        headers = ['time', 'op', '"graph name"', '"data set"', '"exec time"', 'thread']
        dump_tsv(path, headers)    

    thread_name = currentThread().getName()
    new_records = [r + [thread_name] for r in records]
    dump_tsv_bulk(path, new_records)

def dump_store_stats(dir_name, c_time, num_graphs, num_cols):
    path = '%s/graphs.csv' % dir_name
    
    if not os.path.exists(path):
        headers = ['time', 'graphs', 'cols']
        dump_tsv(path, headers)

    dump_tsv(path, [c_time, num_graphs, num_cols])        
        
class TestStress(unittest.TestCase):

    def setUp(self):
        self.env_path = mktemp(prefix='/home/mikael/tmp/')
        env = Environment(self.env_path, create=True)

        self.baseuri = 'http://example.org/'
        self.graph_col = '/'
        
        self.bind = '127.0.0.1:9080'
        
        env.config = {'store':{'db_uri': 'sqlite:///%s' % (env.db_dir + '/tmp.db'),
#                               'data_path': env.data_dir,
                               'num_workers': '1',
                               'gc_interval': 2.0}}
        env.config['server'] = {'bind': self.bind}
        env.config['service'] = {'baseuri': self.baseuri,
                                 'graphs_prefix': self.graph_col}
        env.config['index:dummy'] = {'type':'dummy'}
        env.config['logging'] = {'type': 'file', 'level': 'debug'}

        env.log = env.setup_logging()
        base_path = os.path.join(env.data_dir, 'client')
        
        self.graph_client = GraphClient('http://%s' % self.bind, base_path=base_path, graphs_prefix=self.graph_col)

        self.system_client = SystemClient('http://%s' % self.bind, base_path=base_path, system_prefix='/system/')
        
        self.query_client = QueryClient('http://%s' % self.bind, index_name='test', base_path=base_path, query_prefix='/query/')

        self.server = Server(env)
        self.server.start()
        
        # let server start
        time.sleep(1.0)
    
    def tearDown(self):
        self.server.stop()
#        rmtree(self.env_path)

    def _gen_collection(self, depth, num_choices=10):
        a_start = 65
        char_pool = [chr(i) for i in range(a_start, a_start+num_choices)]
        cols = []

        for i in range(depth):
            cols.append(random.choice(char_pool))

        return '/%s/' % ('/'.join(cols))

    def _gen_collections(self, num_cols, col_length=3, col_name_choices=10):
        cols = set()

        while len(cols) < num_cols:
            cols.add(self._gen_collection(random.randrange(1,col_length+1), num_choices=col_name_choices))

        return cols

    def _gen_graphs(self, cols, min_graphs, max_graphs):
        all_graphs = []
        start_graph = int(random.random()*2**32)
        for col in cols:
            for i in range(random.randrange(min_graphs, max_graphs)):
                all_graphs.append(col + str(start_graph+i))

        return all_graphs

    def _stat_path(self, path):
        # find name of new stat dir
        def is_int(i):
            try:
                int(i)
                return True
            except ValueError, e:
                return False

        try:
            max_stat = max([int(i) for i in os.listdir(path) if is_int(i)]) + 1
        except ValueError, e:
            max_stat = 1

        stat_path = './tests/stat/%d' % max_stat # str(int(time.time()))
        os.mkdir(stat_path)
        return stat_path

    def testInsertManyGraphs(self):
        num_graphs = 10
        data = file_to_str('./tests/data/add.rdf')
        
        parent_pid = os.getpid()
        pids = child_pids(parent_pid)
        pids.append(parent_pid)

        print ["%d: %d kB" % (pid, memory(pid)/1024) for pid in pids]
        time.sleep(5)

        for i in range(num_graphs):
            self.graph_client.create('/test/%d' % i, data, 'application/rdf+xml')

    def testRandomLongGraphs(self):
        # issue random operations on random data with random delays
                
        stat_path = self._stat_path('./tests/stat/')
        total_time = 60*60*8
        concurrent_threads = 15
        col_length = 3
        col_name_choices = 10
        num_cols = 100
        min_graphs = 10
        max_graphs = 2**20
                
        mime_type = 'application/rdf+xml'
        ops = ['create', 'retrieve', 'delete', 'graph_update', 'graph_remove', 'graph_append']
        files = ['add.rdf', 'remove.rdf', 'append.rdf', 'update.rdf', 'replace.rdf']
        paths = ['./tests/data/%s' % f for f in files]
        
        cols = self._gen_collections(num_cols, col_length=col_length, col_name_choices=col_name_choices)
        all_graphs = self._gen_graphs(cols, min_graphs, max_graphs)

        parent_pid = os.getpid()
        pids = child_pids(parent_pid)
        pids.append(parent_pid)

        # init the stats
        for pid in pids:            
            dump_mem_stats(stat_path, 0, pid)
        
        dump_store_stats(stat_path, 0, 0, 0)

        current_time = 0
        
        def random_ops(max_time, min_op_interarrival, max_op_interarrival):
            c_t = 0
            
            ops_record = []
            
            while c_t < max_time:
                op = random.choice(ops)
                f = getattr(self.graph_client, op)

                graph_name = random.choice(all_graphs)
                path = random.choice(paths)
                
                t = time.time()
                try:
                    if op in ['delete', 'retrieve']:
                        f(graph_name)
                    else:
                        f(graph_name, file_to_str(path), mime_type)
                except NotFound, e:
                    # this is excepted to happen all the time
                    pass
                except Exception, e:
                    print "exception: ", e
    
                dt = time.time() - t
                ops_record.append([current_time+c_t, op, graph_name, os.path.basename(path), dt])
                sleep_time = random.uniform(min_op_interarrival, max_op_interarrival)
                time.sleep(sleep_time)
                c_t += dt + sleep_time
            
            # thread is done, record the ops that it performed
            for record in ops_record:
                dump_op_record(stat_path, record)

        while current_time < total_time:
            thread_time = 10
            
            print "Starting iteration: ", current_time            
            threads = []
            for i in range(concurrent_threads):
                threads.append(Thread(target=random_ops, args=(thread_time, 0.5, 2.0)))

            for t in threads:
                t.start()
            
            for t in threads:
                t.join()

            current_time += thread_time

            for pid in pids:            
                dump_mem_stats(stat_path, current_time, pid)
                
            cols, graphs = self.system_client.collection_retrieve('/', recursive=True)
            dump_store_stats(stat_path, current_time, len(graphs), len(cols))

    def testCreateGraphs(self):
        num_cols = 1000
        col_length = 6
        min_graphs = 10
        max_graphs  = 100
        num_threads = 8
        threads = []

        cols = self._gen_collections(num_cols, col_length=col_length)
        all_graphs = self._gen_graphs(cols, min_graphs, max_graphs)
        mime_type = 'application/rdf+xml'
        data = file_to_str('./tests/data/add.rdf')
        stat_path = self._stat_path('./tests/stat/')

        def create_worker(graphs, start_iter):
            op_records = []
            cur_iter = start_iter

            print "Worker creating %d graphs." % len(graphs)

            for graph_name in graphs:
                try:
                    t = time.time()
                    self.graph_client.create(graph_name, data, mime_type)
                    t_create = time.time() - t
                except NotFound, e:
                    # this is excepted to happen all the time
                    pass
                except Exception, e:
                    print "exception: ", e
                
                dt = time.time() - t
                op_records.append([cur_iter, 'create', graph_name, 'add.rdf', str(dt)])
                cur_iter += 1
            
                # dump records for every 1000th graph
                if cur_iter % 1000 == 0:
                    print "%s, graphs remaining: %d" % (str(currentThread().getName()), len(graphs)-(cur_iter-start_iter)) 
                    dump_op_records(stat_path, op_records)
                    op_records = []

            dump_op_records(stat_path, op_records)

        graphs_per_thread = len(all_graphs)/num_threads

        for i in range(num_threads):
            threads.append(Thread(target=create_worker, args=(all_graphs[i*graphs_per_thread:(i+1)*graphs_per_thread], i*graphs_per_thread)))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

class TestStressIndex(TestStress):

    def setUp(self):
        self.env_path = mktemp()
        env = Environment(self.env_path, create=True)

        self.baseuri = 'http://example.org/'
        self.graph_col = '/'
        
        self.bind = '127.0.0.1:9080'
        
        env.config = {'store':{'db_uri': 'sqlite:///%s' % (env.db_dir + '/tmp.db'),
#                               'data_path': env.data_dir,
                               'num_workers': '2',
                               'gc_interval': 2.0}}
        env.config['server'] = {'bind': self.bind}
        env.config['service'] = {'baseuri': self.baseuri,
                                 'graphs_prefix': self.graph_col}
        env.config['index:dummy'] = {'type':'rdflib-memory'}
        env.config['logging'] = {'type': 'console', 'level': 'critical'}

        base_path = os.path.join(env.data_dir, 'client')
        
        self.graph_client = GraphClient('http://%s' % self.bind, base_path=base_path, graphs_prefix=self.graph_col)

        self.system_client = SystemClient('http://%s' % self.bind, base_path=base_path, system_prefix='/system/')
        
        self.query_client = QueryClient('http://%s' % self.bind, index_name='test', base_path=base_path, query_prefix='/query/')

        self.server = Server(env)
        self.server.start()
        
        # let server start
        time.sleep(1.0)

class TestStressVirtuosoIndex(TestStress):

    def setUp(self):
        self.env_path = mktemp()
        env = Environment(self.env_path, create=True)

        self.baseuri = 'http://example.org/'
        self.graph_col = '/'
        
        self.bind = '127.0.0.1:9080'
        
        env.config = {'store':{'db_uri': 'postgres://test_user:test_pass!@localhost:5432/stellaris',
#                               'data_path': env.data_dir,
                               'num_workers': '2',
                               'gc_interval': 2.0}}
        env.config['server'] = {'bind': self.bind}
        env.config['service'] = {'baseuri': self.baseuri,
                                 'graphs_prefix': self.graph_col}

        env.config['index:virtuoso'] = {'type': 'virtuoso',
                                        'rdfsink_url': 'http://localhost:8890/DAV/home/dav/rdf_sink/',
                                        'sparql_url': 'http://localhost:8890/sparql/',
                                        'user': 'dav',
                                        'password': 'dav'}
        env.config['logging'] = {'type': 'console', 'level': 'critical'}

        base_path = os.path.join(env.data_dir, 'client')
        
        self.graph_client = GraphClient('http://%s' % self.bind, base_path=base_path, graphs_prefix=self.graph_col)

        self.system_client = SystemClient('http://%s' % self.bind, base_path=base_path, system_prefix='/system/')
        
        self.query_client = QueryClient('http://%s' % self.bind, index_name='test', base_path=base_path, query_prefix='/query/')

        self.server = Server(env)
        self.server.start()
        
        # let server start
        time.sleep(1.0)
                    
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestStress('testInsertManyGraphs'))
#    suite.addTest(TestStress('testRandomLongGraphs'))
#    suite.addTest(TestStress('testCreateGraphs'))

    unittest.TextTestRunner(verbosity=2).run(suite)

#    index_suite = unittest.TestSuite()
#    suite.addTest(TestStressIndex('testInsertManyGraphs'))
#    index_suite.addTest(TestStressIndex('testRandomLongGraphs'))
#   unittest.TextTestRunner(verbosity=2).run(index_suite)

    virtuoso_suite = unittest.TestSuite()
#    virtuoso_suite.addTest(TestStressVirtuosoIndex('testInsertManyGraphs'))
#    virtuoso_suite.addTest(TestStressVirtuosoIndex('testRandomLongGraphs'))
    virtuoso_suite.addTest(TestStressVirtuosoIndex('testCreateGraphs'))
    unittest.TextTestRunner(verbosity=2).run(virtuoso_suite)

#    unittest.main()

