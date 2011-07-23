# Copyright 2010 Oren Zomer <oren.zomer@gmail.com>
#
# This file is part of pypsifas.

# pypsifas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pypsifas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pypsifas.  If not, see <http://www.gnu.org/licenses/>.

from datatypes.deque import deque

from collections import defaultdict
from functools import wraps
import thread
from itertools import izip


class RecursionLockException(AssertionError):
    """
    This error is an assertion error - not just an error of usage.
    """
    pass

_recursion_lock_sets = defaultdict(deque)

def recursion_lock(replace_func, exclude = ()):
    """
    replace_func - the function to use in case of recursion
    exclude - a list\tuple of the names & indexes of the args to ignore when checking for recursion.
    for example, see the pretty_str func, in whchi the 'nesting' variable (given in the kws or
    arg #1) is increased in every sub-call, and by ignoring it we can still find out if a recursive
    call happend.
    """
    def decorator(func):
        dummy = object()
        @wraps(func)
        def new_func(*args, **kws):
            recursion_lock_set = _recursion_lock_sets[thread.get_ident()]
            if len(exclude) == 0:
                key_args = args
                key_kws = kws
            else:
                key_args = tuple(arg for ind, arg in enumerate(args) if ind not in exclude)
                key_kws = kws.copy()
                for name in exclude:
                    key_kws.pop(name, None)
            for (rec_func, rec_args, rec_kws) in recursion_lock_set:
                if (func is rec_func) and \
                   (len(key_args) == len(rec_args)) and \
                   all(key_arg is rec_arg for (key_arg, rec_arg) in izip(key_args, rec_args)) and \
                   (len(key_kws) == len(rec_kws)) and \
                   all((value is rec_kws.get(name, dummy)) for (name, value) in key_kws.iteritems()):
                    return replace_func(*args, **kws)
            recursion_key = (func, key_args, key_kws)
            recursion_lock_set.append(recursion_key)
            try:
                rle = None
                return func(*args, **kws)
            except RecursionLockException, rle:
                raise
            finally:
                if rle is None:
                    try:
                        if recursion_lock_set.pop() is not recursion_key:
                            raise RecursionLockException("the recursion-lock set top key is not the expected value")
                    except IndexError:
                        raise RecursionLockException("the recursion-lock set top key does not exists")
                        
                    if len(recursion_lock_set) == 0:
                        if _recursion_lock_sets.pop(thread.get_ident(), None) is not recursion_lock_set:
                            raise RecursionLockException("the recursion-lock set was misused and is not in the set of all recursion-lock sets")
        return new_func
    return decorator
