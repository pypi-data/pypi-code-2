from beaker.container import MemoryNamespaceManager, AbstractDictionaryNSManager
from repoze.lru import LRUCache


class LRUDict(LRUCache):
    """ Wrapper to provide partial dict access
    """
    def __setitem__(self, key, value):
        return self.put(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return bool(self.get(key))

    def __delitem__(self, key):
        del self.data[key]

    def keys(self):
        return self.data.keys()


class MemoryLRUNamespaceManager(MemoryNamespaceManager):
    """ A memory namespace manager that return with LRU dicts backend
    """
    default_max_items = 10000

    def __init__(self, namespace, **kwargs):
        AbstractDictionaryNSManager.__init__(self, namespace)
        if kwargs.has_key('max_items'):
            max_items = kwargs['max_items']
        else:
            max_items = self.default_max_items

        def Factory():
            return LRUDict(int(max_items))

        self.dictionary = MemoryNamespaceManager.namespaces.get(
            self.namespace, Factory)
