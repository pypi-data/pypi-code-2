'''core stuf of stuf'''

from operator import eq
from itertools import imap
from functools import partial

from stuf.util import OrderedDict, lazy, lru_wrapped, recursive_repr, lazycls

_osettr = object.__setattr__
_ogettr = object.__getattribute__


class _BaseStuf(object):

    '''Base class for stuff'''

    def __init__(self, arg):
        self._saddle(src=self._preprep(arg))

    def __iter__(self):
        cls = self.__class__
        for k, v in self.iteritems():
            if isinstance(v, cls):
                yield (k, dict(i for i in v))
            else:
                yield (k, v)

    def __getstate__(self):
        return dict(i for i in self)

    def __setstate__(self, state):
        return self._fromiter(src=state)

    @recursive_repr
    def __repr__(self):
        if not self: return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    @lazy
    def _classkeys(self):
        return frozenset(
            vars(self).keys()+self.__class__.__dict__.keys()+[
                '_keys', '_factory', '_fargs', '_fkw', '_root', '_map',
            ]
        )

    @lazy
    def _setit(self):
        return self.__setitem__

    @classmethod
    def _fromiter(cls, src=(), typ=dict, sq=[list, tuple]):
        return cls(cls._todict(src=src, typ=typ, sq=sq))

    @classmethod
    def _fromkw(cls, typ=dict, sq=[list, tuple], **kw):
        return cls._b_fromiter(src=kw, typ=typ, sq=sq)

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
    _b_classkeys = _classkeys
    _b_copy = copy
    _b_fromiter = _fromiter
    _b_fromkw = _fromkw
    _b_getstate = __getstate__
    _b_iter = __iter__
    _b_prep = _prep
    _b_preprep = _preprep
    _b_repr = __repr__
    _b_saddle = _saddle
    _b_setit = _setit
    _b_todict = _todict
    _b_update = _update


class IStuf(_BaseStuf, dict):

    '''dict with dot attributes'''

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


class Stuf(IStuf):

    '''IStuf taking keyword arguments'''

    def __init__(self, **kw):
        self._saddle(src=self._preprep(kw))


class IDefaultStuf(IStuf):

    '''dict with dot attributes and a default function'''

    def __getstate__(self):
        return dict(
            content=dict(i for i in self),
            factory=self._factory,
            fargs=self._fargs,
            fkw=self._fkw,
        )

    def __setstate__(self, state):
        return self._d_fromiter(
            factory=state['factory'],
            fargs=state['fargs'],
            fkw=state['fkw'],
            src=state['content'],
        )

    def __missing__(self, k):
        factory = self._factory
        if factory is not None:
            self[k] = factory(*self._fargs, **self._fkw)
            return self[k]
        return None

    @classmethod
    def _fromiter(
        cls, factory=None, fargs=(), fkw={}, src=(), sq=[list, tuple],
    ):
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

    def copy(self):
        return self._d_fromiter(
            factory=self._factory,
            fargs=self._fargs,
            fkw=self._fkw,
            src=dict(i for i in self),
        )

    # inheritance protection
    _d_copy = copy
    _d_fromiter = _fromiter
    _d_fromkw = _fromkw
    _d_getstate = __getstate__
    _d_missing = __missing__
    _d_preprep = _preprep
    _d_setstate = __setstate__


class DefaultStuf(IDefaultStuf):

    '''IDefaultStuf taking keyword arguments'''

    def __init__(self, **kw):
        self._saddle(src=self._preprep(kw))


class IOrderedStuf(IStuf):

    '''dict with dot attributes that remembers insertion order'''

    def __setitem__(self, k, v):
        if k not in self:
            root = self._root
            last = root[0]
            last[1] = root[0] = self._map[k] = [last, root, k]
        super(self.__class__, self).__setitem__(k, v)

    def __delitem__(self, k):
        super(IOrderedStuf, self).__delitem__(k)
        link = self._map.pop(k)
        link_prev = link[0]
        link_next = link[1]
        link_prev[1] = link_next
        link_next[0] = link_prev

    def __getstate__(self):
        return tuple(i for i in self)

    def __reduce__(self):
        return _pickleorderedstuf, (tuple(i for i in self),)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return len(self)==len(other) and all(
                imap(eq, self.iteritems(), other.iteritems())
            )
        return super(self.__class__, self).__eq__(other)

    def __iter__(self):
        root = self._root
        curr = root[1]
        while curr is not root:
            key = curr[2]
            value = self[key]
            if isinstance(value, self.__class__):
                yield key, tuple(i for i in value)
            else:
                yield key, value
            curr = curr[1]

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
        return partial(self._b_todict, typ=OrderedDict, maps=[dict])

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
        super(self.__class__, self).clear()

    def copy(self):
        return self._b_fromiter(list(i for i in self))

    def items(self):
        return list((k, v) for k, v in self.iteritems())

    def iteritems(self):
        for k in self: yield k[0], self[k[0]]

    def iterkeys(self):
        for k in self: yield k[0]

    def itervalues(self):
        for k in self: yield self[k[0]]

    def keys(self):
        return list(i for i in self.iterkeys())

    def popitem(self, last=True):
        if not self: raise KeyError('dictionary is empty')
        k = next(reversed(self) if last else iter(self))
        v = self.pop(k)
        return k, v

    def values(self):
        return list(i for i in self.itervalues())

    # inheritance protection
    _r_clear = clear
    _r_delitem = __delitem__
    _r_eq = __eq__
    _r_items = items
    _r_iter = __iter__
    _r_iterkeys = iterkeys
    _r_iteritems = iteritems
    _r_itervalues = itervalues
    _r_keys = keys
    _r_popitem = popitem
    _r_preprep = _preprep
    _r_reduce = __reduce__
    _r_reversed = __reversed__
    _r_saddle = _saddle
    _r_setitem = __setitem__
    _r_todict = _todict
    _r_update = update = _update
    _r_values = values


