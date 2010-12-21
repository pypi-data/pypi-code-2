# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import os, time, stellaris

from stellaris.store.rdbms import RDBMSStore
from stellaris.exceptions import ConfigAttributeMissing
from stellaris.worker import Worker
from stellaris.utils import create_logger

class RequestTimedOut(Exception): pass

def _load_rdbms(config, log):
    try:
        db_uri = config['db_uri']
    except KeyError, e:
        db_uri = 'sqlite:///' + config['db_path'] + '/store.db'

    backup_path = config.get('backup_path', None)
    backup_interval = int(config.get('backup_interval', -1))
    gc_interval = int(config.get('gc_interval', -1))    

    return RDBMSStore(db_uri, gc_interval=gc_interval, backup_path=backup_path, backup_interval=backup_interval, log=log)

### TODO: this is crazy...
def dispatch(func):
    def decorated(*args, **kwargs):
        if func.__name__.startswith('graph_'):
            # this modifies a graph, execute a graph-modifying operation and 
            # return store.update(g)
            
            # first argument is always the graph's name
            graph_name = args[0]
            
            g = self.__store.retrieve(graph_name)
            
            # filter out the graph_ part since that is not in the method-name
            method = func.__name__.replace('graph_', '')
            f = getattr(g, method)
            # the graph_name should not be part of the call
            f(*msg.args[1:], **msg.kwargs)

            self.__store.update(g)

            # prepare the graph for transfer so that pickling it is ok
            g.prepare_transfer()
            # return the modified graph
            return g
        
        # else try to execute the method using the store    
        f = getattr(self.__store, func.func_name)
        return func(*args,**kwargs)
    return decorated

class BackendStore(object):
    def __init__(self, config, log=None):
        try:
            store_type = config['type'].replace('-','_')
        except KeyError, e:
            # defaults to rdbms
            store_type = 'rdbms'
        
        store = getattr(stellaris.store.backend, '_load_%s' % store_type)(config, log)
        store.open()
        self.__store = store

    def __getattr__(self, name):
        def func(*args, **kwargs):
            if name.startswith('graph_'):
                graph_name = args[0]
                g = self.__store.retrieve(graph_name)
                method = name.replace('graph_', '')
                f_modify = getattr(g, method)
                f_modify(*args[1:], **kwargs)
                self.__store.update(g)
                g.prepare_transfer()
                return g

            f = getattr(self.__store, name)
            return f(*args, **kwargs)

        return func

    def close(self):
        self.__store.close()
            
class BackendStoreStandAlone(Worker):
    """
    The backend store is called directly by the frontend. Each ``BackendStore``
    runs in a separate process.
    """

    def __init__(self, config, cancel_timeout=60.0, queue_timeout=1.0, log=None):
        Worker.__init__(self, cancel_timeout=cancel_timeout, queue_timeout=queue_timeout, log=log)
        self.setName('StoreBackend')        
        self.configure(config)
        self.log = log

    def setup(self, config):
        try:
            store_type = config['type'].replace('-','_')
        except KeyError, e:
            # defaults to rdbms
            store_type = 'rdbms'

        if not self.log:
            self.log = create_logger(log_id='store', log_type=config['log_type'], log_level=config['log_level'], log_file=config.get('log_file', None))
            
        self.log.debug("Starting store worker: [%s]" % str(config))
        
        self.__store = getattr(stellaris.store.backend, '_load_%s' % store_type)(config, self.log)
        self.__store.open()
        
        self.log.debug("Store setup complete: %s" %(str(self.__store)))
        
    def teardown(self):
        self.__store.close()

    def dispatch(self, msg):
        if msg.method.startswith('graph_'):
            # this modifies a graph, execute a graph-modifying operation and 
            # return store.update(g)
            
            # first argument is always the graph's name
            graph_name = msg.args[0]
            
            g = self.__store.retrieve(graph_name)
            
            # filter out the graph_ part since that is not in the method-name
            method = msg.method.replace('graph_', '')
            f = getattr(g, method)
            # the graph_name should not be part of the call
            f(*msg.args[1:], **msg.kwargs)

            self.__store.update(g)

            # prepare the graph for transfer so that pickling it is ok
            g.prepare_transfer()
            # return the modified graph
            return g
        
        # else try to execute the method using the store    
        f = getattr(self.__store, msg.method)
        return f(*msg.args, **msg.kwargs)

    def close(self):
        self.stop()
        
if __name__ == '__main__':
    from tempfile import mkdtemp
    from shutil import rmtree
    from stellaris.graph import FileGraph

    db_path = mkdtemp()        
    config = {'store':{'db_uri': 'sqlite:///%s' % (db_path + '/tmp.db')}}        

    try:
        store = BackendStore(config)
        #store.start()
        g = FileGraph('test', './tests/data/add.rdf')
        #time.sleep(3.0)
        store.create(g)
        
        print store.retrieve('test').serialized
        
        store.graph_append('test', FileGraph('blub', './tests/data/append.rdf'))
        
        print store.retrieve('test').serialized
    except Exception, e:
        print "couldnt start store: ", e
    
    store.stop()
    
    rmtree(db_path)

