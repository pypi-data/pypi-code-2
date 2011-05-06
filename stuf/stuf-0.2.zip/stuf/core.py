'''core stuf of stuf'''

from operator import eq
from itertools import imap
from functools import partial

from stuf.util import OrderedDict, lazy, lru_wrapped, recursive_repr, lazycls

_osettr = object.__setattr__
_ogettr = object.__getattribute__


class _basestuf(object):

    def __init__(self, arg):
        self._saddle(src=self._preprep(arg))

    def __iter__(self):
        cls = self.__class__
        for k, v in self.iteritems():
            if isinstance(v, cls):
                yield (k, list(i for i in v))
            else:
                yield (k, v)

    def __reduce__(self):
        items = list([k, self[k]] for k in self)
        inst_dict = vars(self).copy()
        if inst_dict: return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    @recursive_repr
    def __repr__(self):
        if not self: return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    @lazy
    def _classkeys(self):
        return frozenset(vars(self).keys()+self.__class__.__dict__.keys())

    @lazy
    def _setit(self):
        return self.__setitem__

    @classmethod
    def _fromiter(cls, src=(), typ=dict, sq=[list, tuple]):
        return cls(cls._todict(src=src, typ=typ, sq=sq))

    @classmethod
    def _fromkw(cls, typ=dict, sq=[list, tuple], **kw):
        return cls._fromiter(src=kw, typ=typ, sq=sq)

    def _prep(self, arg, **kw):
        if arg: kw.update(self._todict(src=arg))
        return kw

    def _preprep(self, arg):
        return arg

    @classmethod
    def _todict(cls, src=(), typ=dict, maps=[dict], sq=[list, tuple]):
        kw = typ()
        maps = tuple(maps+[cls])
        sq = tuple(sq+[cls])
        if isinstance(src, tuple(maps)):
            kw.update(typ(i for i in src.iteritems()))
        elif isinstance(src, tuple(sq)):
            for arg in src:
                if isinstance(arg, sq) and len(arg) == 2: kw[arg[0]] = arg[-1]
        return kw

    def _saddle(self, src={}, sq=[tuple, dict, list]):
        fromiter = self._fromiter
        setit = self._setit
        tsq = tuple(sq)
        for k, v in src.iteritems():
            if isinstance(v, tsq):
                trial = fromiter(src=v, sq=sq)
                if len(trial) > 0:
                    setit(k, trial)
                else:
                    setit(k, v)
            else:
                setit(k, v)

    def _update(self, *args, **kw):
        return self._saddle(src=self._prep(*args, **kw))

    def copy(self):
        return self._fromiter(dict(i for i in self))

    # inheritance protection
    _b_iter = __iter__
    _b_repr = __repr__
    _b_reduce = __reduce__
    _b_classkeys = _classkeys
    _b_copy = copy
    _b_fromiter = _fromiter
    _b_fromkw = _fromkw
    _b_prep = _prep
    _b_preprep = _preprep
    _b_saddle = _saddle
    _b_setit = _setit
    _b_todict = _todict
    _b_update = _update


class _openstuf(_basestuf, dict):

    def __getattr__(self, k):
        try:
            return self.__getitem__(k)
        except KeyError:
            raise AttributeError(k)

    def __setattr__(self, k, v):
        if k == '_classkeys' or k in self._classkeys:
            _osettr(self, k, v)
        else:
            try:
                return self.__setitem__(k, v)
            except:
                raise AttributeError(k)

    def __delattr__(self, k):
        if not k == '_classkeys' or k in self._classkeys:
            try:
                self.__delitem__(k)
            except KeyError:
                raise AttributeError(k)

    @lazy
    def update(self):
        return self._b_update

    # inheritance protection
    _o_getattr = __getattr__
    _o_setattr = __setattr__
    _o_delattr = __delattr__
    _o_update = update


class _defaultstuf(_openstuf):

    _factory = None
    _fargs = ()
    _fkw = {}

    def __missing__(self, k):
        factory = self._factory
        if factory is not None:
            self[k] = factory(*self._fargs, **self._fkw)
            return self[k]
        return None

    @classmethod
    def _fromiter(cls, factory=None, fargs=(), fkw={}, src=(), sq=[list, tuple]):
        src = cls._todict(src=src)
        src.update(fargs=fargs, factory=factory, fkw=fkw)
        return cls(src)

    @classmethod
    def _fromkw(cls, factory=None, fargs=(), fkw={}, **kw):
        return cls._d_fromiter(factory, fargs, fkw, kw)

    def _preprep(self, arg):
        factory = arg.pop('factory')
        fargs = arg.pop('fargs')
        fkw = arg.pop('fkw')
        self._factory = factory
        self._fargs = fargs
        self._fkw = fkw
        self._fromiter = partial(
            self._d_fromiter,
            factory=factory,
            fargs=fargs,
            fkw=fkw,
        )
        return arg

    # inheritance protection
    _d_missing = __missing__
    _d_fromiter = _fromiter
    _d_fromkw = _fromkw
    _d_preprep = _preprep


