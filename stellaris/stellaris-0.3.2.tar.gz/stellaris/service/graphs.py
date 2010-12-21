# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, simplejson, os, sys

from stellaris.store.exceptions import GraphNotFound, GraphAlreadyExists, Unauthorized
from stellaris.service.security import authorize
from stellaris.security import AUTHENTICATED_USER, PUBLIC_USER, READ, READ_WRITE

from uuid import uuid4 as uuid

from benri.app import WSGICollection
from benri.app.json import JSON_CONTENT_TYPE
from urlparse import urlunparse, urljoin
from mimetypes import types_map as mimetype
from cStringIO import StringIO

from paste.fileapp import _FileIter, FileApp
from paste.httpexceptions import HTTPMultipleChoices, HTTPSeeOther, HTTPNotFound, HTTPBadRequest, HTTPConflict, HTTPInternalServerError, HTTPMethodNotAllowed, HTTPUnauthorized
from paste.request import parse_querystring

log = logging.getLogger('stellaris')

def localgraph(app):
    def wrapped_app(cls, env, resp):
        graph_id = cls._graph_id(env)
        local_g = None
        
        try:
            local_g = cls.store.exists(graph_id, prefix_lookup=True)
        except GraphNotFound, e:
            pass
            
        if local_g:
            env['stellaris.local_graph'] = local_g
        return app(cls, env, resp)
    
    return wrapped_app

class Graphs(WSGICollection):
    """
    A collection of graphs.
    """
    def __init__(self, store, static_path, prefix='/graphs/', log=None):
        self.store = store
        self.__prefix = prefix
        self.__static_path = static_path
        self.log = log

        if self.log:
            log.debug('Graphs at prefix %s' % (prefix))
        # note that this is shared non-thread-safe state
        # the worst thing that can happen is that a read concurrent
        # to a write gets a stale version. Optimistic concurrency
        # based operations must be passed to the store which serializes
        # operations.
        self._cache = {}
        WSGICollection.__init__(self, uri_prefix=prefix)

    # GET /graphs/
    def list(self, env, resp):
        # this returns an html page used for browsing the graph-collections
        app = FileApp(os.path.join(self.__static_path, 'html/graphs.html'))
        return app(env, resp)

    def _graph_id(self, env):
        if env['REQUEST_METHOD'] == 'POST':
        # POST is for when a new graph is created
        
        # the slug contains the value recommended by the client to
        # create the URI where the file will be accessible via
            graph_id = env.get('HTTP_SLUG', '/')

            # graphs with no slug will get a unique temporary name
            if graph_id == '/':
                graph_id = '/temporary/' + str(uuid())

            if graph_id.endswith('/'):
                graph_id = graph_id + str(uuid())
        else:
            try:
                # preference goes to the local graph, this can be a prefix of the
                # original request
                return env['stellaris.local_graph']
            except KeyError, e:
                (_, args) = env['wsgiorg.routing_args']        
                graph_id = self._check_arg('id', args)
            
        # make sure graph id's starts with the root '/'
        if not graph_id.startswith('/'):
            graph_id = '/' + graph_id
    
        return graph_id
        
    def _check_format(self, content_type):            
        if 'rdf+xml' in content_type:
            return 'rdf'
        elif 'rdf+n3' in content_type:
            return 'n3'
        elif 'application/xml' == content_type:
            return 'xml'
        elif content_type == JSON_CONTENT_TYPE:
            return 'json'
        else:
            raise HTTPBadRequest('Content-Type, %s, is not valid. Must be either rdf/xml or rdf/n3.' % (content_type))

    # POST /graphs/
    
    # Creates a new graph in the collection
    # Defines a random name when the 'Slug'-header is not specified
    
    # If the 'Slug'-header is a collection, i.e. ends with '/' a random
    # name in that collection is used. Note that this should be the same
    # as the baseuri for the graph, the RDF-data can then have relative URI:s.
    # The absolute URI will then be network-accessible.

    # default TTL for any new graph is infinite, if the client wants to 
    # change the ttl it must be done explicitly by modifying the graph
    # in the /admin/graphs/-collection.
    
    # The 'Content-Type'-header must be part of the request, indicating
    # what format the graph has. This can be any of the following:
    # 'application/rdf+xml'
    # 'application/rdf+n3'
    # 'text/rdf+n3'
    
    @authorize(access_type=READ_WRITE)
    def create(self, env, resp):
        graph_id = self._graph_id(env)        
        content_size = self._check_content_size(env)
        #format = self._check_format(self._check_content_type(env))

        try:
            self.store.create(graph_id, env['wsgi.input'], content_size=content_size)
        except GraphAlreadyExists, e:
            raise HTTPConflict("Graph: %s, already exists." % (str(e)))
        except Exception, e:
            raise HTTPInternalServerError(str(e))
        
        # remove leading slash from graph_id to get correct behaviour for 
        # urljoin
        location = urljoin(urlunparse((env['wsgi.url_scheme'], env['HTTP_HOST'], os.path.join(env['PATH_INFO'], self.__prefix), '','','')), graph_id[1:])
        
        headers = [('Location', location)]
        resp('201 Created', headers)
        return []
        
    # GET /graphs/{id:any}
    # returns the RDF-graph corresponding to the id in the URI
    # If the id ends with a '/', assume it is a collection and return
    # JSON or HTML listing all sub-collections and sub-graphs.
    
    # When 'recursive=<depth>' is part of the query string, the listing
    # contain all sub-collections and sub-graphs to that depth. A depth of
    # 0 is default, while -1 indicates that the depth is infinite.
    # This is useful to for example create a backup-utility which retrieve
    # all graphs under a collection or for implementing recursive delete.
    
    @localgraph
    @authorize(access_type=READ)
