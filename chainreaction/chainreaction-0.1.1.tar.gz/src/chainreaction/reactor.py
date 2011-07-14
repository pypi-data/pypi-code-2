"""Wrapper class that provides iterable object with infix style method call.  

Unreadble
>>> filter(lambda y: y % 2, map(lambda x: x + 1, iterable))

Readable
>>> iterable.map(lambda x: x + 1).filter(lambda y: y % 2)

The simplest(only) way to use this module is to call the 'react' function.  
'react' is a factory function which looksup '__iter__' and '__getitem__' from
given argument (they are iterator/sequence protocol),
and returns Wrapped object(Chainable object).  

Chainable object support any methods of its wrapped object,
and try to wrap their return value.  
By convention, side effective methods return nothing, but chainable object
returns its side affected object wrapped with appropriate wrappper.  
If iterator was passed into 'react', it would be consumed when it called
any iterative methods.  

Example Usage:
>>> from chainreaction.reactor import react
>>> tobewrapped = "hello"
>>> wrapped = react(tobewrapped) #Chainable object
>>> wrapped.upper().map(lambda c: ord(c))
  
>>> tobewrapped = [1, 2, 3]
>>> wrapped = react(tobewrapped)
>>> wrapped.append(4).counts()
4
>>> len(tobewrapped)
4

#if iterator was given, this iterator would be consumed everytime  
#it iterate with some methods.
>>> tobewrapped = iter([1,2,3])
>>> wrapped = react(tobewrapped)
>>> wrapped.counts()
4
#and interator was consumed... this is only a side effect of using _chainreact.
>>> len(list(tobewrapped))
0

@author: Keita Oouchi
@email : keita.oouchi@gmail.com
"""

import itertools
import functools

__all__ = ["react"]

def react(iterable):
    """Factory function creating Chainable object.
    
    If iterable supports iterator or sequencial access protocol,
    wrap it with Chainable class and provide some chaining style method.
    """
    cls = type(iterable)
    if hasattr(iterable, "__getitem__"):
        if cls is dict or issubclass(cls, dict):
            return DictChain(iterable)
        elif cls in (str, bytes, bytearray) or issubclass(cls, (str, bytes, bytearray)):
            return StrChain(iterable)
        else:
            return SeqChain(iterable)
    elif hasattr(iterable, "__iter__"):
        if cls in (set, frozenset) or issubclass(cls, (set, frozenset)):
            return SetChain(iterable)
        elif hasattr(iterable, "__next__") or hasattr(iterable, "next"):
            return IterChain(iterable)
        else:
            return Chainable(iterable)
    else:
        template = "Chainable does not support {0}. given argument:{1}:{0}"
        raise AttributeError(template.format(cls, iterable))

def _chainreact(__getattr__):
    """Decorator function used in Chainable's __getattr__ method.
    
    Chainable object support methods of its wrapped objects, and try to keep
    its return value also chainable.
    """
    def containment(*methodname):
        self, methodobj = __getattr__(*methodname)
        def reaction(*realargs):
            result = methodobj(*realargs)
            result = result if result else self
            return react(result)
        return reaction
    return containment


