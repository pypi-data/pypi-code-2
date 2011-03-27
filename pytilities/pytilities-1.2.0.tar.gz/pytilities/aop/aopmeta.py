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

from .advisor import advisor
from .functions import _wrapped_callable

def _make_attrs(base):
    # obj: either cls, or self, as in class (produced
    # by meta) and instance (produced by class)
    def __getattribute__(obj, name):
        if not advisor.is_advisable(name):
            return AOPMeta._getattr(obj, base, name)

        retval = advisor.process_call(
            obj, name, 
            lambda s: AOPMeta._getattr(s, base, name), 
            'get', (obj,), {})

        # must wrap callables, to advice the call
        if callable(retval): 
            return _wrapped_callable(obj, name, retval)
        else:
            return retval

    def __setattr__(obj, name, value):
        if not advisor.is_advisable(name):
            return AOPMeta._setattr(obj, base, name, value),

        retval = advisor.process_call(
            obj, name, 
            lambda s, v: AOPMeta._setattr(s, base, name, v),
            'set', (obj, value), {})
        assert retval is None, 'setter should return None'

    def __delattr__(obj, name):
        if not advisor.is_advisable(name):
            return AOPMeta._delattr(obj, base, name),

        retval = advisor.process_call(
            obj, name, 
            lambda s: AOPMeta._delattr(s, base, name),
            'delete', (obj,), {})
        assert retval is None, 'deleter should return None'


    return __getattribute__, __setattr__, __delattr__


class AOPMeta(type):
    '''
    Follows advice rules as described by `Advisor`
    '''

    def __init__(cls, name, bases, dictionary):
        (cls.__getattribute__, 
         cls.__setattr__, cls.__delattr__) = _make_attrs(object)

        super().__init__(name, bases, dictionary)

    def _getattr(obj, base, name): 
        # note that this still calls __getattr__ if needed
        return base.__getattribute__(obj, name)

    # Note that set and delete happen on the object itself, never on one of its
    # bases, ... If not found on the obj, it will be added to the obj.
    def _setattr(obj, base, name, value):
        base.__setattr__(obj, name, value) # directly set on our dict

    def _delattr(obj, base, name):
        base.__delattr__(obj, name)

    (__getattribute__, __setattr__, __delattr__) = _make_attrs(type)

