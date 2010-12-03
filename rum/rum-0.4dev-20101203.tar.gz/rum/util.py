import re
import types
from inspect import getargspec, isclass
from rumcomponent.util import NoDefault
from rumcomponent.util import import_string

__all__ = ["import_string", "adapt_call", "safe_issubclass", "NoDefault",
           "generate_label", "merge_dicts"]


def adapt_call(func, **kw):
    """
    Calls ``func`` with as many arguments from ``kw`` as possible.

    Example::

        >>> def some_func(a, b):
        ...     return a + b
        >>> adapt_call(some_func, a=4, b=3, c=6)
        7
        
        >>> def some_func(a, b=2):
        ...     return a + b
        >>> adapt_call(some_func, a=4)
        6

        >>> def some_func(a, b=2, **kw):
        ...     return a + b + kw['c']
        >>> adapt_call(some_func, a=4, c=2)
        8

        >>> class SomeCallable(object):
        ...     def __call__(self, a, b):
        ...         return a + b
        >>> adapt_call(SomeCallable(), a=5, b=4)
        9

        >>> class SomeClass(object):
        ...     def __init__(self, name):
        ...         self.name = name
        >>> obj = adapt_call(SomeClass, name="foo", age="bar")
        >>> obj.name
        'foo'
    """
    if not isinstance(func, (types.FunctionType, types.MethodType)):
        if isclass(func):
            # Handle constructors
            inspect = getattr(func, '__init__')
        else:
            # Handle callable objects
            func = inspect = getattr(func, '__call__')
    else:
        inspect = func
    args, varargs, varkw, defaults = getargspec(inspect)
    if varkw is None:
        for k in kw.keys():
            if k not in args:
                del kw[k]
    return func(**kw)

def safe_issubclass(cls, typs):
    return isclass(cls) and issubclass(cls, typs)



_labelRE = re.compile(r'([A-Z][a-z0-9]+|[a-z0-9]+|[A-Z0-9]+)')

def generate_label(name):
    """
    Convert a name to a Human Readable name.

    Yanked from TGFastData
    """
    # Create label from the name:
    #   1) Convert _ to spaces
    #   2) Convert CamelCase to Camel Case
    #   3) Upcase first character of Each Word
    # Note: I *think* it would be thread-safe to
    #       memoize this thing.
    from rum.i18n import ugettext
    return ugettext(' '.join(_labelRE.findall(name))).capitalize()

def keywords_to_str(keywords_orig):
    keywords=dict()
    for (k,v) in keywords_orig.iteritems():
        if isinstance(k,unicode):
            k=k.encode("utf-8")
        keywords[k]=v
    return keywords

    
def merge_dicts(to, from_):
    """
    Recursively merges ``from_`` into ``to`` (in-place) and returns ``to``.
    Keys from ``from_`` will ovewrite existing keys in ``to``

    Example::

        >>> d1 = {'a':1, 'sub':{'a':2}}
        >>> d2 = {'a':3, 'sub':{'b':4}}
        >>> result = merge_dicts(d1, d2)
        >>> result['a'] == 3
        True
        >>> result['sub']['a'] == 2
        True
        >>> result['sub']['b'] == 4
        True
    """
    for (k,v) in from_.iteritems():
        if k in to and isinstance(to[k], dict) and isinstance(v, dict):
            merge_dicts(to[k], v)
        else:
            to[k] = v
    return to


