# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import os

from paste.fileapp import _FileIter
from urlparse import urljoin
from tempfile import mkstemp
from xml.etree.ElementTree import iterparse, tostring as et_tostring
from cStringIO import StringIO

from stellaris.exceptions import ConfigAttributeMissing
from stellaris.store.exceptions import GraphNotFound
from stellaris.storemanager import StoreManager
from stellaris.indexmanager import IndexManager
from stellaris.graph import Graph, FileGraph
from stellaris.security import READ
                
class FrontendStore(object):
    """
    The FrontendStore provides the interface used directly by the WSGI-
    application serving the clients or by a wrapping store such as a 
    federation-layer and/or security.
    """
    
    def __init__(self, env):
        self._env = env

        try:
            stand_alone = env.config['service']['stand_alone']
            if stand_alone.lower() == 'true':
                stand_alone = True
            else:
                stand_alone = False
        except KeyError, e:
            raise ConfigAttributeMissing('service', str(e))

        self.__im = IndexManager(env, stand_alone=stand_alone)

        try:
            self.__sm = StoreManager(env, stand_alone=stand_alone)
        except:
            self.__im.stop()
            raise

        try:
            self.__spool_path = os.path.join(env.data_dir, 'spool')
            
            if not os.path.exists(self.__spool_path):
                os.mkdir(self.__spool_path)                
        except Exception, e:
            self._env.log.error('Could not create the spool-directory.')
            self.close()
            raise

        try:
            self.__baseuri = env.config['service']['baseuri']
        except KeyError, e:
            self.__baseuri = 'http://%s/' % env.config['server']['bind']

        try:
            self.graph_prefix = urljoin(self.__baseuri, env.service_prefix)
        except KeyError, e:
            self.graph_prefix = self.__baseuri

        # start recovery of all indices that should be recovered on
        # restart, i.e. in-memory indices
        for index in self.__im.memory_indices():
            self.recover(index)
            
    def recover(self, index_name, graph_prefix='/'):
        """
        Re-indexes all data in the indexes with the latest stored graph
        """
        def all_graphs(collection):
            cols, graphs = self.collection_retrieve(collection)
            for col in cols:
                new_graphs = all_graphs(col)
                graphs += new_graphs

            return graphs

        graphs = all_graphs(graph_prefix)

        self._env.log.info("Starting recovery of index '%s' with %s graphs." % (index_name, len(graphs)))

        for graph_name in graphs:
            g = self.retrieve(graph_name)
            self.__im.recover(index_name, [g])
        
        self._env.log.info("Recovered index '%s' with %s graphs." % (index_name, len(graphs)))
        
    def _dump_content(self, content, content_size):
        (fd, tmp_name) = mkstemp(dir=self.__spool_path)

        f = os.fdopen(fd, 'w+')
        for chunk in _FileIter(content, size=content_size, block_size=2**14):
            f.write(chunk)
        
        f.close()
        
        return tmp_name
                  
    def _parse_atomic_ops(self, name, content, content_size):
        # get an iterable
        context = iterparse(content, events=("start", "end"))

        XML_NS = "http://stellaris.zib.de/schema/atomic_operations#"
        xml_start = '<?xml version="1.0" encoding="UTF-8"?>'
        
        def qname(tag):
            return "{%s}%s" % (XML_NS, tag)
        
        clean_paths = []
        
        def create_op(op_type, elem):
            try:
                path = self._dump_content(StringIO('%s\n%s' % (xml_start, et_tostring(elem[0]))), -1)
                g = FileGraph(name, path, baseuri=self.__baseuri)
                ret = (op_type, g)
                clean_paths.append(path)
                return ret
            except KeyError, e:
                # there was no RDF data in the append
                pass                        
        
        # turn it into an iterator
        context = iter(context)

        # get the root element
        event, root = context.next()

        op_list = []
        
        for event, elem in context:
            if event == "end":
                if elem.tag == qname("atomic"):
                    root.clear()
                elif elem.tag == qname("append"):
                    op_list.append(create_op('append', elem))
                elif elem.tag == qname("remove"):
                    op_list.append(create_op('remove', elem))
                elif elem.tag == qname("update"):
                    op_list.append(create_op('update', elem))                

        # list with (op_type, Graph)
        return op_list, clean_paths
        
    def create(self, name, content, content_size=-1):
        """
        Creates a new graph using the given name and content.
        
        ``name`` - The name of the graph.
        ``content`` - file-like object containing the data for the graph
        ``content_size`` - Indicates the size in bytes of the content
        """
        
        path = self._dump_content(content, content_size)
        g = FileGraph(name, path, baseuri=self.graph_prefix)

        store = self.__sm.responsible_store(name)

        # do we need to know the location of the graph?        
        try:
            # create graph in the store
            ret_g = store.create(g)

            # add to the index
            self.__im.replace(g.uri, g)
            
            return g
        except Exception, e:
            self._env.log.error('Error when creating new graph: %s, %s:%s.' % (name, type(e), str(e)))
            raise
        finally:        
            # remove the temporary file independent of the operation result
            os.remove(path)
    
    def retrieve(self, name, version=None, cached_version=-1):
        """
        Retrieve a graph with the given name and version.
        
        ``name`` - Name of the graph.
        ``version`` - An int representing the graphs version, or None to get the
                      latest version.
        """
        
        store = self.__sm.responsible_store(name)
        return store.retrieve(name, version=version, cached_version=cached_version)

    def graph_replace(self, name, content, content_size=-1):
        path = self._dump_content(content, content_size)
        g = FileGraph(name, path, baseuri=self.graph_prefix)
        
        store = self.__sm.responsible_store(name)    

        try:
            new_g = store.graph_replace(name, g)
            self.__im.replace(g.uri, new_g)
        except Exception, e:
            self._env.log.error('Error when replacing graph: %s, %s:%s.' % (name, type(e), str(e)))
            raise
        finally:
            os.remove(path)
        
        return new_g

    def graph_update(self, name, content, content_size=-1):
        path = self._dump_content(content, content_size)
        g = FileGraph(name, path, baseuri=self.graph_prefix)
        
        store = self.__sm.responsible_store(name)

        try:
            new_g = store.graph_update(name, g)
            self.__im.replace(g.uri, new_g)
        finally:
            os.remove(path)
        
        return new_g
        
    def graph_append(self, name, content, content_size=-1):
        path = self._dump_content(content, content_size)
        g = FileGraph(name, path, baseuri=self.graph_prefix)
        
        store = self.__sm.responsible_store(name)    

        try:
            new_g = store.graph_append(name, g)
            self.__im.replace(g.uri, new_g)
        finally:
            os.remove(path)

        return new_g
        
    def graph_remove(self, name, content, content_size=-1):
        path = self._dump_content(content, content_size)
        g = FileGraph(name, path, baseuri=self.graph_prefix)
        
        store = self.__sm.responsible_store(name)    

        try:
            new_g = store.graph_remove(name, g)
            self.__im.replace(g.uri, new_g)
        finally:
            os.remove(path)

        return new_g

    def delete(self, name):
        g = Graph(name, None, baseuri=self.graph_prefix)
        store = self.__sm.responsible_store(name)    
        store.delete(name)
        self.__im.delete(g.uri)

    def exists(self, name, prefix_lookup=False):
        # this is analogous to the version store graph_exists, that cant
        # be used here though, since the graph can exist in any store.
        """
        Check if the current graph exists. If prefix_lookup is ``True``, each 
        prefix of the hierarchy in the name is checked for existence.
        Example: name = /a/b/c, then /a/b/c, /a/b, /a are checked in that order.
        Returns True if the name or any of the prefixes where found.
        
        Note: Even if this returns true, there may be another thread in the 
              system that removes the graph before it has a chance to be 
              retrieved.
              
        ``name`` - the (hierarchical) name of the graph
        ``prefix_lookup`` - indicates if an hierarchical prefix search should be
                            made. Default is ``False``
        """
       
        if not prefix_lookup:
            store = self.__sm.responsible_store(name)
            return store.exists(name)
                    
        name_spl = name.split('/')

        names = [name] + ['/'.join(name_spl[:i]) for i in range(-1,-len(name_spl)+1,-1)]

        for n in names:
            store = self.__sm.responsible_store(n)
            try:
                return store.exists(n)
            except:
                pass
                        
        raise GraphNotFound(name)

    def collection_retrieve(self, name):
        store = self.__sm.responsible_store(name)
        return store.collection_retrieve(name)
                                        
    def graph_update_ttl(self, name, ttl):
        store = self.__sm.responsible_store(name)
        store.graph_update_ttl(name, ttl)
    
    def query(self, index_name, query, format='xml', out_file=False):
        res = self.__im.query(index_name, query, format=format, out_file=out_file)

        # are the results most likely a path
        if out_file and res[0].startswith('/'):
            chunks = []
            
            for chunk in _FileIter(file(res), size=None, block_size=2**14):
                chunks.append(chunk)

            return ''.join(chunks)

        return res

    def query_indices(self):
        return self.__im.indices()
            
    def graph_atomic_operations(self, name, content, content_size=-1):
        path = self._dump_content(content, content_size)
        op_list, clean_graphs = self._parse_atomic_ops(name, file(path), content_size)
        os.remove(path)

        store = self.__sm.responsible_store(name)
        new_g = store.graph_atomic_operations(name, op_list)
        self.__im.replace(new_g.uri, new_g)
        
        # clean the temporary graph paths
        for clean_path in clean_graphs:
            os.remove(clean_path)
        
        return new_g

    # TODO: re-factor group management
    def group_list(self):
        store = self.__sm.responsible_store('doesnt matter')
        return store.group_list()
        
    def group_create(self, name, users=[]):
        store = self.__sm.responsible_store(name)
        return store.group_create(name, users=users)

    def group_retrieve(self, name):
        store = self.__sm.responsible_store(name)
        return store.group_retrieve(name)
                
    def group_update(self, name, users=[]):
        store = self.__sm.responsible_store(name)
        return store.group_update(name, users=users)

    def group_delete(self, name):
        store = self.__sm.responsible_store(name)
        return store.group_delete(name)

    def group_add_to_collection(self, collection_name, group_name, access_rights=READ):
        store = self.__sm.responsible_store(group_name)
        return store.group_add_to_collection(collection_name, group_name, access_rights=READ)

    def group_remove_from_collection(self, collection_name, group_name):
        store = self.__sm.responsible_store(group_name)
        return store.group_remove_from_collection(collection_name, group_name)

    def is_authorized(self, collection_name, user, access_type=READ):
        store = self.__sm.responsible_store(collection_name)
        return store.is_authorized(collection_name, user, access_type=access_type)

    def is_admin(self, user):
        store = self.__sm.responsible_store(user)
        return store.is_admin(user)
                        
    def close(self):
        self.__sm.stop()
        self.__im.stop()
