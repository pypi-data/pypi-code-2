from pyf.manager.path import DataPath, DataRoad
from pyf.warehouse.storage import WarehouseStorage

class DataManager(object):
    def __init__(self, max_items_per_shelve=500):
        # Config
        self.max_items_per_shelve = max_items_per_shelve
        
        # Internal data structure
        self.paths = dict()
        self.networks = dict()
        
        self.storages = dict()
        
    def get_path_output(self, path_name, consumer_no=None):
        path = self.get_path(path_name)
        
        if not consumer_no:
            if len(path.consumers) == 1:
                consumer_no = 0
            else:
                raise ValueError('Path has too much consumers. Please specify a consumer number.')
        
        consumer = path.consumers[consumer_no]
        
        return consumer
        
    def save_path_result(self, path_name, consumer_no=None, init_storage=True, storage_name=None):
        if init_storage:
            storage = self.create_named_storage(storage_name or path_name)
        else:
            storage = self.get_storage(storage_name or path_name)
        
        result_iter = self.get_path_output(path_name, consumer_no)
        
        storage.load(result_iter)
        
    def get_path(self, name):
        path = self.paths.get(name)
        if path is not None:
            return path
        else:
            raise ValueError('Path %s does not exist' % name)
        
    def get_storage(self, name):
        storage = self.storages.get(name)
        if storage is not None:
            return storage
        else:
            raise ValueError('Storage %s does not exist' % name)
        
    def get_network(self, name):
        path = self.networks.get(name)
        if path is not None:
            return path
        else:
            raise ValueError('Network %s does not exist' % name)
        
    def setup_path(self, name, values):
        path = self.get_path(name)
        path.setup(values)
        
    def setup_network(self, name, *args, **kwargs):
        path = self.get_network(name)
        path.initialize(*args, **kwargs)
        
#    def get_chained_path(self, *path_names):
#        root_node = dict(content=None, children=list())
#        
#        current_node = root_node
#        for path_name in path_names:
#            path = self.get_path(path_name)
#            current_node['content'] = path
#            next_node = dict()
#            current_node['children'] = list()
#            current_node = next_node
#            
#        return DataPath(dict(content=paths))
        
    def add_path(self, name, path):
        self.paths[name] = path
        
    def add_network(self, name, network):
        self.networks[name] = network
        
    def create_named_storage(self, name, index_key=None):
        storage = WarehouseStorage(max_items_per_shelve=self.max_items_per_shelve,
                                   index_key=index_key)
        
        self.storages[name] = storage
        
        return storage
        
    def clean(self):
        for storage in self.storages.values():
            storage.clean()
