# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import os, simplejson

from urlparse import urljoin
from xml.etree import ElementTree as ET
from benri.client import Client as BenriClient, CollectionClient
from cStringIO import StringIO
from urllib import urlencode

from stellaris.client.parsers import SPARQLResults

MIME = {'json': 'application/json',
        'sparql': 'application/x-www-form-urlencoded',
        'sparql_results_xml': 'application/sparql-results+xml',
        'sparql_results_json': 'application/sparql-results+json'}
         
JSON_CONTENT_TYPE = 'application/json'
SPARQL_POST_CONTENT_TYPE = 'application/x-www-form-urlencoded'
SPARQL_XML_RESULTS = "application/sparql-results+xml"

class GraphClient(BenriClient):
    # TODO: add stuff for authentication/authorization using cookies  
    def __init__(self, service_url, base_path=None, prefix='/', key=None, cert=None, user=None, password=None):
        BenriClient.__init__(self, service_url, base_path=base_path, key=key, cert=cert, user=user, password=password)

        self.__graphs = CollectionClient(self, prefix=prefix)
#        self.__acls = CollectionClient(self, self._client, prefix='/admin/acls/')
#        self.__lifetime = CollectionClient(self, self._client, prefix='/admin/lifetime/')

    def _atomic_ops_to_xml(self, ops):
        NS = 'http://stellaris.zib.de/schema/atomic_operations#'
        
        _ns_elem = lambda name: '{%s}%s' % (NS, name)

        root = ET.Element(_ns_elem("atomic"))
        
        for op_type, file_name in ops:
            
            op = ET.SubElement(root, _ns_elem(op_type))
            op.append(ET.XML(''.join([l for l in file(file_name)])))

        # wrap it in an ElementTree instance, and save as XML
        return ET.tostring(root)
        
    def create(self, graph_name, data, mimetype):
        """
        Creates a new graph with the given name.
        
        ``graph_name`` - name of the graph
        ``data`` - a string or a file-like object
        ``mimetype`` - type of the content in data
        """
        return self.__graphs.create(data, name=graph_name, mimetype=mimetype)

    def retrieve(self, graph_name, version=None):
        qs = ''
        if version:
            qs = 'version=%s' % str(int(version))
            
        return self.__graphs.retrieve(graph_name, query_string=qs)

    def update(self, graph_name, data, mimetype):
        # replaces the existing data with a completely new graph
        return self.__graphs.update(graph_name, data, mimetype=mimetype)
    
    def delete(self, graph_name):
        return self.__graphs.delete(graph_name)

    def _graph_modify(self, graph_name, data, mimetype, op=''):
        qs = ''            
        return self.__graphs.update(graph_name, data, mimetype=mimetype, noun=op, query_string=qs)
                
    def graph_replace(self, graph_name, data, mimetype):
        return self._graph_modify(graph_name, data, mimetype)

    def graph_update(self, graph_name, data, mimetype):
        return self._graph_modify(graph_name, data, mimetype, op='update')

    def graph_remove(self, graph_name, data, mimetype):
        return self._graph_modify(graph_name, data, mimetype, op='remove')

    def graph_append(self, graph_name, data, mimetype):
        return self._graph_modify(graph_name, data, mimetype, op='append')
        
    def graph_atomic_operations(self, graph_name, ops):
        """
        Send a single request that will atomically execute multiple requests.
        
        ``graph_name`` - Name of the graph on which the operations will execute
        ``ops`` - A list of (operation_type, path)-tuples. Operation type is
                  either 'append', 'update' or 'remove'. Path is a file-system
                  path to a graph serialized with RDF/XML.
        """
        xml = self._atomic_ops_to_xml(ops)
        mimetype = 'application/xml'
        return self.__graphs.update(graph_name, xml, mimetype=mimetype)

    def graph_update_ttl(self, graph_name, ttl):
        return self.__graphs.update(graph_name, simplejson.dumps({'ttl':ttl}), mimetype=MIME['json'])

