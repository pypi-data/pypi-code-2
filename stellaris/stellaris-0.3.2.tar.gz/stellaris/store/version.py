# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, os

from base64 import urlsafe_b64decode as decode, urlsafe_b64encode as encode

#from benri.db import DB, Index
#from benri.security import AuthorizationService

#from stellaris.store import Store
from stellaris.store.exceptions import GraphAlreadyExists, GraphNotFound
from stellaris.graph import VersionedGraph
from stellaris.store.cache import Cache, CacheEntryNotFound

log = logging.getLogger('stellaris')

class VersionFileStore(object):

    def __init__(self, path):
        self.__base_path = path

        if not os.path.exists(self.__base_path):
            os.mkdir(self.__base_path)
        
        # use + as version sep since it is not part of the urlsafe 
        # base64 encoding
        self.__version_sep = '+'
        # sets how many characters in a directory
        # the directories are there for load-balancing the files stored in
        # the filesystem. The FS usually get problems with over 10K files in
        # a single dir.
        self.__dir_length = 2
        self.__dir_depth = 3
        
        # use a dict for now,
        # TODO: implement LRU or some other caching-policy
        self.__graph_cache = Cache(size=1000)

    def graph_path(self, name):
        """
        Creates a physical storage path for the graph. The created path joined
        with the name is returned.
        """
        enc_name = encode(name)
        
        # create a directory hierarchy to avoid having too many files or
        # sub-directories in a single directory
        
        def create_hierarchy(name, depth):
            l = []
            for i in range(depth):
                pos = i*self.__dir_length
                l.append(name[pos:pos+self.__dir_length])
            
            # adds a directory for the graph name which will contain
            # all versions
            l.append(name)
            create_path = os.path.join(self.__base_path, os.sep.join(l))
            # os.makedirs(os.path.join(self.__base_path, os.sep.join(l)))
            return create_path

        graph_path = create_hierarchy(enc_name, self.__dir_depth) 
        return os.path.join(graph_path, enc_name)
        
    def create(self, graph):
        # Create a stored graph from the graph
        # use the name to derive the graph path
        path = self.graph_path(graph.name)
        
        # if the graph exists already, it cannot be created
        if os.path.exists(path):
            raise GraphAlreadyExists()

        new_graph = VersionedGraph(path)
        new_graph.graph = graph

        
        # store the graph in the cache
        self.__graph_cache[graph.name] = VersionedGraph(path)
        return self.__graph_cache[graph.name]

    def retrieve(self, name):
        try:
            return self.__graph_cache[name]
        except CacheEntryNotFound, e:
            # not in the cache, check disk
            pass

        # get the graph_path for the name
        path = self.graph_path(name)
        
        if not os.path.exists(path):
            raise GraphNotFound(name)
        
        # create a new versioned graph and return it
        g = VersionedGraph(path)
        
        # touch the cache
        self.__graph_cache[g.name] = g
        
        return g

    def replace(self, name, graph, commit=True):
        """
        Replaces all triples in the current graph with the triples from the
        given graph.
                
        ``name`` - the name of the local graph
        ``graph`` - update the local graph with this graph
        ``commit`` - True if the changes should be commit directly to the 
                     backend. False does not persistently store the changes.
        """
        local_g = self.retrieve(name)
        local_g.replace(graph, commit=commit)
        
        return local_g
        
    def update(self, name, graph, commit=True):
        """
        Updates the local graph with the triples from graph. Returns the updated
        graph.
        
        ``name`` - the name of the local graph
        ``graph`` - update the local graph with this graph
        ``commit`` - True if the changes should be commit directly to the 
                     backend. False does not persistently store the changes.
        """
        local_g = self.retrieve(name)
        local_g.update(graph, commit=commit)
        
        return local_g

    def append(self, name, graph, commit=True):
        """
        Append triples to the local graph from the given graph. Returns the 
        updated graph.
        
        ``name`` - the name of the local graph
        ``graph`` - append triples from this graph
        ``commit`` - True if the changes should be commit directly to the 
                     backend. False does not persistently store the changes.
        """
        local_g = self.retrieve(name)
        local_g.append(graph, commit=commit)
        
        return local_g

    def remove(self, name, graph, commit=True):
        """
        Remove triples from the local graph that matches the triples from graph. 
        Returns the updated graph.
        
        ``name`` - the name of the local graph
        ``graph`` - graph with triples to remove
        ``commit`` - True if the changes should be commit directly to the 
                     backend. False does not persistently store the changes.
        """
        local_g = self.retrieve(name)
        local_g.remove(graph, commit=commit)
        
        return local_g

    def delete(self, name): 
        """
        Deletes the graph from the persistent storage.
        """
        # this is done by changing the link of the existing graph,
        # thus, it is still possible to retrieve old versions
        g = self.retrieve(name)
        
        g.delete()
        
        # remove from the cache
        try:
            del self.__graph_cache[name]
        except KeyError, e:
            pass

    def rollback(self, name):
        """
        Destroy all non-committed changes.
        """
        # it is sufficient to clean the graph from the cache since an 
        # uncommitted graph only exist in memory. Next time it is read into
        # the cache, it will be fetched from disk according to the latest
        # version of the graph.
        
        # the user of the atomic functionality must make sure that no 
        # intermediary operations are committing. The version number is only
        # increased for a commit.
        
        try:
            del self.__graph_cache[name]
        except KeyError,e:
            pass
    
    def __contains__(self, name):
        """
        Returns True if the store contain a graph with the given name.
        """
         # get the graph_path for the name
        path = self.graph_path(name)
        
        if os.path.exists(path):
            return True
        
        return False
            
    def commit(self, name):
        """
        Commit any non-committed state in a graph.
        """
        g = self.retrieve(name)
        g.commit()
        return g
        
