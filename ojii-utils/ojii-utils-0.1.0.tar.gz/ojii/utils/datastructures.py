class NULL: pass


class AutoDictionary(dict):
    """
    ad = AutoDictionary(list)
    ad['hello'].append('world')
    => ad = {'hello': ['world']}
    """
    def __init__(self, factory=NULL, *args, **kwargs):
        assert callable(factory), "AutoDictionary requires the `factory` argument."
        self._factory = factory
        
    def __getitem__(self, item):
        if item not in self:
            self[item] = self._factory()
        return super(AutoDictionary, self).__getitem__(item)
    
    
class TypedDictionary(dict):
    """
    A (rather slow) dictionary to make handling keys which could be provided in
    different types but should always be converted to a single type before using.
    
    td = TypedDictionary(converter=str)
    td[1] = 'one']
    td[1] == td['1']
    => True
    """
    def __init__(self, converter=NULL, *args, **kwargs):
        assert callable(converter), "TypedDictionary requires the `converter` argument."
        self._converter = converter
        
    def __setitem__(self, key, value):
        super(TypedDictionary, self).__setitem__(self._converter(key), value)
        
    def __getitem__(self, key):
        super(TypedDictionary, self).__getitem__(self._converter(key))
        
    def __contains__(self, key):
        super(TypedDictionary, self).__contains__(self._converter(key))