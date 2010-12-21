# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import os, logging, sys

from stellaris.index.backend import BackendIndex, setup_index
from stellaris.index.exceptions import IndexNotFound

from random import randint as rand

class IndexManager(object):

    def __init__(self, env, stand_alone=False):
        
        default_index = None
        
        self.__indices = {}
        
        self.__in_memory_indices = []

        for section, index_name in self._extract_indices(env.config):
            if env.config[section].get('default', 'False').lower() == 'true':
                default_index = index_name

            if env.config[section].get('persistent', 'true').lower() == 'false':
                self.__in_memory_indices.append(index_name)

            env.config[section]['section'] = section
            cfg = env.config[section]
            cfg['section'] = section
            cfg['baseuri'] = env.config['service']['baseuri']
            cfg['name'] = index_name
            cfg['log_type'] = env.config['logging']['type']
            cfg['log_level'] = env.config['logging']['level']
            cfg['log_file'] = os.path.join(env.log_dir, 'index_%s.log' % index_name)
            cfg['data_dir'] = env.data_dir
            cfg['etc_dir'] = env.etc_dir
            
            # create the indices
            # The BackendIndex-class will detect index type and use the
            # given configuration parameters. If the initialization fails,
            # the manager will stop all started threads and raise an
            # exception.
            try:
                if stand_alone:
                    self.__indices[index_name] = BackendIndex(cfg, cancel_timeout=600.0, log=env.log)
                else:
                    self.__indices[index_name] = setup_index(cfg)
            except Exception, e:
                env.log.error("Creating index failed for %s:%s: %s" %(index_name, section, str(e)))
                self.stop()
                raise

        env.log.info("Registered indices %s " % (str(self.__indices.keys())))
        self._env = env

        if not default_index:
            default_index = self.__indices.keys()[0]
            
        self.__indices['query'] = self.__indices[default_index]

    def memory_indices(self):
        return self.__in_memory_indices

    def _extract_indices(self, config):
        """
        Retrieves the different indices and their config-parameters using the
        input config.
        """
        
        indices = []
        
        for section in config.keys():
            if section.startswith('index:'):
                index_name = section[section.find(':')+1:]
                indices.append((section, index_name))
        
        return indices

    def recover(self, index_name, graphs):
        if not index_name in self.__indices:
            raise IndexNotFound(index_name)
        
        for g in graphs:
            self.__indices[index_name].replace(g.uri, g)
      
    def indices(self):
        """
        Returns a list of index names.
        """
        return self.__indices.keys()

    def replace(self, graph_uri, graph):
        for index_name in self.__indices:
            self.__indices[index_name].replace(graph_uri, graph)

    def delete(self, graph_uri):
        for index_name in self.__indices:
            self.__indices[index_name].delete(graph_uri)
                    
    def query(self, index_name, query, format='xml', out_file=False):
        # rand(0, len(self.__indices)-1)
        if not index_name in self.__indices:
            raise IndexNotFound(index_name)
                 
        return self.__indices[index_name].query(query, format=format, out_file=out_file)

    def stop(self):
        for index_name in self.__indices:
            self.__indices[index_name].close()

if __name__ == '__main__':
    from stellaris.graph import Graph as SGraph
    
    config = {'index:test':{'type':'rdflib-memory', 
                            'baseuri':'http://example.org/'}}
    config['index:foo'] = {'type':'rdflib-memory', 
                           'baseuri':'http://foo.org/'}
                            
    im = IndexManager(config)

    g = SGraph('./tests/data/add.rdf', 'hello')

    im.replace('hello', g)
    q = """PREFIX exterms: <http://www.example.org/terms/>
           SELECT ?date
           WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . }"""

    print im.query('test', q)
    print im.query('foo', q)
    
    im.stop()