class _orderedstuf(_openstuf):

    _root = None
    _map = None

    def __setitem__(self, k, v):
        if k not in self:
            root = self._root
            last = root[0]
            last[1] = root[0] = self._map[k] = [last, root, v]
        super(_orderedstuf, self).__setitem__(k, v)

    def __delitem__(self, k):
        super(_orderedstuf, self).__delitem__(k)
        link = self._map.pop(k)
        link_prev = link[0]
        link_next = link[1]
        link_prev[1] = link_next
        link_next[0] = link_prev

    def __eq__(self, other):
        if isinstance(other, _orderedstuf):
            return len(self)==len(other) and all(
                imap(eq, self.iteritems(), other.iteritems())
            )
        return super(_orderedstuf, self).__eq__(other)

    def __iter__(self):
        root = self._root
        curr = root[1]
        while curr is not root:
            cr = curr[2]
            if isinstance(cr, self.__class__):
                yield cr, tuple(i for i in self[cr])
            else:
                yield cr, self[cr]
            curr = curr[1]

    def __reduce__(self):
        items = list([k, self[k]] for k in self)
        tmp = self._map, self._root
        del self._map, self._root
        inst_dict = vars(self).copy()
        self._map, self._root = tmp
        if inst_dict: return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def __reversed__(self):
        root = self._root
        curr = root[0]
        while curr is not root:
            yield curr[2]
            curr = curr[0]

    @lazy
    def _saddle(self):
        return partial(self._b_saddle, sq=[tuple, dict, list])

    @lazycls
    def _todict(self):
        return partial(
            self._b_todict, typ=OrderedDict, maps=[dict],
        )

    @lazy
    def _update(self):
        return partial(self._b_update, seqs=(OrderedDict, tuple, dict, list))

    def _preprep(self, arg):
        self._root = root = [None, None, None]
        root[0] = root[1] = root
        self._map = {}
        return arg

    def clear(self):
        try:
            for node in self._map.itervalues(): del node[:]
            self._root[:] = [self._root, self._root, None]
            self._map.clear()
        except AttributeError:
            pass
        super(_orderedstuf, self).clear()

    def popitem(self, last=True):
        if not self: raise KeyError('dictionary is empty')
        k = next(reversed(self) if last else iter(self))
        v = self.pop(k)
        return k, v

    _r_setitem = __setitem__
    _r_delitem = __delitem__
    _r_eq = __eq__
    _r_iter = __iter__
    _r_reduce = __reduce__
    _r_reversed = __reversed__
    _r_clear = clear
    _r_popitem = popitem
    _r_preprep = _preprep
    _r_saddle = _saddle
    _r_todict = _todict
    _r_update = update = _update


class _closedstuf(_basestuf):

    _stuf = {}

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

    @lazy
    def __contains__(self):
        return self._stuf.__contains__

    @lazy
    def __len__(self):
        return self._stuf.__len__

    @lazy
    def __reduce__(self):
        return self._stuf.__reduce__

    @lazy
    def _update(self):
        return self._b_update

    @lazy
    def get(self):
        return self._stuf.get

    @lazy
    def iterkeys(self):
        return self._stuf.iterkeys

    @lazy
    def keys(self):
        return self._stuf.keys

    @lazy
    def setdefault(self):
        return self._stuf.setdefault

    def _preprep(self, arg):
        self._keys = frozenset(arg.keys())
        self._stuf = dict()
        return arg

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        cls = self.__class__
        for v in self._stuf.iteritems():
            if isinstance(v, cls):
                yield list(v.__iter__())
            else:
                yield v

    def itervalues(self):
        for v in self._stuf.itervalues():
            if isinstance(v, self.__class__):
                yield dict(v.__iter__())
            else:
                yield v

    def values(self):
        return list(self.itervalues())

    _c_getitem = __getitem__
    _c_getattr = __getattr__
    _c_delattr = __delattr__
    _c_cmp = __cmp__
    _c_contains = __contains__
    _c_len = __len__
    _c_reduce = __reduce__
    _c_prep = _preprep
    _c_update = _update
    _c_get = get
    _c_items = items
    _c_iterkeys = iterkeys
    _c_itervalues = itervalues
    _c_keys = keys
    _c_setdefault = setdefault
    _c_values = values


class _fixedstuf(_closedstuf):

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

    @lazy
    def update(self):
        return self._c_update

    _fs1_setattr = __setattr__
    _fs1_setitem = __setitem__
    _fs1_update = update


class _frozenstuf(_closedstuf):

    _keys = None
    _stuf = None

    def __setattr__(self, k, v):
        if k == '_classkeys' or k in self._classkeys:
            _osettr(self, k, v)
        else:
            raise TypeError(u'%s is immutable' % self.__class__.__name__)

    @lazy
    def __getitem__(self):
        return lru_wrapped(self._c_getitem, 100)

    @lazy
    def __getattr__(self):
        return lru_wrapped(self._c_getattr, 100)

    @lazy
    def _setit(self):
        return self._stuf.__setitem__

    _fs2_setattr = __setattr__
    _fs2_getitem = __getitem__
    _fs2_getattr = __getattr__
    _fs2_setit = _setit


# stuf from keywords
stuf = _openstuf._fromkw
defaultstuf = _defaultstuf._fromkw
orderedstuf = _orderedstuf._fromkw
fixedstuf = _fixedstuf._fromkw
frozenstuf = _frozenstuf._fromkw
# stuf from iterables
istuf = _openstuf._fromiter
iorderedstuf = _orderedstuf._fromiter
ifixedstuf = _fixedstuf._fromiter
idefaultstuf = _defaultstuf._fromiter
ifrozenstuf = _frozenstuf._fromiter