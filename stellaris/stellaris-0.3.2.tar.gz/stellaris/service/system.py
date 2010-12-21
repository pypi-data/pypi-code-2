# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, simplejson, sys

from stellaris.store.exceptions import GraphNotFound, GraphAlreadyExists, Unauthorized, CollectionNotFound, GroupNotFound
from stellaris.index.exceptions import IndexNotFound
from stellaris.service.security import authorize
from stellaris.security import READ, READ_WRITE, ADMIN_READ_WRITE

from benri.app import WSGICollection
from benri.app.json import JSON_CONTENT_TYPE, json

from paste.httpexceptions import HTTPMultipleChoices, HTTPSeeOther, HTTPNotFound, HTTPBadRequest, HTTPConflict, HTTPInternalServerError, HTTPMethodNotAllowed, HTTPUnauthorized

log = logging.getLogger(__name__)

# the browser displays a set of sub-collections and graphs part of the current
# collection.
# By "expanding" a collection/graph the attributes are shown and the possibility
# to update/modify the collection/graph is given.
# By following the link of a collection, the sub-tree is shown
# By following the link of a graph, the actual RDF is retrieved

# how to list sub-collections of a collection?
# how to list graphs in a collection?
# -> store.collection_retrieve(<collection_name>)
# GET /system/collections/<collection_name>
# The following two classes are used by the client to retrieve data and update
# attributes

class SystemGraphs(WSGICollection):
    """
    The system graphs collection is used to update attributes for the graphs
    such as TTL or index type.
    """
    def __init__(self, store, prefix='/system/graphs/'):
        self.store = store

        if not prefix.endswith('/'):
            prefix += '/'

        self.__prefix = prefix
        WSGICollection.__init__(self, uri_prefix=prefix)

    def _graph_id(self, env):
        (_, args) = env['wsgiorg.routing_args']        
        graph_id = self._check_arg('id', args)
            
        # make sure graph id's starts with the root '/'
        if not graph_id.startswith('/'):
            graph_id = '/' + graph_id
    
        return graph_id

    # retrieves a json document with system information about the graph
    # ttl, index type, etc. 
    @authorize(access_type=READ)
    @json
    def retrieve(self, env, resp):
        graph_id = self._graph_id(env)
        
        try:
            g = self.store.retrieve(graph_id)
            resp('200 OK', [])
            return [{'ttl': g.ttl, 'graph-name': g.uri, 'version': g.version}]
        except GraphNotFound, e:
            raise HTTPNotFound('Graph: %s, not found' % str(graph_id))
        except Exception, e:
            raise HTTPInternalServerError(str(e) + str(type(e)))
            
    @authorize(access_type=ADMIN_READ_WRITE)
    @json
    def update(self, env, resp):
        graph_id = self._graph_id(env)
        
        json_obj = env['benri.json']
        
        try:
            ttl = float(json_obj['ttl'])
            self.store.graph_update_ttl(graph_id, ttl)
        except ValueError, e:
            raise HTTPBadRequest('TTL was not float or int.')
        except KeyError, e:
            raise HTTPBadRequest('ttl-key not part of the json request.')
        except Exception, e:
            raise HTTPInternalServerError(str(e) + str(type(e)))
                
        resp('200 OK', [])
        return []
        
class SystemCollections(WSGICollection):
    """
    Used to modify various properties of the collections such as the assigned
    groups.
    """

    def __init__(self, store, prefix='/system/collections/'):
        self.store = store

        if not prefix.endswith('/'):
            prefix += '/'

        self.__prefix = prefix
        WSGICollection.__init__(self, uri_prefix=prefix)

    def _graph_id(self, env):
        return self._collection_id(env)
        
    def _collection_id(self, env):
        (_, args) = env['wsgiorg.routing_args']        
        collection_id = self._check_arg('id', args)

        if collection_id == None:
            collection_id = '/'
                
        # make sure graph id's starts with the root '/'
        if not collection_id.startswith('/'):
            collection_id = '/' + collection_id
    
        return collection_id

    def list(self, env, resp):
        return self.retrieve(env, resp)
        
    @authorize(access_type=READ)    
    @json
    def retrieve(self, env, resp):
        collection_id = self._collection_id(env)

#        log.debug('Retrieving collection id: %s' % collection_id)
        try:
            collections, graphs = self.store.collection_retrieve(collection_id)
            resp('200 OK', [])
            return [{'graphs': graphs, 'collections': collections}]
        except CollectionNotFound, e:
            raise HTTPNotFound('Collection: %s, not found' % str(collection_id))
        except Exception, e:
            raise HTTPInternalServerError(str(e) + str(type(e)))

    @authorize(access_type=ADMIN_READ_WRITE)
    @json
    def update(self, env, resp):
        collection_id = self._collection_id(env)
        # group to associate with or remove
        json_req = env['benri.json']
        
        try:
            action = json_req['action']
            group = json_req['group']
        except KeyError, e:            
            raise HTTPBadRequest('Key missing in json request: %s.' % str(e))
            
        try:
            rights = json_req['rights']
        except KeyError, e:
            # default rights
            rights = 'read'
        
        rights_table = {'write': READ_WRITE,
                        'read': READ,
                        'admin': ADMIN_READ_WRITE}

        try:
            rights = rights_table[rights.lower()]                
        except KeyError, e:
            raise HTTPBadRequest('The requested access rights does not exist, %s. Please give one of the following %s.' % (rights, rights_table.keys()))
                        
        try:
            if action == 'add':
                self.store.group_add_to_collection(collection_id, group, access_rights=rights)
            elif action == 'remove':
                self.store.group_remove_from_collection(collection_id, group)
            
            resp('200 OK', [])
            return []
        except CollectionNotFound, e:
            raise HTTPNotFound('Collection: %s, not found' % str(collection_id))
        except GroupNotFound, e:
            raise HTTPNotFound('Collection: group %s, not found' % str(group))            
        except Exception, e:
            raise HTTPInternalServerError(str(e) + str(type(e)))

class SystemIndices(WSGICollection):
    """
    System information about the indices being used to index the data in the
    graph store. Also contains methods for triggering recovery etc.
    """

    def __init__(self, store, prefix='/system/indices/'):
        self.store = store

        if not prefix.endswith('/'):
            prefix += '/'

        self.__prefix = prefix
        WSGICollection.__init__(self, uri_prefix=prefix)

    def _index_id(self, env):
        (_, args) = env['wsgiorg.routing_args']        
        index_id = self._check_arg('id', args)

        # default index
        if index_id == None:
            index_id = 'query'

        return index_id

    @json
    def list(self, env, resp):
        resp('200 OK', [])
        return [self.store.query_indices()]

    @authorize(access_type=ADMIN_READ_WRITE)
    @json
    def update(self, env, resp):
        index_name = self._index_id(env)
        
        json_req = env['benri.json']
        
        try:
            if json_req['recover']:        
                self.store.recover(index_name)
            
            resp('200 OK', [])
            return ['Recovery of %s was sucessful.' % index_name]
        except IndexNotFound, e:
            raise HTTPNotFound('Index: %s, not found' % str(index_name))
        except KeyError, e:            
            raise HTTPBadRequest('Key missing in json request: %s.' % str(e))
        except Exception, e:
            raise HTTPInternalServerError(str(e) + str(type(e)))

                    
