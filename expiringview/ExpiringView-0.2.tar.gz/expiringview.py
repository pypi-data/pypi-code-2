
import collections
import time


class ExpiringView(collections.MutableMapping):
    '''Mapping class which gives key/value pairs an expiry time.
    
    Parameters:
        mapping: The mapping to wrap.
        maxage: The default maxage of pairs.
        on_expire: Function to call when a pair is expired
    
    '''
    
    def __init__(self, mapping, maxage=None, on_expire=None):
        self.mapping = mapping
        self.maxage = maxage
        if on_expire:
            self.on_expire = on_expire
    
    def on_expire(self, key, value):
        '''Default callback for expired pairs. Override.'''
        pass
        
    def collect_garbage(self):
        '''Purge all expired pairs.'''
        for x in self:
            pass
    
    # Everything from this point on is standard Mapping interfaces.
    # ------------------------------------------------------------------------
    
    def __setitem__(self, key, value):
        self.set(key, value)
    
    def _get(self, key):
        pair = self.mapping.get(key)
        if pair and pair[0] is not None and pair[0] < time.time():
            del self.mapping[key]
            self.on_expire(*pair)
            return None
        return pair
    
    
    def set(self, key, value, maxage=None):
        if maxage is None:
            maxage = self.maxage
        if maxage is None:
            expiry = None
        else:
            expiry = time.time() + maxage
        self.mapping[key] = (expiry, value)
    
    def setdefault(self, key, value, maxage=None):
        try:
            return self[key]
        except KeyError:
            self.set(key, value, maxage)
            return value
        
    def __getitem__(self, key):
        pair = self._get(key)
        if not pair:
            raise KeyError(key)
        return pair[1]
    
    def __delitem__(self, key):
        pair = self._get(key)
        del self.mapping[key]
        if expiry is not None and expiry < time.time():
            raise KeyError(key)
    
    def __iter__(self):
        for key in self.mapping.keys():
            pair = self._get(key)
            if pair:
                yield key
    
    def __len__(self):
        return len(self.mapping)
    
    def __getattr__(self, name):
        return getattr(self.mapping, name)
    


if __name__ == '__main__':

    def on_expire(*args):
        print 'expired', repr(args)
    x = ExpiringView({}, maxage=1, on_expire=on_expire)
    x['key'] = 'value'

    print x.items()
    print x['key']
    time.sleep(1)
    print x.items()
    print x['key']