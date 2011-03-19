# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

__docformat__ = 'reStructuredText'

from .overloader import Overloader

def overloaded(overloads, is_method = True):
    """
    Overloads an operation.
    
    The decorated operation is replaced entirely, its docstring is copied to
    the replacement operation.

    The returned operation has a process_args function, see
    `Overloader.process_args` for documentation.

    Parameters:

        `overloads` :: (Overload...)
            a collection of rules indicating which operation to call for which
            combination of arguments. At least one overload must be given.

        `is_method` :: bool
            If True, the decorated is considered to be a method and a self
            parameter is added to each overload automatically (don't add self
            parameters manually). If False, the decorated is treated as a
            function.

    Usage example::

        def __init_xy(self, x, y):
            self.__storage = Storage(x, y)

        def __init_storage(self, storage):
            self.__storage = storage

        @overloaded((
            Overload(__init_xy,
                Param("x", default=0),
                Param("y", default=0)),
            Overload(__init_storage,
                Param("storage"))))
        def __init__(self):
            "docstring"
            pass
    """
    overloader = Overloader(overloads, is_method)

    # replacement for the decorated
    def __overloaded(*args, **kwargs):
        return overloader.process_call(*args, kwargs=kwargs)

    def _overloaded(f):
        __overloaded.__doc__ = f.__doc__
        __overloaded.process_args = overloader.process_args
        return __overloaded

    return _overloaded

