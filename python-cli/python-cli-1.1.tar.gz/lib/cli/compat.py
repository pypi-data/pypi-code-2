#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

# We try to keep all compatiblity related functions in this module, so
# that the main body of code can be relatively clean.

# In Python 2.4, Exception is not derived from object, but we'd like to use
# super() on it.

_super = super

def super(type, self):
    if issubclass(type, object):
        return _super(type, self)
    class proxy(object):
        def __init__(self, type, obj):
            object.__setattr__(self, '__type__', type)
            object.__setattr__(self, '__obj__', obj)
        def __getattribute__(self, name):
            def bind(func, self):
                def _f(*args):
                    func(self, *args)
                return _f
            type = object.__getattribute__(self, '__type__')
            obj = object.__getattribute__(self, '__obj__')
            return bind(getattr(type, name), obj)
    base = type.__bases__[0]
    return proxy(base, self)