class Chainable(object):
    """ This class is a base class provides chainable interface.
    
    Iterator object would be wrapped with this class.
    """

    def __init__(self, iterable):
        self._iterable = iterable
        self._iterator = iterable
        self.type = type(iterable)

    @_chainreact
    def __getattr__(self, name):
        """Wrap return value using '_chanreact'."""
        return self._iterable, getattr(self._iterable, name)

    def __repr__(self):
        return "'{0}':{1}".format(self.unwrap, type(self))

    def _constract(self, iterable):
        """This method would be called when other methods, excluding methods of
        wrapped object, was called and wrap their return value if possible.
        """
        try:
            result = self.type(iterable)
        except TypeError:
            result = iterable
        finally:
            return result

    def __enter__(self):
        result = self._iterable.__enter__()
        if result:
            return self

    def __exit__(self, *args):
        result = self._iterable.__exit__(args)
        if result:
            return result

    @property
    def isiterator(self):
        """Check whether given iterable is iterator object."""
        return hasattr(self._iterable, "next") or hasattr(self._iterable, "__next__")

    @property
    def unwrap(self):
        """Return wrapped object."""
        return self._iterator

    @property
    def dump(self):
        print("[Information]")
        print(type(self).__name__)
        print(self.type)
        print(self)

    @property
    def tostring(self):
        return "".join((str(x) for x in self._iterator))

    def foreach(self, f):
        for x in self._iterator:
            f(x)

    def filter(self, pred):
        result = filter(pred, self._iterator)
        return react(self._constract(result))

    def map(self, f):
        result = map(f, self._iterator)
        return react(self._constract(result))

    def forall(self, pred):
        """True if whole elements satisfy a given predicate."""
        for x in self._iterator:
            if not pred(x):
                return False
        return True

    def forany(self, pred):
        """True if any elements satisfy a given predicate."""
        for x in self._iterator:
            if pred(x):
                return True
        return False

    def dropwhile(self, pred):
        """Drops longest prefix of elements that satisfy a given predicate."""
        result = itertools.dropwhile(pred, self._iterator)
        return react(self._constract(result))

    def dropright(self, pred):
        """Drops longest suffix of elements that satisfy a given predicate."""
        size = len(self._iterator)
        passed = size - 1
        tf = pred(self._iterator[passed])
        while tf:
            passed -= 1
            tf = pred(self._iterator[passed])
        return react(self._constract(self._iterator[0: passed + 1]))

    def takewhile(self, pred):
        """Takes longest prefix of elements that satisfy a given predicate."""
        result = itertools.takewhile(pred, self._iterator)
        return react(self._constract(result))

    def takeright(self, pred):
        """Takes longest suffix of elements that satisfy a given predicate."""
        size = len(self._iterator)
        passed = size - 1
        tf = pred(self._iterator[passed])
        while tf:
            passed -= 1
            tf = pred(self._iterator[passed])
        return react(self._constract(self._iterator[passed + 1:size]))

    def mkstring(self, joiner=""):
        """Returns wrapped str object using a joiner string."""
        strlist = (str(x) for x in self._iterator)
        return react(joiner.join(strlist))

    def counts(self, pred=lambda x: True):
        """Counts the number of elements that satisfy a given predicate."""
        result = 0
        for x in self._iterator:
            if pred(x):
                result += 1
        return result

    def contains(self, key):
        """Tests whether this wrapped object contains a given key as an element."""
        return key in self._iterator

    def reduce(self, f):
        """End of chain reaction"""
        return functools.reduce(f, self._iterator)

class IterChain(Chainable):
    def __init__(self, iterable):
        self._iterable = iterable
        self._iterator = iterable
        self.type = type(iterable)

    def _constract(self, iterable):
        return iterable

    @property
    def tolist(self):
        return react(list(self._iterable))

    @property
    def totuple(self):
        return react(tuple(self._iterable))

    @property
    def toset(self):
        return react(set(self._iterable))

class StrChain(Chainable):

    def __getitem__(self, key):
        return react(self._iterable[key])

    def _constract(self, iterable):
        return "".join((str(x) for x in iterable))

    @property
    def reverse(self):
        result = reversed(self._iterator)
        return react(self._constract(result))

    @property
    def tostring(self):
        if self.type == str:
            return self._iterator
        else:
            temp = self._iterator.decode()
            if type(temp) == str:
                return temp
            else:
                return temp.encode()

    def map(self, f):
        """Returns IterChain"""
        result = map(f, self._iterator)
        return react(result)

    def mkstring(self, joiner=""):
        return react(joiner.join(self._iterator))

class SeqChain(Chainable):

    def __getitem__(self, key):
        """a[i:j] => a.__getitem__(slice(i,j))"""
        item = self._iterable[key]
        try:
            result = react(item)
        except AttributeError:
            result = item
        finally:
            return result

    @property
    def reverse(self):
        result = reversed(self._iterator)
        return react(self._constract(result))

    @property
    def sort(self):
        result = sorted(self._iterator)
        return react(self._constract(result))

    @property
    def toset(self):
        return react(set(self._iterable))

    def accumulate(self, f):
        """Returns a seq of accumulated value."""
        def inner():
            it = iter(self._iterator)
            total = next(it)
            yield total
            for elem in it:
                total = f(total, elem)
                yield total
        return react(self._constract(inner()))

class SetChain(Chainable):

    @property
    def min(self):
        return min(self._iterator)

    @property
    def max(self):
        return max(self._iterator)

class DictChain(Chainable):

    def __init__(self, iterable):
        """DictChain internally uses list of tuple(key,value) as its iterator.
        [example]
        >>> dictchain.map(lambda t: (t[0], t[1] * 2))
        """
        self._iterable = iterable
        self._iterator = iterable.items()
        self.type = type(iterable)

    def __getitem__(self, key):
        item = self._iterable[key]
        try:
            result = react(item)
        except AttributeError:
            result = item
        finally:
            return result

    @property
    def tostring(self):
        key_value_pairs = ("{0}={1}".format(str(t[0]), str(t[1])) for t in self._iterator)
        return "&".join(key_value_pairs)

    def mkstring(self, joiner="&"):
        key_value_pairs = ("{0}={1}".format(str(t[0]), str(t[1])) for t in self._iterator)
        return react(joiner.join(key_value_pairs))
