#!/usr/bin/env python
"""
Sub-Package STDLIB of Package PLIB -- Python Standard Library Extensions
Copyright (C) 2008-2011 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains classes and functions which extend or
modify the Python standard library.

Note that, as with the PLIB.CLASSES sub-package, the ModuleProxy
class from the PLIB.UTILS sub-package is used to put the sub-modules
of this package in the package namespace, so that you can write,
for example,

    from plib.stdlib import abstractcontainer

instead of having to write

    from plib.stdlib.abstractcontainer import abstractcontainer

See the PLIB.CLASSES sub-package docstring and comments for more details.

This file itself currently includes:

variables pythonpath, plibpath, binpath, sharepath --
    contain pathnames to root python directory, plib directory,
    third-party binary directory, and third-party shared data directory
    (the latter two are where plib's scripts and example programs will
    have been installed)

function closure -- a reference to ``plib.stdlib.func.partial``,
    provided for convenience since the name is more indicative of
    the usage to some

function gcd -- fast implementation of Euclid's GCD algorithm.

function inrange -- returns index forced to be >= low, <= high.

function iterfile --

Returns a generator that can be used in place of "for line in file"
in cases (such as when stdin is the file) where Python's line buffering
might mean the program doesn't get the lines one at a time as they come,
but in bunches. See

http://utcc.utoronto.ca/~cks/space/blog/python/FileIteratorProblems

for a discussion of this issue and the code for this function that
fixes it. Note that the issue can also arise, as the blog entry notes,
with line-oriented network protocols, which means any time you are
using a "file-like object" derived from a socket.

function lcm -- fast implementation of LCM based on GCD above.

function normalize -- returns index with negative values normalized
    relative to count.

function normalize_slice -- returns a list of indexes "covered" by a
    slice (normalized relative to count), or an integer giving the
    index to which a zero-length slice refers (normalized relative
    to count).

function prod -- returns the product of all items in an iterable.

function slice_len -- returns the "length" of a slice (meaning the
    number of indexes that would be affected if it were used as an
    index into a sequence).

functions strtobool, strtodate -- self-explanatory.

function cached_property (and auxiliary class CachedProperty) --

Implementation of a "cached property" descriptor, which
does the following: on first access, it does a (presumably
expensive) calculation to determine the property's value,
and then "caches" the value in the instance as a plain
attribute, so further lookups will get the attribute
directly without the function call overhead of the
descriptor. Note that this means this must be a non-data
descriptor (because data descriptors, such as properties,
can't be masked by an ordinary instance attribute). This
also means, of course, that the "cached property" should
never be written to (it can be, but doing so wipes out
the cached value with no way of recovering it).

Note: the functionality has been split between a descriptor
class and a public decorator-usable function, but that is
not strictly necessary (since classes can be used as
decorators). Splitting it this way allows for a use case
where the class is called directly and the property name is
supplied explicitly (in which case there is no need for the
class to be cluttered with code to magically extract the
name from the fget function).

Also note that, unlike the standard property function, there
would be no real benefit in implementing cached_property in
a C extension module; the main reason for doing that would
be speed, but since the whole point is to eliminate the
overhead of the property altogether after the first access,
the additional overhead of a Python class instance is
negligible compared to the (presumably expensive) initial
calculation of the property value.

function upgrade_builtins -- convenience function to ensure
    that function names from more recent Python versions are
    in the builtin namespace even in earlier versions. See
    the function docstring for details.
"""

import sys
import datetime
from operator import mul

from plib.utils import ModuleProxy

from _paths import *

from plib.stdlib.func import partial as closure


def gcd(x, y):
    """Return greatest common divisor of x, y.
    """
    while x:
        x, y = y % x, x
    return y


def inrange(index, v1, v2):
    """Force index to be within the range v1 to v2, and return result.
    """
    if v1 < v2:
        low = v1
        high = v2
    else:
        low = v2
        high = v1
    return min(max(index, low), high)


