# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import time, logging, re, os, simplejson

from urlparse import urljoin
from paste.request import parse_formvars
from paste.fileapp import _FileIter, FileApp
from paste.util.mimeparse import best_match

from benri.app import WSGIApp
from benri.app.json import json, JSON_CONTENT_TYPE

from paste.httpexceptions import HTTPMultipleChoices, HTTPSeeOther, HTTPNotFound, HTTPBadRequest, HTTPConflict, HTTPInternalServerError, HTTPMethodNotAllowed, HTTPUnauthorized

from stellaris.index.exceptions import IndexNotFound

class Query(WSGIApp):

    def __init__(self, store, static_path, default_index='query', prefix='/query/', log=None):
        self.store = store
        self.__prefix = prefix
        self.__static_path = static_path
        self.__default_index = default_index
        self.routes = {'/query[/]': dict(GET=self.list),
                       '/query/{id:any}': dict(POST=self.query, GET=self.query)}
 
        self.log = log
                              
        WSGIApp.__init__(self)

    def _rewrite_query(self, query):
        """
        Re-writes the query by replacing any FROM NAMED that contains a 
        collection with the set of graphs in the collection.
        
        Ex:
        FROM NAMED </a/>
        =>
        FROM NAMED </a/a>
        FROM NAMED </a/b>
        """
        
        # TODO: Filter out collections which the user is not authorized for
        def replace_collection(re_match):
            uri = re_match.group('uri')
            # check if this is a collection
            if uri.endswith('/') and uri.startswith(self.store.graph_prefix):
                
                sub_c, graphs = self.store.collection_retrieve('/' + uri.replace(self.store.graph_prefix, ''))
                # assume that internal graph names start with '/'
                return ''.join(['FROM NAMED <%s>\n' % urljoin(self.store.graph_prefix, g[1:]) for g in graphs])
            
            # use from, since this is likely to work better with most
            # index backends
            return 'FROM NAMED <%s>\n' % uri
                
        # find all rows with from named
        p = re.compile(r'(from named <(?P<uri>.*)>)', re.IGNORECASE)
        new_q = p.sub(replace_collection, query)
        return new_q
        
    # GET /query/
    # Returns a list of the available indicies
    @json
    def list(self, env, resp):
        # content-neg, if best match is not JSON, serve up HTML/XML
        
        match = best_match([JSON_CONTENT_TYPE, 'application/xml', 'text/xml', 'application/xhtml+xml', 'text/html'], env['HTTP_ACCEPT'])
        
        if match == JSON_CONTENT_TYPE:
            resp('200 OK', [])
            return [self.store.query_indices()]
        
        app = FileApp(os.path.join(self.__static_path, 'html/query.html'))
        return app(env, resp)

    def query(self, env, resp):
        (_, args) = env['wsgiorg.routing_args']
        index_name = args.get('id', self.__default_index)

        queryargs = parse_formvars(env, include_get_vars=True)

        if not 'query' in queryargs:
           resp("400 BAD REQUEST", [('Content-Type', "text/plain")])
           return ["No query specified in request."]
        
        query = queryargs['query']
            
        format = 'xml'
        if 'format' in queryargs:
            format = queryargs['format']

        valid_formats = ['xml', 'json']

        if not format in valid_formats:
           resp("400 BAD REQUEST", [('Content-Type', "text/plain")])
           return ["Format " + format + " is not valid. Available formats: " + str(valid_formats)]
                
        res = ""
        
        new_query = self._rewrite_query(query)
        
        if self.log:
            self.log.debug('Executing query: %s' % new_query)
            
        try:
            dt = time.time()        
            res = self.store.query(index_name, new_query, format=format, out_file=True)
            if self.log:
                self.log.info('Query execution time: %s', time.time()-dt)

            if not res:
                raise Exception('Query failed with empty response: %s' % res)
        except IndexNotFound, e:
            resp("404 Not Found", [('Content-Type', "text/plain")])
            return["Index with name '%s' not available." % index_name]
        except Exception, e:
            if self.log:
                self.log.error('%s:%s' %(str(type(e)), str(e)))
            resp("500 Internal Server Error", [('Content-Type', "text/plain")])
            return['%s' %(str(e))]
        
        # if the client knows the sparql format return the correct mime-type,
        # otherwise assume that it is something that can handle xml
        if format=='json' or ('HTTP_ACCEPT' in env and 'application/sparql-results+' + format in env['HTTP_ACCEPT']):
            # ensures that the json output is in UTF-8 according to the standard
            # shouldn't this be ensured by rdflib?
            res = res.encode('utf-8')
            headers = [('Content-Length', str(len(res)))]
            resp("200 OK", headers + [('Content-Type', "application/sparql-results+" + format)])
        else:
            headers = [('Content-Length', str(len(res)))]            
            resp("200 OK", headers + [('Content-Type', "application/xml")])
        
        return [res]        
        
    # GET /query/{id:any}
    # This executes the query for the given index,
    # For SPARQL-enabled indices, the protocol is defined at:
    # http://www.w3.org/TR/rdf-sparql-protocol/
    def retrieve(self, env, resp):
        return self.query(env, resp)     

    # POST /query/{id:any}
    # This 
    def create(self, env, resp):
        return self.query(env, resp)

    # TODO: use this to update properties for the index
    def update(self, env, resp):
        pass

    # TODO: deletion of index
    def delete(self, env, resp):
        pass
