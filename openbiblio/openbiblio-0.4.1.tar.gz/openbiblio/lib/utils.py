from contextlib import contextmanager
from copy import copy
from ordf.term import Literal, Node, URIRef

def coerce_uri(x):
    if not isinstance(x, URIRef):
        if isinstance(x, Node):
            raise TypeError(x, type(x), "must be URIRef or a type other than Node")
        x = URIRef(x)
    return x

def coerce_literal(x):
    if not isinstance(x, Literal):
        if isinstance(x, Node):
            raise TypeError(x, type(x), "must be Literal or a type other than Node")
        x = Literal(x)
    return x

@contextmanager
def flockdb(filename, flag="r"):
    """
    A helper for multiprocess-safe access to some shelf. Use it
    like this:

    >>> with flockdb("mydb") as db:
    ...    print db[key]
    ...

    The flag argument is passed through to shelve and is interpreted
    by this function in the following way: if the flag is "r" -- the default --
    the lock that is acquired is a shared lock. If the flag is something
    else, the lock that is acquired is exclusive.
    """
    import fcntl, os, shelve
    try:
        os.stat(filename)
    except OSError:
        db = shelve.open(filename, "c", 0600)
        db.close()
        
    if flag == "r":
        locktype = fcntl.LOCK_SH
    else:
        locktype = fcntl.LOCK_EX
        
    fp = open(filename, "r")
    fcntl.flock(fp.fileno(), locktype)

    try:
        db = shelve.open(filename, flag)
    except:
        fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
        fp.close()
        raise

    yield db

    db.close()
    fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
    fp.close()

class private_property(property):
    def __init__(self, name, **kw):
        self.name = name
        super(private_property, self).__init__(self._get, self._set, self._del)
        if "default" in kw:
            self.default = kw["default"]
    def _set(self, obj, v):
        private = obj.__dict__.setdefault("__private__", {})
        private[self.name] = v
    def _get(self, obj):
        private = obj.__dict__.get("__private__", {})
        try:
            return private[self.name]
        except KeyError:
            if hasattr(self, "default"):
                return copy(self.default)
            raise AttributeError("%s has no attribute %s" % (repr(obj), self.name))
    def _del(self, obj):
        private = obj.__dict__.get("__private__", {})
        try:
            del private[self.name]
        except KeyError:
            if hasattr(self, "default"):
                return
            raise AttributeError("%s has no attribute %s" % (repr(obj), self.name))
