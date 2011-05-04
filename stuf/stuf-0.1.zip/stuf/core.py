'''stuf'''

from operator import eq as _eq
from itertools import imap as _imap
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from collections import _recursive_repr

from stuf.util import lru_cache, lazy

_osettr = object.__setattr__
_ogettr = object.__getattribute__


class _basestuf(object):

    def __iter__(self):
        for k, v in self.iteritems():
            if isinstance(v, self.__class__):
                yield (k, list(v.__iter__()))
            else:
                yield (k, v)

    @staticmethod
    def _args2dict(*args, **kw):
        if args:
            if len(args) > 1:
                raise TypeError('Invalid number of arguments %s' % len(args))
            source = args[0]
            if isinstance(source, (_basestuf, dict)):
                kw.update(source)
            elif isinstance(source, (list, tuple)):
                for arg in source:
                    if isinstance(arg, (list, tuple)) and len(arg) == 2:
                        kw[arg[0]] = arg[-1]
        return kw

    @lazy
    def _classkeys(self):
        return frozenset(self.__dict__.keys()+self.__class__.__dict__.keys())


class _basefixfroze(_basestuf):

    def __init__(self, *args, **kw):
        kw = self._args2dict(*args, **kw)
        self._keys = frozenset(kw.keys())
        self._stuf = dict()
        self._saddle(**kw)

    def __getitem__(self, k):
        if k in self._keys: return self._stuf[k]
        raise KeyError(k)

    def __getattr__(self, k):
        try:
            return _ogettr(self, k)
        except AttributeError:
            if k in self._keys: return self._stuf[k]
            raise AttributeError(k)

    def __delattr__(self, k):
        raise TypeError(u'%ss are immutable' % self.__class__.__name__)

    def __cmp__(self, other):
        for k, v in self.iteritems():
            if other[k] != v: return False
        return False

    def __contains__(self, k):
        return self._stuf.__contains__(k)

    def __len__(self):
        return self._stuf.__len__()

    def __reduce__(self):
        return self._stuf.__reduce__()

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, unicode(self._stuf))

    def _saddle(self, *args, **kw):
        stf = self._stuf
        cls = self.__class__
        for k, v in self._args2dict(*args, **kw).iteritems():
            if isinstance(v, (tuple, dict, list)):
                trial = cls(v)
                if len(trial) > 0:
                    stf[k] = trial
                else:
                    stf[k] = v
            else:
                stf[k] = v

    def get(self, k, default=None):
        return self._stuf.get(k, default)

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        for v in self._stuf.iteritems():
            if isinstance(v, self.__class__):
                yield list(v.__iter__())
            else:
                yield v

    def iterkeys(self):
        return self._stuf.iterkeys()

    def itervalues(self):
        for v in self._stuf.itervalues():
            if isinstance(v, self.__class__):
                yield dict(v.__iter__())
            else:
                yield v

    def keys(self):
        return self._stuf.keys()

    def setdefault(self, k, default):
        return self._stuf.setdefault(k, default)

    def values(self):
        return list(self.itervalues())


class stuf(_basestuf, dict):

    '''stuf'''

    def __init__(self, *args, **kw):
        self.update(*args, **kw)

    def __getattr__(self, k):
        try:
            return super(stuf, self).__getitem__(k)
        except KeyError:
            raise AttributeError(k)

    def __setattr__(self, k, v):
        try:
            _ogettr(self, k)
        except AttributeError:
            try:
                super(stuf, self).__setitem__(k, v)
            except:
                raise AttributeError(k)
        else:
            _osettr(self, k, v)

    def __delattr__(self, k):
        try:
            _ogettr(self, k)
        except AttributeError:
            try:
                super(stuf, self).__delitem__(k)
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    def update(self, *args, **kw):
        cls = self.__class__
        for k, v in self._args2dict(*args, **kw).iteritems():
            if isinstance(v, (tuple, dict, list)):
                trial = cls(v)
                if len(trial) > 0:
                    super(stuf, self).__setitem__(k, trial)
                else:
                    super(stuf, self).__setitem__(k, v)
            else:
                super(stuf, self).__setitem__(k, v)


