# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

from urlparse import urljoin

class Index(object):

    def __init__(self, baseuri="http://stellaris.gac-grid.org/"):
        """
        ``baseuri``   - Prefix used for graph names
        """
        self.baseuri = baseuri
            
    def delete(self, graph_name):
        """
        Delete the graph with the given name from the index.
           
        ``graph_name`` - delete the graph with this name
        """                
    
    def replace(self, graph_uri, graph):
        """
        If the given graph is stored in the index already, it is replaced with
        the latest version. Otherwise, the graph is inserted.
           
        ``graph`` - replace the currently indexed graph with this graph
        """

    def query(self, query, format="xml"):
        """Execute a `query` and returns the result as a string formatted 
           according to `format`. The query is SPARQL string. The return string
           is either in the standard SPARQL XML format or JSON.
           
           @param query - The query as a SPARQL string
           @param format - indicates the output format ('xml' or 'json')           
        """
                
    def clear(self):
        """Removes all stored data. Use with caution!"""

    def close(self):
        """Closes an index."""

from stellaris.index.concurrent import ConcurrentIndex
