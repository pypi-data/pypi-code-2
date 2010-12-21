# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import os, urllib, time, sys, logging

from urllib import urlencode
from urlparse import urljoin

from datetime import datetime, timedelta
from benri.client.client import Client, NotFound

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import stellaris
from stellaris import RDF, XSD, STELLARIS
from stellaris.serialize import serializeXML
from stellaris.index import Index
from stellaris.index.exceptions import IndexReplaceFailed, IndexDeleteFailed, IndexQueryFailed, IndexNotAvailable

log = logging.getLogger(__name__)

class SesameClient(object):

    def __init__(self, sesame_repo_url, log=None):
        self.__client = Client(sesame_repo_url)
        
        try:
            self.__client.get('/size')
        except NotFound, e:
            raise IndexNotAvailable('Could not find the Sesame repository at URL: %s' % sesame_repo_url)

        self.log = log
        
    def replace_context(self, context, data):
        headers = {}
        headers['Content-Type'] = 'application/rdf+xml'
        
        self.__client.put('/statements?%s' % urlencode({'context': "<%s>" %context}), data, headers=headers)

    def delete_context(self, context):
        data = """<?xml version="1.0" encoding="UTF-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"></rdf:RDF>"""

        # remove all data stored at the context by inserting an empty graph
        self.replace_context(context, data)
        
    def query(self, query, format='xml', out_file=False):
        headers = {}
        headers['Accept'] = 'application/sparql-results+xml'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        data = urlencode({'query': query})
        stat, resp = self.__client.post('/', data, headers=headers)
        return resp

class SesameIndex(Index):

    def __init__(self, sesame_repository_url, baseuri="http://stellaris.gac-grid.org/", log=None):
        """
        Uses a Sesame repository for indexing graphs.
        
        ``sesame_repository_url`` - full URL to the sesame repository. Ex:
                                    http://example.org/openrdf-sesame/repo/
        """
        Index.__init__(self, baseuri)
        
        # mapping from graph name to the indexed graph 
        self.contexts = {}
        
        # non-opened store
        self.__client = SesameClient(sesame_repository_url, log=log)
        self.log = log
       
    def init_store(self):
        pass
#        self.store.bind("stellaris", STELLARIS)

        # initialize contexts        
#        for g in self.store.contexts():
#            self.contexts[g.identifier] = g

        if self.log:
            self.log.debug("Initializing store complete.")
           
    def close(self):
        pass
#        self.gc.stop()

    def delete(self, graph_uri):
        """
        Deletes the graph with the given ``graph_uri`` from the index.
        
        ``graph_uri`` - uri of the graph to delete.
        """
            
        if not graph_uri in self.contexts:
            # graph is not stored, just return
            return

        # remove from the store and then remove from the local contexts
        self.__client.delete_context(context=self.contexts[graph_uri])
        del self.contexts[graph_uri]
            
    def replace(self, graph_uri, graph):
        """
        Overwrites the graph stored at ``graph_uri`` with the given ``graph``.
        
        ``graph_uri`` - overwrite graph with this name
        ``graph`` - use this graph to overwrite the graph
        """

        try:
            self.__client.replace_context(graph_uri, graph.serialized)
            self.contexts[graph_uri] = graph_uri
        except Exception, e:
            raise IndexReplaceFailed(e)

    def query(self, query, format="xml"):
        """
        Exectues the given query over the index.
        """
        return self.__client.query(query, format=format)
        
    def close(self):
        pass
 
    def __delitem__(self, graph_uri):
        """Alias for delete."""
        self.store.delete(graph_uri)
                
    def __setitem__(self, graph_uri, graph):
        """Alias for replace."""
        self.replace(graph_uri, graph)
        
    def __contains__(self, graph_uri):
        return graph_uri in self.contexts

if __name__ == '__main__':
#    import hotshot, psyco

    from stellaris.graph import FileGraph
    sesame_url = 'http://localhost:8180/openrdf-sesame/repositories/stellaris/'
    store = SesameIndex(sesame_url) #datapath='/tmp/store/')

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
