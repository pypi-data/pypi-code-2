# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import os, urllib, time, sys

from rdflib import plugin
from rdflib import URIRef, Literal, BNode, Namespace
from rdflib import RDF
from rdflib import sparql
from rdflib.store import Store
from rdflib.Graph import ConjunctiveGraph, Graph, ReadOnlyGraphAggregate
from rdflib.sparql import sparqlGraph
from rdflib.sparql.bison import Parse
from rdflib.sparql.bison.Query import Query
#from rdflib.sparql.bison.SPARQLEvaluate import Evaluate
from rdflib.syntax.parsers import Parser
from urlparse import urljoin

from datetime import datetime, timedelta

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import stellaris
from stellaris import RDF, XSD, STELLARIS
from stellaris.serialize import serializeXML
from stellaris.graph import TYPE_RDFLIB
from stellaris.index import Index
from stellaris.index.exceptions import IndexReplaceFailed, IndexDeleteFailed, IndexQueryFailed

class RDFLibIndex(Index):

    def __init__(self, baseuri="http://stellaris.gac-grid.org/", log=None):
        Index.__init__(self, baseuri)
        
        # mapping from graph name to the indexed graph, called context in RDFLib 
        self.contexts = {}
        
        # non-opened store
        self.store = None
        self.log = log
       
    def init_store(self):
        self.store.bind("stellaris", STELLARIS)

        # initialize contexts        
        for g in self.store.contexts():
            self.contexts[g.identifier] = g

        if self.log:
            self.log.info("Initializing store complete.")
           
    def close(self):
        self.store.close()
#        self.gc.stop()

    def delete(self, graph_uri):
        """
        Deletes the graph with the give ``graph_uri`` from the index.
        
        ``graph_uri`` - uri of the graph to delete.
        """
            
        if not graph_uri in self.contexts:
            # graph is not stored, just return
            return

        # remove from the store and then remove from the local contexts
        self.store.remove((None, None, None), context=self.contexts[graph_uri])
        del self.contexts[graph_uri]

        self.store.commit()

    def replace(self, graph_uri, graph):
        """
        Overwrites the graph stored at ``graph_uri`` with the given ``graph``.
        
        ``graph_uri`` - overwrite graph with this name
        ``graph`` - use this graph, ``stellaris.graph.Graph``, to overwrite the 
                    graph.
        """

        try:
            self.delete(graph_uri)

            g = Graph(self.store, identifier=graph.uri)
            self.contexts[graph.uri] = g
            
            if graph.graph_type != TYPE_RDFLIB:
                g.parse(StringIO(graph.serialized))
            else:
                self.contexts[graph.uri] += graph.graph
                
            self.store.commit()
        except Exception, e:
            raise IndexReplaceFailed(e)
       
    def query(self, query, format="xml", out_file=False):
        """
        Exectues the given query over the index.
        """
        try:
            # assume that if the query is neither of str or unicode
            if isinstance(query, unicode) or isinstance(query, str):
                query = Parse(query)
            elif not isinstance(query, Query):
                raise SyntaxError("Query is not a valid query object")
                
            dt = time.time()            
            graphs = query.query.dataSets
            query_graphs = []
             
            if graphs == []:
                # query all indexed graphs
                query_graphs = self.contexts.values()
            else:
                local_graphs = []
                remote_graphs = []
                
                for graph_uri in graphs:
                    try:
                        local_graphs.append(self.contexts[str(graph_uri)])
                    except KeyError, e:
                        # TODO: this could be cached and done with a worker pool
                        #       in the case of many graphs
                        g = Graph()
                        try:
                            remote_graphs.append(g.parse(graph_uri))
                        # probably some HTTP error
                        # if not all data can be downloaded, the query will fail
                        except Exception, e:
                            raise Exception('Graph %s could not be retrieved or parsed.' % graph_uri)
                
                query_graphs = local_graphs + remote_graphs
            
            g = Graph()
            if query_graphs:
                g = ReadOnlyGraphAggregate(query_graphs)
            
            # reset the query data sets since we have already taken care of them
            query.query.dataSets = []
            results = g.query(query)
            if self.log:
                self.log.debug("Query execution took %s seconds" % (str(time.time()-dt)))
        except Exception, e:
            raise IndexQueryFailed(str(e))
        
        #log.debug('query results: %s', results.serialize(format='python'))
        if format == 'xml':
            return serializeXML(results)
        
        return results.serialize(format=format)

    def close(self):
        self.store.close()
 
    def __delitem__(self, graph_uri):
        """Alias for delete."""
        self.store.delete(graph_uri)
                
    def __setitem__(self, graph_uri, graph):
        """Alias for replace."""
        self.replace(graph_uri, graph)
        
    def __contains__(self, graph_uri):
        return graph_uri in self.contexts

