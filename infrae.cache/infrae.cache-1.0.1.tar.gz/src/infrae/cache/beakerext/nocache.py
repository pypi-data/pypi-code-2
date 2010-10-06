from beaker.container import MemoryNamespaceManager, AbstractDictionaryNSManager


class NoCache(object):

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, item):
        pass

    def __contains__(self, key):
        pass

    def keys(self):
        return []

    def clear(self):
        pass


class NoCacheNamespaceManager(MemoryNamespaceManager):
    """
    No cache namespace manager used for testing.
    """
    def __init__(self, namespace, **kwargs):
        AbstractDictionaryNSManager.__init__(self, namespace)

        def Factory():
            return NoCache()

        self.dictionary = MemoryNamespaceManager.namespaces.get(
            self.namespace, Factory)
