"""
Author:
    Chen Xiaoyu <smallfish.xy@gmail.com>
    http://chenxiaoyu.org

Description:
    Wrapper For Key-Value Database (Memcached, Redis, TokyoTyrant ...)

Example:
    # test memcached
    >>> from pywrapper.kv import create_wrapper
    >>> w = create_wrapper('memcached', host='127.0.0.1', port=11211)
    >>> w.set("name", "smallfish")
    >>> print w.get("name")
    smallfish
    >>> w.update("name", "bigfish")
    >>> print w.get("name")
    bigfish
    >>> w.delete("name")
    >>> print w.get("name")
    None

    # test redis
    >>> w = create_wrapper('redis', host='127.0.0.1', port=6379, db=1)

    # test tokyotyrant
    >>> w = create_wrapper('tokyotyrant', host='127.0.0.1', port=1978)
"""

__VERSION__ = "0.1"

class UnknownWrapperException(Exception): pass

class BaseWrapper:
    pass

class TokyoTyrantWrapper(BaseWrapper):
    def __init__(self, **params):
        module = _import_module('memcache')
        host = params['host']
        port = params['port']
        self.conn = module.Client(["%s:%s" % (host, port)], debug=1)

    def get(self, key):
        return self.conn.get(key)

    def set(self, key, value):
        self.conn.set(key, value)

    def update(self, key, value):
        self.conn.set(key, value)

    def delete(self, key):
        self.conn.delete(key)

class MemcachedWrapper(BaseWrapper):
    def __init__(self, **params):
        module = _import_module('memcache')
        host = params['host']
        port = params['port']
        self.conn = module.Client(["%s:%s" % (host, port)], debug=1)

    def get(self, key):
        return self.conn.get(key)

    def set(self, key, value):
        self.conn.set(key, value)

    def update(self, key, value):
        self.conn.set(key, value)

    def delete(self, key):
        self.conn.delete(key)

class RedisWrapper(BaseWrapper):
    def __init__(self, **params):
        module = _import_module('redis')
        host = params['host']
        port = params['port']
        db   = params['db']
        self.conn = module.Redis(host=host, port=port, db=db)

    def get(self, key):
        return self.conn.get(key)

    def set(self, key, value):
        self.conn.set(key, value)

    def update(self, key, value):
        self.conn.set(key, value)

    def delete(self, key):
        self.conn.delete(key)

_wrappers = {}

def _register_wrapper(name, wrapper):
    _wrappers[name] = wrapper

_register_wrapper('memcached', MemcachedWrapper)
_register_wrapper('tokyotyrant', TokyoTyrantWrapper)
_register_wrapper('redis', RedisWrapper)

def _import_module(module_name):
    try:
        return __import__(module_name, None, None, ['x'])
    except ImportError:
        pass
    raise ImportError("Unable import " + module_name)

def create_wrapper(name, **params):
    if name in _wrappers:
        return _wrappers[name](**params)
    else:
        raise UnknownWrapperException, name