class MySQLIndex(RDFLibIndex):

    def __init__(self, user='rdflib', password='rdflib', host='localhost', port=3306, db='rdflib', baseuri="http://stellaris.gac-grid.org/", log=None):
        RDFLibIndex.__init__(self, baseuri=baseuri)
        config = 'user=%s,password=%s,host=%s,port=%s,db=%s' % (user, password, host, str(port), db)
        
        # annoyingly, if configuration is not none, the db is opened
        # without allowing the user to specify if it should be created
        # or not
        self.store = plugin.get('MySQL', Store)(configuration=None, identifier=self.baseuri)
        self.store.open(config, create=True)
        self.init_store()
        self.log = log
        
class MemoryIndex(RDFLibIndex):

    def __init__(self, baseuri="http://stellaris.gac-grid.org/", log=None):
        RDFLibIndex.__init__(self, baseuri=baseuri)
        self.store = plugin.get('IOMemory',Store)(identifier=self.baseuri)
        self.log = log
        self.init_store()

class BerkeleyDBIndex(RDFLibIndex):

    def __init__(self, datapath, baseuri="http://stellaris.gac-grid.org/", log=None):
        RDFLibIndex.__init__(self, baseuri=baseuri)
    
        if not os.path.exists(datapath):
            os.mkdir(datapath)
        
        self.datapath = datapath
        self.store = plugin.get('Sleepycat',Store)(configuration=self.datapath, identifier=self.baseuri)
        self.store.open(self.datapath, create=True)
        self.log = log
        self.init_store()
        
if __name__ == '__main__':
#    import hotshot, psyco

    from stellaris.graph import FileGraph
    store = MemoryIndex() #datapath='/tmp/store/')

    graph_name = 'http://test.org/hello'
    g = FileGraph(graph_name, './tests/data/add.rdf')
    store.replace(graph_name, g)

    graph_name = 'http://test.org/hello2'
    g = FileGraph(graph_name, './tests/data/update.rdf')
    store.replace(graph_name, g)

    graph_name = 'http://test.org/hello3'
    g = FileGraph(graph_name, './tests/data/replace.rdf')
    store.replace(graph_name, g)

    query = """PREFIX exterms: <http://www.example.org/terms/>
                   PREFIX dc: <http://purl.org/dc/elements/1.1/>
                   SELECT ?date ?lang
                   #FROM <http://stellaris.zib.de:24000/context/test>
                   #FROM NAMED <http://test.org/hello>
                   #FROM NAMED <http://test.org/hello2>                   
                   WHERE { <http://www.example.org/index.html> exterms:creation-date ?date .
                           <http://www.example.org/index.html> dc:language ?lang . }
                """

    print store.contexts
    print store.query(query, format='json')
    
    store.replace(graph_name, g)
    store.delete(g.uri)
    
    try:
        print store.contexts[g.uri]
    except KeyError, e:
        pass
        
    store.close()
    
#    psyco.full()
#    prof = hotshot.Profile("hotshot_query_stats_psyco")
#    prof.runcall(main)
#    prof.close()
#    main()