class SystemClient(BenriClient):
    # by sharing a base-path it is possible to use the same security credentials
    def __init__(self, service_url, base_path=None, prefix='/', key=None, cert=None, user=None, password=None):
        BenriClient.__init__(self, service_url, base_path=base_path, key=key, cert=cert, user=user, password=password)
        
        self.__data_client = CollectionClient(self, prefix=prefix)
        
        sys_graphs_prefix = urljoin(prefix, 'system/graphs/')
        self.__graphs = CollectionClient(self, prefix=sys_graphs_prefix)

        collections_prefix = urljoin(prefix, 'system/collections/')
        self.__collections = CollectionClient(self, prefix=collections_prefix)

        groups_prefix = urljoin(prefix, 'system/groups/')
        self.__groups = CollectionClient(self, prefix=groups_prefix)

        indices_prefix = urljoin(prefix, 'system/indices/')
        self.__indices = CollectionClient(self, prefix=indices_prefix)
        
    def group_list(self):
        stat, json_resp = self.__groups.retrieve('')
        try:
            return simplejson.loads(json_resp)
        except ValueError, e:
            return json_resp

    def group_create(self, group_name, users=[]):
        json_obj = {'users': users}
        
        return self.__groups.create(simplejson.dumps(json_obj), name=group_name, mimetype=MIME['json'])

    def group_retrieve(self, group_name):
        stat, json_resp = self.__groups.retrieve(group_name)
        json_obj = simplejson.loads(json_resp)
        return json_obj['users']

    def group_update(self, group_name, users=[]):
        json_obj = {'users': users}
        stat, resp = self.__groups.update(group_name, simplejson.dumps(json_obj), mimetype=MIME['json'])
        return stat, resp
        
    def group_delete(self, group_name):
        return self.__groups.delete(group_name)

    def collection_add_group(self, collection_name, group_name, access_rights="read"):
        json_obj = {'action': 'add', 'group': group_name, 'rights': access_rights}
        stat, resp = self.__collections.update(collection_name, simplejson.dumps(json_obj), mimetype=MIME['json'])
        return stat, resp

    def collection_remove_group(self, collection_name, group_name):
        json_obj = {'action': 'remove', 'group': group_name}
        stat, resp = self.__collections.update(collection_name, simplejson.dumps(json_obj), mimetype=MIME['json'])
        return stat, resp

    def collection_retrieve(self, collection_name, recursive=False):
        
        def get_collection(collection):
            stat, json_resp = self.__collections.retrieve(collection)
            try:
                json_obj = simplejson.loads(json_resp)
            except ValueError, e:
                raise ValueError('Failed to decode json data: %s\nOriginal request: %s' % (str(e), json_resp))
            return (json_obj['collections'], json_obj['graphs'])
        
        # get all graphs in the collection
        def all_graphs(collection):
            cols, graphs = self.collection_retrieve(collection)
            all_cols = cols[:]
            for col in cols:
                new_cols, new_graphs = all_graphs(col)
                graphs += new_graphs
                all_cols += new_cols
            
            return all_cols, graphs
        
        if recursive:
            return all_graphs(collection_name)
        
        return get_collection(collection_name)

    def collection_delete(self, collection_name, recursive=False):
        """
        Delete all graphs within a collection. Set recursive to `True` in order
        to delete all sub-collections as well.
        
        ``collection_name`` - name of the collection to delete
        ``recursive`` - flag indicating if the delete should be recursive, 
                        defaults to `False`.
        """        
        cols, graphs = self.collection_retrieve(collection_name, recursive=recursive)

        for g in graphs:
            try:
                self.__data_client.delete(g)
            except Exception, e:
                raise
                    
    def graph_retrieve(self, graph_name):
        stat, json_resp = self.__graphs.retrieve(graph_name)
        json_obj = simplejson.loads(json_resp)
        return json_obj

    def graph_update(self, graph_name, attrs):
        stat, resp = self.__graphs.update(graph_name, simplejson.dumps(attrs), mimetype=MIME['json'])
        return stat, resp

    def indices(self):
        stat, resp = self.__indices.retrieve('', accepts=MIME['json'])
        return simplejson.loads(resp)

    def recover_index(self, index_name):
        stat, resp = self.__indices.update('/%s' % index_name, simplejson.dumps({'recover': True}), mimetype=MIME['json'])
        
class QueryClient(BenriClient):
    # by sharing a base-path it is possible to use the same security credentials
    def __init__(self, service_url, index_name='query', base_path=None, prefix='/', key=None, cert=None, user=None, password=None):
        BenriClient.__init__(self, service_url, base_path=base_path, key=key, cert=cert, user=user, password=password)
        
        query_prefix = os.path.join(prefix, 'query/')
        self.__endpoint_uri = urljoin(service_url, os.path.join(query_prefix, index_name))
#        self.__query = BenriClient(self, prefix=urljoin(query_prefix, index_name))

    def query(self, query, format='xml'):
        # create maps to POST
        body = {'query': query, 'format': format}
        
        headers = {'Content-Type': MIME['sparql'],
                   'Accept': "%s" % MIME['sparql_results_%s' %format]}
        stat, resp = self.post(self.__endpoint_uri, urlencode(body), headers=headers)
        return resp

    def indices(self):
        headers = {'Accept': MIME['json']}       
        stat, resp = self.get(os.path.dirname(self.__endpoint_uri), headers=headers)
        return simplejson.loads(resp)