#    @Federation
#    @authorized
    def retrieve(self, env, resp):
    
        graph_id = self._graph_id(env)
        
#        content_type = self._check_accept(env)
        queryargs = dict(parse_querystring(env))
        
        try:
            version = int(queryargs['version'])
        except ValueError, e:
            raise HTTPBadRequest('The given version, %s, is not an integer.' % queryargs['version'])
        except KeyError, e:
            version = None
            
        # version == -1 or not there means that the latest version
        # should be used.

        cached_version = int(env.get('HTTP_IF_NONE_MATCH', -1))
        # if the version given by the user is the same as
        # the version in the graph cache, return not modified
        try:
            if cached_version == self._cache[graph_id]:
                resp('304 Not Modified', [('ETag', str(cached_version))])
                return []
        except KeyError, e:
            pass

        try:
            g = self.store.retrieve(graph_id, version=version)
            headers = [('Content-Type', mimetype['.rdf'])]
            headers.append(('Content-Length', str(len(g.serialized))))

            # the client must always check with the server if a newer version
            # is available. This still requires a round-trip to the DB,
            # alternatively, this class could maintain a hashmap with 
            # graph-name and version to remove this overhead.
            headers.append(('ETag', str(g.version)))
            headers.append(('Cache-Control', 'private, must-revalidate, max-age=0'))
            # populate the cache
            self._cache[graph_id] = g.version

            resp('200 OK', headers)
            return StringIO(g.serialized)
        except GraphNotFound, e:
            raise HTTPNotFound('Graph: %s, not found' % str(graph_id))
        except Exception, e:
            raise HTTPInternalServerError(str(e) + str(type(e)))

    def _xml_update(self, graph_id, env):
        content_size = self._check_content_size(env)
            
        return self.store.graph_atomic_operations(graph_id, env['wsgi.input'], content_size=content_size)

    def _read_json(self, content, content_size):
        chunks = []
        
        for chunk in _FileIter(content, size=content_size, block_size=2**14):
            chunks.append(chunk)
        
        return simplejson.loads(''.join(chunks))
    
    def _json_update(self, graph_id, env):
        content_size  = self._check_content_size(env)        
        json_obj = self._read_json(env['wsgi.input'], content_size)
        
        try:
            ttl = float(json_obj['ttl'])
        except ValueError, e:
            raise HTTPBadRequest('TTL was not float or int.')
        except KeyError, e:
            raise HTTPBadRequest('ttl-key not part of the json request.')
            
        self.store.graph_update_ttl(graph_id, ttl)
    
    def _rdf_xml_update(self, graph_id, env):
        (_, args) = env['wsgiorg.routing_args']
        queryargs = dict(parse_querystring(env))        
        # default to replacing the graph entirely
        noun = args.get('noun', 'replace') 
        
        # try if query args specify the modification
        if noun == None or noun == 'replace':
            noun = queryargs.get('modification', 'replace')
            
        content_size = self._check_content_size(env)
        if noun == None:
            noun = 'replace'

        try:            
            func = getattr(self.store, 'graph_%s' % noun)
        except AttributeError, e:
            raise HTTPBadRequest('%s is not a valid graph operation.' % noun)
        
        func(graph_id, env['wsgi.input'], content_size=content_size)
            
    def _error_update(self, graph_id, env):
        raise HTTPBadRequest('Content-type: %s, of the uploaded data is not supported' % env['CONTENT_TYPE'])

    # PUT /graphs/{id:any};{noun:any}
    # Modifies the graph with the given id. The noun indicates in what way
    # the graph should be modified. 'add', 'update', 'remove' are allowed 
    # values.
    @authorize(access_type=READ_WRITE)    
    def update(self, env, resp):
        (_, args) = env['wsgiorg.routing_args']

        graph_id = self._graph_id(env)

        # its ok if content size is not set if there is a query string
        content_type = self._check_content_type(env) #self._check_format(self._check_content_type(env))
        
        format = content_type[content_type.find('/')+1:]
        format = format.replace('+','_')
        
        try:
            # remove graph from the cache, even if this fails
            try:
                del self._cache[graph_id]
            except KeyError, e:
                pass

            f = getattr(self, '_%s_update' % format, self._error_update)
            f(graph_id, env)                                           
        except GraphNotFound, e:
            raise HTTPNotFound('Graph: %s, not found' % str(graph_id))
        except HTTPBadRequest, e:
            raise e
        except Exception, e:
            raise HTTPInternalServerError(str(e))        

        resp('200 OK', [])
        return []
        
    # DELETE /graphs/{id:any}
    # deletes the graph from the system
    @authorize(access_type=READ_WRITE)    
    def delete(self, env, resp):
        graph_id = self._graph_id(env)

        try:
            # remove graph from the cache, even if this fails
            try:
                del self._cache[graph_id]
            except KeyError, e:
                pass

            self.store.delete(graph_id)
        except GraphNotFound, e:
            raise HTTPNotFound('Graph: %s, not found' % str(graph_id))
        except Exception, e:
            raise HTTPInternalServerError(str(e))        

        resp('200 OK', [])
        return []
