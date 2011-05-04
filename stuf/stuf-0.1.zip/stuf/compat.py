'''compatibility stuf'''

try:
    from thread import get_ident as _get_ident
except ImportError:
    from dummy_thread import get_ident as _get_ident


class OrderedDict(dict):

    '''Dictionary that remembers insertion order'''

    def __init__(self, *args, **kw):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self._root
        except AttributeError:
            self._root = root = []
            root[:] = [root, root, None]
            self._map = {}
        self._update(*args, **kw)

    def __setitem__(self, k, value, dict_setitem=dict.__setitem__):
        if k not in self:
            root = self._root
            last = root[0]
            last[1] = root[0] = self._map[k] = [last, root, k]
        dict_setitem(self, k, value)

    def __delitem__(self, k, dict_delitem=dict.__delitem__):
        dict_delitem(self, k)
        link_prev, link_next, k = self._map.pop(k)
        link_prev[1] = link_next
        link_next[0] = link_prev

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            return len(self)==len(other) and self.items() == other.items()
        return dict.__eq__(self, other)

    def __iter__(self):
        root = self._root
        curr = root[1]
        while curr is not root:
            yield curr[2]
            curr = curr[1]

    def __ne__(self, other):
        return not self == other

    def __repr__(self, _repr_running={}):
        call_key = id(self), _get_ident()
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1
        try:
            if not self: return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, self.items())
        finally:
            del _repr_running[call_key]

    def __reversed__(self):
        root = self._root
        curr = root[0]
        while curr is not root:
            yield curr[2]
            curr = curr[0]

    def clear(self):
        try:
            for node in self._map.itervalues(): del node[:]
            root = self._root
            root[:] = [root, root, None]
            self._map.clear()
        except AttributeError:
            pass
        dict.clear(self)

    def copy(self):
        return self.__class__(self)

    def items(self):
        return list((k, self[k]) for k in self)

    def iteritems(self):
        for k in self: yield (k, self[k])

    def iterkeys(self):
        return iter(self)

    def itervalues(self):
        for k in self: yield self[k]

    def keys(self):
        return list(self)

    __marker = object()

    def pop(self, k, default=__marker):
        if k in self:
            result = self[k]
            del self[k]
            return result
        if default is self.__marker: raise KeyError(k)
        return default

    def popitem(self, last=True):
        if not self: raise KeyError('dictionary is empty')
        root = self._root
        if last:
            link = root[0]
            link_prev = link[0]
            link_prev[1] = root
            root[0] = link_prev
        else:
            link = root[1]
            link_next = link[1]
            root[1] = link_next
            link_next[0] = root
        k = link[2]
        del self._map[k]
        value = dict.pop(self, k)
        return k, value

    def setdefault(self, k, default=None):
        if k in self: return self[k]
        self[k] = default
        return default

    def update(self, *args, **kw):
        if len(args) > 2:
            raise TypeError(
                'update() takes at most 2 positional arguments (%d given)' % (
                    len(args),
                )
            )
        elif not args:
            raise TypeError('update() takes at least 1 argument (0 given)')
        self = args[0]
        other = ()
        if len(args) == 2:
            other = args[1]
        if isinstance(other, dict):
            for k in other: self[k] = other[k]
        elif hasattr(other, 'keys'):
            for k in other.keys(): self[k] = other[k]
        else:
            for k, value in other: self[k] = value
        for k, value in kw.items(): self[k] = value

    _update = update

    def values(self):
        return list(self[k] for k in self)