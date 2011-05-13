# decotrace - Function call/return value logging.
# Copyright (C) 2011 Nathan Wilcox
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
decotrace provides a function, method, and class decorator which sends
messages about call arguments, return values, and exceptions to an
arbitrary output function.

The default output function is to write to sys.stderr, but a common use
case is to provide a logging context.

Example usage:

>>> from decotrace import traced
>>> @traced
... def f(x):
...   return (x, x)
... 
>>> f(42)
f(42)...
f(42) -> (42, 42)
(42, 42)

Using a custom output:
>>> import sys, logging, decotrace
>>> logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
>>> traced = decotrace.TraceContext(logging.getLogger('-decotrace-').debug)
>>> @traced
... def f(x):
...   return x * 2
... 
>>> f(7)
DEBUG:-decotrace-:f(7)...
DEBUG:-decotrace-:f(7) -> 14
14
"""

__VERSION__ = '0.1.4'

import sys
import inspect
from types import ClassType, FunctionType, MethodType


class TraceContext (object):
    def __init__(self, output = lambda s: sys.stderr.write(s + '\n')):
        self._output = output
        self._depth = 0

    def __call__(self, thing):
        t = type(thing)
        if t is FunctionType:
            return self._wrap_funclike(thing)
        elif t is MethodType:
            return self._wrap_function(thing)
        elif t in [type, ClassType]:
            return self._wrap_type(thing)
        else:
            raise NotImplementedError('Cannot wrap: {0!r}'.format(t))
        
    # Private:
    def _log(self, tmpl, *args, **kw):
        prefix = '  ' * self._depth
        self._output('{0}{1}'.format(prefix, tmpl.format(*args, **kw)))

    def _wrap_funclike(self, c):
        (argnames, _, _, _) = inspect.getargspec(c)
        if argnames and argnames[0] == 'self':
            return self._wrap_method(c)
        else:
            return self._wrap_function(c)

    def _wrap_method(self, m):
        def wrapped(wrappedSelf, *args, **kw):
            name = '{0}[@{1:08x}].{2}'.format(
                wrappedSelf.__class__.__name__,
                id(self),
                m.__name__)
            fullArgs = (wrappedSelf,) + args
            return self._trace_call(name, 1, m, fullArgs, kw)
        return wrapped

    def _wrap_function(self, f):
        name = f.__name__
        return lambda *a, **kw: self._trace_call(name, 0, f, a, kw)

    def _wrap_type(self, basetype):
        classdict = {}
        for n, v in vars(basetype).items():
            if type(v) is FunctionType:
                v = self(v)
            classdict[n] = v
        if type(basetype) is ClassType:
            bases = (basetype, object)
        else:
            bases = (basetype,)
        return type(basetype.__name__, bases, classdict)

    def _trace_call(self, name, argStart, f, args, kw):
        argDesc = self._describeArgs(args[argStart:], kw)
        self._log('{0}{1}...', name, argDesc)
        try:
            self._depth += 1
            try:
                result = f(*args, **kw)
            finally:
                self._depth -= 1
        except Exception, e:
            self._log('{0}{1} raising {2!r}', name, argDesc, e)
            raise
        else:
            self._log('{0}{1} -> {2!r}', name, argDesc, result)
            return result

    @staticmethod
    def _describeArgs(args, kw):
        fields = [ repr(a) for a in args ]
        fields.extend( [ '{0}={1!r}'.format(k, v) for (k, v) in sorted(kw.items()) ] )
        return '({0})'.format(', '.join(fields))


traced = TraceContext()
