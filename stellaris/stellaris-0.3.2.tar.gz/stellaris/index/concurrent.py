# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB
from __future__ import with_statement

from threading import Lock, Thread
from thread import get_ident as thread_id
from Queue import Queue, Empty

from stellaris.index import Index
from stellaris.index.exceptions import QueryTimedOut

class ConcurrentIndex(Index):
    """
    The concurrent index is used to ensure that consistent data is returned. 
    That is, any concurrent operations are serialized using a lock.
    """

    def __init__(self, index, num_query_threads=20, query_timeout=60.0):
        self.__lock = Lock()
        self.__index = index
        self.__query_timeout = query_timeout
        self.__num_query_threads = num_query_threads
         
#        self.__queues = {}
        self.__query_queue = Queue()
        self.__query_threads = []
        
        for i in range(self.__num_query_threads):
            self.__query_threads.append(Thread(target=self.query_worker))
        
        for t in self.__query_threads:
            t.start()
                        
    def query_worker(self):
        while True:
            try:
                q_msg = self.__query_queue.get(timeout=1.0)
                
                if q_msg == None:
                    # time to quit
                    break
                
                resp_q, query, format = q_msg
                
                fail = False
                
                try:
                    res = self.__index.query(query, format)
                except Exception, e:
                    fail = True
                    res = e
                
                resp_q.put((res, fail))
            except Empty,e:
                continue
        
    # both delete and replace will run in the main thread of the BackendIndex
    def delete(self, graph_uri):
        self.__index.delete(graph_uri)
            
    def replace(self, graph_uri, graph):
        self.__index.replace(graph_uri, graph)

    def query(self, query, format='xml', out_file=False):
        
        resp_q = Queue()
        self.__query_queue.put((resp_q, query, format))
        
        timeout = 1.0
        total_time = 0.0
        
        while total_time < self.__query_timeout:
            try:
                res = resp_q.get(timeout=timeout)    
                
                if res == None:
                    # stop any blocking tasks
                    break
                
                query_res, fail = res
                
                if fail:
                    raise query_res

                return query_res          
            except Empty, e:
                total_time += timeout

        raise QueryTimedOut('The query timed out after %s seconds' % self.__query_timeout)
        #self.__store.query(query, format=format)
        
    def close(self):
        # If the process is killed with -9 here it is fine, these threads
        # are only reading
        for i in range(self.__num_query_threads):
            self.__query_queue.put(None)

        for t in self.__query_threads:
            t.join()
            
if __name__ == '__main__':
    from stellaris.graph import Graph as SGraph
    from stellaris.index.native import MemoryIndex
    
    index = MemoryIndex() #datapath='/tmp/store/')
	
    g = SGraph('./tests/data/add.rdf', 'hello')
    index.replace('hello', g)
    index.replace('hello', g)
    index.delete(g.uri)
    
    try:
        print index.contexts[g.uri]
    except KeyError, e:
        pass
        
    cindex = ConcurrentIndex(index)
    
    cindex.replace('hello', g)
    q = """PREFIX exterms: <http://www.example.org/terms/>
                 SELECT ?date
                 WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . }"""

    print cindex.query(q)
    
    cindex.close()
