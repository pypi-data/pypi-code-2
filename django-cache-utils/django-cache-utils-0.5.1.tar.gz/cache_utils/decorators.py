#coding: utf-8
from django.core.cache import cache
from django.utils.functional import wraps
from cache_utils.utils import get_args_string

def cached(timeout, group=None):
    """ Caching decorator. Can be applied to function, method or classmethod.
        Supports bulk O(1) cache invalidation and meaningful cache keys.
        Takes function's arguments and full name into account while
        constructing cache key.
    """

    backend_kwargs = {'group': group} if group else {}

    def _cached(func):

        # check if decorator is applied to function, method or classmethod
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        static = method = False
        if len(argnames) > 0:
            if argnames[0] == 'self' or argnames[0] == 'cls':
                method = True
                if argnames[0] == 'cls':
                    static = True

        @wraps(func)
        def wrapper(*args, **kwargs):

            # introspect function's or method's full name
            if method:
                if static:
                    class_name = args[0].__name__
                else:
                    class_name = args[0].__class__.__name__
                func_name = ".".join([func.__module__, class_name, func.__name__])
                key_args = args[1:]
            else:
                func_name = ".".join([func.__module__, func.__name__])
                key_args = args

            # construct the key using function's (method's) full name and
            # passed parameters
            key = '[cached]%s(%s)' % (func_name, get_args_string(key_args, kwargs))

            # try to get the value from cache
            value = cache.get(key, **backend_kwargs)

            # in case of cache miss recalculate the value and put it to the cache
            if value is None:
                value = func(*args, **kwargs)
                cache.set(key, value, timeout, **backend_kwargs)
            return value
        return wrapper
    return _cached