def iterfile(f):
    """Return a generator that yields lines from a file.
    
    This works like "for line in file" does, but avoids potential
    problems with buffering. Use as::
    
        for line in iterfile(file):
    """
    
    while 1:
        line = f.readline() # guarantees getting each line when it's ready
        if not line:
            return # we've reached EOF
        yield line


def lcm(x, y):
    """Return least common multiple of x, y.
    """
    if (x == 0) and (y == 0):
        return 0
    return x * y / gcd(x, y)


def normalize(count, index):
    """Return index with negative values normalized to count.
    
    Index values out of range after conversion will raise IndexError.
    """
    
    if index < 0:
        result = index + count
    else:
        result = index
    if (result < 0) or (result > count - 1):
        raise IndexError, "sequence index out of range"
    return result


def normalize_slice(count, index):
    """Return slice index normalized to count.
    
    Return one of the following, depending on the type of slice index:
    
    - For a non-empty slice (e.g., [x:y] where x != y), return a list of
      indexes to be affected;
    
    - For an empty slice (e.g., [x:x]), return the slice location (x)
      as an int.
    
    - For extended slices, if start and stop are the same, return an
      empty list; otherwise treat as a non-empty slice.
    
    The index(es) returned will be normalized relative to count, and indexes
    out of range after normalization will be truncated to range(0, count + 1).
    The extra index at count is to allow for the possibility of an append
    (a zero-length slice with index == count). Note that this means that,
    unlike the normalize function above, this function will never throw an
    exception due to values being out of range; this is consistent with the
    observed semantics of Python slice syntax, where even values way out of
    range are accepted and truncated to zero or the end of the sequence.
    The only exception this routine will throw is ValueError for a zero
    slice step.
    """
    
    if index.step is None:
        step = 1
    else:
        step = int(index.step)
    if step == 0:
        raise ValueError, "Slice step cannot be zero."
    if index.start is None:
        if step < 0:
            start = count - 1
        else:
            start = 0
    else:
        start = int(index.start)
        if start < 0:
            start += count
    if index.stop is None:
        if step < 0:
            stop = -1
        else:
            stop = count
    else:
        stop = int(index.stop)
        if stop < 0:
            stop += count
    if start == stop:
        if step != 1:
            return []
        return inrange(start, 0, count)
    elif ( (count == 0) or
        ((step > 0) and ((start >= count) or (start > stop))) or
        ((step < 0) and ((start < 0) or (start < stop))) ):
            return []
    else:
        start = inrange(start, 0, count - 1)
        if step < 0:
            stop = inrange(stop, -1, count - 1)
        else:
            stop = inrange(stop, 0, count)
        return range(start, stop, step)


def prod(iterable):
    """Return the product of all items in iterable.
    """
    
    return reduce(mul, iterable, 1)


def slice_len(s):
    """Return the number of indexes referenced by a slice.
    
    Note that we do not normalize the slice indexes, since we don't
    have a sequence length to reference them to. Also note that,
    because of this, we have to return None if there is no stop value,
    or if start or stop are negative.
    """
    
    if s.start is None:
        start = 0
    else:
        start = int(s.start)
    if start < 0:
        return None
    if s.stop is None:
        return None
    stop = int(s.stop)
    if stop < 0:
        return None
    if s.step is None:
        step = 1
    else:
        step = int(s.step)
    if step == 0:
        raise ValueError, "Slice step cannot be zero."
    if start == stop:
        return 0
    else:
        return (stop - start) // step


def strtobool(s):
    """Return bool from string s interpreting s as a 'Python value string'.
    
    Return None if s is not 'True' or 'False'.
    """
    
    return {'False': False, 'True': True}.get(s, None)


def strtodate(s):
    """Return date object from string formatted as date.__str__ would return.
    """
    
    return datetime.date(*map(int, s.split('-')))