class defaultstuf(stuf):

    _factory = None
    _fargs = ()

    def __init__(self, factory, *args, **kw):
        self._factory = factory
        if args: self._fargs = args[0]
        self.update(*args[1:], **kw)

    def __missing__(self, k):
        self[k] = self._factory(*self._fargs)
        return self[k]

    def update(self, *args, **kw):
        factory = self._factory
        fargs = self._fargs
        cls = self.__class__
        for k, v in self._args2dict(*args, **kw).iteritems():
            if isinstance(v, (tuple, dict, list)):
                trial = cls(factory, fargs, v)
                if len(trial) > 0:
                    super(stuf, self).__setitem__(k, trial)
                else:
                    super(stuf, self).__setitem__(k, v)
            else:
                super(stuf, self).__setitem__(k, v)


class fixedstuf(_basefixfroze):

    '''fixed stuf'''

    _keys = None
    _stuf = None

    def __setitem__(self, k, v):
        if k in self._keys:
            self._stuf[k] = v
        else:
            raise KeyError(k)

    def __setattr__(self, k, v):
        if k == '_classkeys' or k in self._classkeys:
            _osettr(self, k, v)
        elif k in self._keys:
            try:
                self._stuf[k] = v
            except:
                raise AttributeError(k)
        else:
            raise AttributeError(k)

    def update(self, *args, **kw):
        self._saddle(*args, **kw)


class frozenstuf(_basefixfroze):

    '''fixed stuf'''

    _keys = None
    _stuf = None

    @lru_cache()
    def __getitem__(self, k):
        return super(frozenstuf, self).__getitem__(k)

    @lru_cache()
    def __getattr__(self, k):
        return super(frozenstuf, self).__getattr__(k)

    def __setattr__(self, k, v):
        if k == '_classkeys' or k in self._classkeys:
            _osettr(self, k, v)
        else:
            raise TypeError(u'%s is immutable' % self.__class__.__name__)


class orderedstuf(stuf):

    _root = None
    _map = None

    def __init__(self, *args, **kw):
        self._root = root = [None, None, None]
        root[0] = root[1] = root
        self._map = {}
        self.update(*args, **kw)

    def __setitem__(self, k, v):
        if k not in self:
            root = self._root
            last = root[0]
            last[1] = root[0] = self._map[k] = [last, root, v]
        super(orderedstuf, self).__setitem__(k, v)

    def __delitem__(self, k):
        super(orderedstuf, self).__delitem__(k)
        link = self._map.pop(k)
        link_prev = link[0]
        link_next = link[1]
        link_prev[1] = link_next
        link_next[0] = link_prev

    def __eq__(self, other):
        if isinstance(other, orderedstuf):
            return len(self)==len(other) and all(
                _imap(_eq, self.iteritems(), other.iteritems())
            )
        return super(orderedstuf, self).__eq__(other)

    def __iter__(self):
        root = self._root
        curr = root[1]
        while curr is not root:
            yield curr[2]
            curr = curr[1]

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        tmp = self._map, self._root
        del self._map, self._root
        inst_dict = vars(self).copy()
        self._map, self._root = tmp
        if inst_dict: return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    @_recursive_repr
    def __repr__(self):
        if not self: return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def __reversed__(self):
        root = self._root
        curr = root[0]
        while curr is not root:
            yield curr[2]
            curr = curr[0]

    @staticmethod
    def _args2dict(*args, **kw):
        newdict = OrderedDict()
        if args:
            if len(args) > 1:
                raise TypeError(u'Invalid number of arguments %s' % len(args))
            source = args[0]
            if isinstance(source, (OrderedDict, dict)):
                newdict.update(tuple(source.iteritems()))
            elif isinstance(source, (list, tuple)):
                for arg in source:
                    if isinstance(arg, (list, tuple)) and len(arg) == 2:
                        newdict[arg[0]] = arg[-1]
        newdict.update(kw)
        return newdict

    def clear(self):
        try:
            for node in self._map.itervalues(): del node[:]
            self._root[:] = [self._root, self._root, None]
            self._map.clear()
        except AttributeError:
            pass
        super(orderedstuf, self).clear()

    def copy(self):
        return self.__class__(self)

    def popitem(self, last=True):
        if not self: raise KeyError('dictionary is empty')
        k = next(reversed(self) if last else iter(self))
        v = self.pop(k)
        return k, v

    def update(self, *args, **kw):
        cls = self.__class__
        for k, v in self._args2dict(*args, **kw).iteritems():
            if isinstance(v, (OrderedDict, tuple, dict, list)):
                trial = cls(v)
                if len(trial) > 0:
                    self.__setitem__(k, trial)
                else:
                    self.__setitem__(k, v)
            else:
                self.__setitem__(k, v)