"""
Various utility functions

Copyright (c) 2009 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

email: contact@picloud.com

The cloud package is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this package; if not, see 
http://www.gnu.org/licenses/lgpl-2.1.html
"""

import sys
import types
import ctypes
import cPickle
import inspect
from functools import partial

def islambda(func):
    return func.func_name == '<lambda>'

def funcname(func):
    module = ""
    if hasattr(func,'__module__'):
        module = (func.__module__ if func.__module__ else '__main__')
    """Return a human readable name associated with a function"""
    if inspect.ismethod(func):
        nme = '.'.join([module,func.im_class.__name__,func.__name__]) 
    elif inspect.isfunction(func):
        nme =  '.'.join([module,func.__name__])
    elif inspect.isbuiltin(func):
        return  '.'.join([module,func.__name__])
    elif isinstance(func,partial):
        return 'partial_of_' + funcname(func.func)    
    else:
        raise ValueError("cannot deal with type: ", type(func))
    nme +=  ' at ' + ':'.join([func.func_code.co_filename,str(func.func_code.co_firstlineno)])
    return nme 
    
def numargs(func):
    """Return number of (required) args this function has"""
    if inspect.isfunction(func):
        op_args = len(func.func_defaults) if func.func_defaults else 0 
        return func.func_code.co_argcount - op_args
    elif inspect.ismethod(func):
        op_args = len(func.im_func.func_defaults) if func.im_func.func_defaults else 0
        return func.im_func.func_code.co_argcount - op_args - 1
    raise ValueError('cannot deal with type: %s' % type(func))
    
    
"""Ordered Dictionary"""
import UserDict
class OrderedDict(UserDict.DictMixin):
    
    def __init__(self):
        self._keys = []
        self._data = {}
        
        
    def __setitem__(self, key, value):
        if key not in self._data:
            self._keys.append(key)
        self._data[key] = value
    
    def insertAt(self, loc, key, value):
        if key in self._data:
            del self._data[self._data.index(key)]
        self._keys.insert(loc, key)
        self._data[key] = value
        
    def __getitem__(self, key):
        return self._data[key]
    
    
    def __delitem__(self, key):
        del self._data[key]
        self._keys.remove(key)
        
        
    def keys(self):
        return list(self._keys)    
    
    def copy(self):
        copyDict = OrderedDict()
        copyDict._data = self._data.copy()
        copyDict._keys = self._keys[:]
        return copyDict
    
"""Python 2.5 support"""
from itertools import izip, chain, repeat
if sys.version_info[:2] < (2,6):
    def izip_longest(*args):
        def sentinel(counter = ([None]*(len(args)-1)).pop):
            yield counter()         # yields the fillvalue, or raises IndexError
        fillers = repeat(None)
        iters = [chain(it, sentinel(), fillers) for it in args]
        try:
            for tup in izip(*iters):
                yield tup
        except IndexError:
            pass
