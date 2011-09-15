from google.appengine.api import memcache


class memoize(object):
    def __init__(self, key, time=3600 * 24 * 30):
        self.time = time
        self.key  = key

    def __call__(self, f):
        def func(*args, **kwargs):
            data = memcache.get(self.key)
            if data is not None:
                return data

            data = f(*args, **kwargs)
            memcache.set(self.key, data, self.time)
            return data

        func.func_name = f.func_name
        return func