class VersionStore(object):

    def __init__(self, config):
        #Store.__init__(self, config)
        self.__vfs = VersionFileStore(config['store']['version_store_path'])

    def create_graph(self, graph):
        return self.__vfs.create(graph)
        #return Store.create_graph(self, graph)

    def retrieve_graph(self, name):
        return self.__vfs.retrieve(name)

    def replace_graph(self, name, graph):
        return self.__vfs.replace(name, graph)
        
    def update_graph(self, name, graph):
        return self.__vfs.update(name, graph)

    def append_graph(self, name, graph):
        return self.__vfs.append(name, graph)

    def remove_graph(self, name, graph):
        return self.__vfs.remove(name, graph)

    def delete_graph(self, name):
        self.__vfs.delete(name)

    # this executes multiple operations related to a single graph for a single
    # message version, the graph version is only increased by one from these
    # changes
    def graph_atomic_operations(self, name, op_list):
        """
        Executes a list of operations on the graph with the given name. Returns
        the committed graph.
        
        ``name`` - name of the graph
        ``op_list`` - list of (op_type, input_graph)-tuples, where op_type is
                      either 'append', 'remove' or 'update' and input_graph is
                      the graph to be used for the operation.
        """
        g = self.__vfs.retrieve(name)
        
        for (op_type, input_graph) in op_list:
            try:
                f = getattr(self.__vfs, op_type)
                f(name, input_graph, commit=False)
            except AttributeError, e:
                self.__vfs.rollback(name)
                raise
        
        return self.__vfs.commit(name)

    def graph_exists(self, name, prefix_lookup=False):
        """
        Check if the current graph exists. If prefix_lookup is ``True``, each 
        prefix of the hierarchy in the name is checked for existence.
        Example: name = /a/b/c, then /a/b/c, /a/b, /a are checked in that order.
        Returns the graph if any of the prefixes where found, otherwise 
        ``None``.
        
        Note: Even if this returns the prefix, there may be another thread in 
              the system that removes the graph before it has a chance to be 
              retrieved.
              
        ``name`` - the (hierarchical) name of the graph
        ``prefix_lookup`` - indicates if an hierarchical prefix search should be
                            made. Default is ``False``
        """
        
        if not prefix_lookup:
            if name in self.__vfs:
                return name
            return None
            
        
        # this is to make sure to get all the names to check, the generated list
        # leaves out the top value of /a/b/c
        if not name.endswith('/'):
            name += '/'
            
        if not name.startswith('/'):
            name = '/' + name
            
        name_spl = name.split('/')

        names = ['/'.join(name_spl[:i]) for i in range(-1,-len(name_spl)+1,-1)]

        for n in names:
            if n in self.__vfs:
                return n
        
        return None
        
    def close(self):
        pass
        #Store.close(self)