class CachedProperty(object):
    """Non-data descriptor class for cached property.
    
    The expected typical use case is to be called from the
    cached_property function, which generates the name of
    the property automatically, but the class can also be
    instantiated directly with an explicit name supplied.
    """
    
    def __init__(self, aname, fget, doc=None):
        self.aname = aname
        self.fget = fget
        self.__doc__ = doc
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        result = self.fget(obj)
        setattr(obj, self.aname, result)
        return result


def cached_property(fget, doc=None):
    """Function to return cached property instance.
    
    We need this as a wrapper to supply the name of the property
    by magic rather than force the user to enter it by hand;
    this is done by looking up the name of the fget function
    (which also allows this function to be used as a decorator
    and have the intended effect).
    """
    
    if doc is None:
        doc = fget.__doc__
    return CachedProperty(fget.__name__, fget, doc)


### Convenience function to upgrade builtin namespace ###

BUILTIN_NAMES = [
    'all',
    'any',
    'reversed',
    'sorted'
]

EXTRA_NAMES = [
    'first',
    'inverted',
    'last'
]

# This ensures we don't run the upgrade multiple times
_upgraded = False


def upgrade_builtins():
    """Upgrades __builtin__ namespace in earlier Python versions.
    
    This function is provided as a convenience for easier coding when using
    functions that are builtins in later Python versions, but which would
    normally have to be imported from plib.stdlib in earlier versions. For
    example, without this function, you would have to say::
    
        try:
            any
        except NameError:
            from plib.stdlib import any
    
    in order to ensure that the ``any`` function was accessible in your
    module. If you were using multiple such functions, this stanza would
    quickly become large and messy.
    
    An alternative to this function would be to put a similar stanza in the
    plib.stdlib code, so that such functions would always appear in the
    plib.stdlib namespace, whether they were builtins in the running Python
    version or not. However, this would still require you to say::
    
        from plib.stdlib import <builtin1>, <builtin2>, ...
    
    in your module, meaning that you would have to keep track of which
    builtins you were using module by module (or else use from import *,
    which is considered highly undesirable by all right-thinking Python
    programmers). Since the whole point of having built-in functions is to
    not have to do such things, this seems less than optimal.
    
    This function solves the problem as best it can be solved without major
    magical hackery at the time of importing plib.stdlib--which I may decide
    to try in future, so you have been warned. :-) But at present, this is
    the intended usage::
    
        # Do this somewhere in your code, usually at the end of imports
        from plib.stdlib import upgrade_builtins
        upgrade_builtins(__name__)
    
    This will add equivalent functions to the built-in namespace for all
    builtins from the following list that are not already present in the
    running version of Python. In addition, it will add the plib-specific
    "builtins" listed below, which are not provided by default in any
    current Python version, but which are so general and useful that IMHO
    they ought to be. :-) You only need to do this once, anywhere in your
    code, and the upgraded builtins will be available for the life of that
    invocation of the interpreter.
    
    Builtins currently provided:
    
    - all
    - any
    - reversed
    - sorted
    
    Additional plib-specific "builtins":
    
    - first
    - inverted
    - last
    """
    
    global _upgraded
    if not _upgraded:
        import __builtin__
        for builtin_name in BUILTIN_NAMES:
            if not hasattr(__builtin__, builtin_name):
                import _builtins
                setattr(__builtin__, builtin_name,
                    getattr(_builtins, builtin_name))
        for extra_name in EXTRA_NAMES:
            import _extras
            setattr(__builtin__, extra_name, getattr(_extras, extra_name))
        _upgraded = True

# *************** end of 'internal' functions for this module ***************

# Now we do the ModuleProxy magic to make classes in
# our sub-modules appear in our namespace

excludes = ['_builtins', '_extras',
    '_defaultdict', '_namedtuple',
    'coll', 'decotools', 'func', 'imp', 'options']

ModuleProxy(__name__).init_proxy(__name__, __path__, globals(), locals(),
    excludes=excludes)

# Now clean up our namespace
del ModuleProxy