class OrderedStuf(IOrderedStuf):

    '''IOrderedStuf taking keyword arguments'''

    def __init__(self, **kw):
        self._saddle(src=self._preprep(kw))


class _ClosedStuf(_BaseStuf):

    '''Restricted stuf'''

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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return len(self)==len(other) and all(
                imap(eq, iter(self), iter(other))
            )
        elif isinstance(other, dict):
            return len(self)==len(other) and all(
                imap(eq, self.iteritems(), other.iteritems())
            )
        return False

    @lazy
    def __contains__(self):
        return self._stuf.__contains__

    @lazy
    def __len__(self):
        return self._stuf.__len__

    @lazy
    def _stuf(self):
        return {}

    @lazy
    def _update(self):
        return self._b_update

    @lazy
    def get(self):
        return self._stuf.get

    @lazy
    def items(self):
        return self._stuf.items

    @lazy
    def iteritems(self):
        return self._stuf.iteritems

    @lazy
    def iterkeys(self):
        return self._stuf.iterkeys

    @lazy
    def itervalues(self):
        return self._stuf.itervalues

    @lazy
    def keys(self):
        return self._stuf.keys

    @lazy
    def setdefault(self):
        return self._stuf.setdefault

    @lazy
    def values(self):
        return self._stuf.values

    def _preprep(self, arg):
        self._keys = frozenset(arg.keys())
        return arg

    # inheritance protection
    _c_eq = __eq__
    _c_contains = __contains__
    _c_delattr = __delattr__
    _c_get = get
    _c_getattr = __getattr__
    _c_getitem = __getitem__
    _c_items = items
    _c_iterkeys = iterkeys
    _c_itervalues = itervalues
    _c_len = __len__
    _c_keys = keys
    _c_prep = _preprep
    _c_setdefault = setdefault
    _c_stuf = _stuf
    _c_update = _update
    _c_values = values


class IFixedStuf(_ClosedStuf):

    '''dict with dot attributes and mutability restricted to initial keys'''

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

    def __reduce__(self):
        return _picklefixedstuf, (dict(i for i in self),)

    @lazy
    def update(self):
        return self._c_update

    # inheritance protection
    _fs1_reduce = __reduce__
    _fs1_setattr = __setattr__
    _fs1_setitem = __setitem__
    _fs1_update = update


class FixedStuf(IFixedStuf):

    '''IFixedStuf taking keyword arguments'''

    def __init__(self, **kw):
        self._saddle(src=self._preprep(kw))


class IFrozenStuf(_ClosedStuf):

    '''Immutable dict with dot attributes'''

    def __setattr__(self, k, v):
        if k == '_classkeys' or k in self._classkeys:
            _osettr(self, k, v)
        else:
            raise TypeError(u'%s is immutable' % self.__class__.__name__)

    def __reduce__(self):
        return _picklefrozenstuf, (dict(i for i in self),)

    @lazy
    def __getitem__(self):
        return lru_wrapped(self._c_getitem, 100)

    @lazy
    def __getattr__(self):
        return lru_wrapped(self._c_getattr, 100)

    @lazy
    def _setit(self):
        return self._stuf.__setitem__

    # inheritance protection
    _fs2_getitem = __getitem__
    _fs2_getattr = __getattr__
    _fs2_reduce = __reduce__
    _fs2_setattr = __setattr__
    _fs2_setit = _setit


class FrozenStuf(IFrozenStuf):

    '''IFixedStuf taking keyword arguments'''

    def __init__(self, **kw):
        self._saddle(src=self._preprep(kw))


# factories for stuf from keywords
stuf = IStuf._fromkw
defaultstuf = IDefaultStuf._fromkw
orderedstuf = IOrderedStuf._fromkw
fixedstuf = IFixedStuf._fromkw
frozenstuf = IFrozenStuf._fromkw
# factories for stuf from iterables
istuf = IStuf._fromiter
iorderedstuf = IOrderedStuf._fromiter
ifixedstuf = IFixedStuf._fromiter
idefaultstuf = IDefaultStuf._fromiter
ifrozenstuf = IFrozenStuf._fromiter

# pickle helpers
def _pickleorderedstuf(it):
    return iorderedstuf(it)

def _picklefixedstuf(it):
    return ifixedstuf(it)

def _picklefrozenstuf(it):
    return ifrozenstuf(it)