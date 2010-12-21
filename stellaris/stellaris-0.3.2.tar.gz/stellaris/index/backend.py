# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import stellaris.index.backend, os

from stellaris.worker import Worker
from stellaris.index import ConcurrentIndex
from stellaris.exceptions import ConfigAttributeMissing
from stellaris.utils import create_logger

def _load_dummy(config, section, log):
    from stellaris.index import Index
    try:
        return ConcurrentIndex(Index(baseuri=config['baseuri']))
    except KeyError, e:
        raise ConfigAttributeMissing(section, str(e))
    except Exception, e:
        raise e
    
def _load_virtuoso(config, section, log):
    from stellaris.index.virtuoso import VirtuosoIndex
    try:
#        return VirtuosoIndex(config['rdfsink_url'], config['sparql_url'], config['user'], config['password'], baseuri=config['baseuri'], log=log)
        return VirtuosoIndex(config['install_prefix'], os.path.join(config['etc_dir'], 'virtuoso.ini_tmpl'), config['sparql_url'], config['data_dir'], log=log)
    except KeyError, e:
        raise ConfigAttributeMissing(section, str(e))
    except Exception, e:
        raise e
        
def _load_sesame(config, section, log):
    from stellaris.index.sesame import SesameIndex
    try:
        return SesameIndex(config['sesame_url'], baseuri=config['baseuri'], log=log)
    except KeyError, e:
        raise ConfigAttributeMissing(section, str(e))
    except Exception, e:
        raise e
        
def _load_rdflib_memory(config, section, log):
    from stellaris.index.native import MemoryIndex
    try:
        return ConcurrentIndex(MemoryIndex(baseuri=config['baseuri'], log=log))
    except KeyError, e:
        raise ConfigAttributeMissing(section, e)
    except Exception,e:
        raise e
        
def _load_rdflib_bdb(config, section, log):
    from stellaris.index.native import BerkeleyDBIndex
    try:
        return ConcurrentIndex(BerkeleyDBIndex(config['db_path'], baseuri=config['baseuri'], log=log))
    except KeyError, e:
        raise ConfigAttributeMissing(section, e)
    except Exception,e:
        raise e

def _load_rdflib_mysql(config, section, log):
    from stellaris.index.native import MySQLIndex
    try:
        return ConcurrentIndex(MySQLDBIndex(user=config['user'], password=config['password'], host=config['host'], port=config['port'], db=config['db_name'], baseuri=config['baseuri'], log=log))
    except KeyError, e:
        raise ConfigAttributeMissing(section, e)
    except Exception,e:
        raise e
        
#index_to_class = {}
#index_to_class['rdflib-memory'] = '

def setup_index(config):
    try:
        index_type = config['type'].replace('-','_')
    except KeyError, e:
        raise ConfigAttributeMissing(config['section'], e)
    
    log = create_logger('index-%s' % config['name'], log_type=config['log_type'], log_level=config['log_level'], log_file=config['log_file'])
    
    f = getattr(stellaris.index.backend, '_load_%s' % index_type)
    # failure here is fatal
    return f(config, config['section'], log)

class BackendIndex(Worker):

    def __init__(self, config, cancel_timeout=60.0, queue_timeout=1.0, log=None):
        Worker.__init__(self, cancel_timeout=cancel_timeout, queue_timeout=queue_timeout, log=log)
        self.setName('IndexBackend')
        self.configure(config)
                
    def setup(self, config):
        self.__index = setup_index(config)

    def teardown(self):
        self.__index.close()

    def dispatch(self, msg):
        f = getattr(self.__index, msg.method)
        return f(*msg.args, **msg.kwargs)

    def close(self):
        # alias for stop
        self.stop()

if __name__ == '__main__':
    from stellaris.graph import Graph as SGraph
#    from stellaris.index.native import MemoryIndex
    
    g = SGraph('./tests/data/add.rdf', 'hello')
    config = {'type': 'rdflib-memory', 
              'baseuri': 'http://example.com/',
              'section': 'index:test'}
    w = BackendIndex(config)
    
    w.replace('hello', g)
    q = """PREFIX exterms: <http://www.example.org/terms/>
                 SELECT ?date
                 WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . }"""

    print w.query(q)
    
    w.stop()        
