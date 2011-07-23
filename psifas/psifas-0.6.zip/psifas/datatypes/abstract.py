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

import operator
from datatypes.singleton import Singleton
from scapy_packet import is_sequence_type
from psifas_exceptions import MergeException

class Abstract(object):
    pass

def is_abstract(*args):    
    scanned_seqs = []
    while len(args) > 0:
        next_args = []
        for arg in args:
            if isinstance(arg, Abstract):
                return True
            if is_sequence_type(arg) and not isinstance(arg, str) and \
               not any(arg is seq for seq in scanned_seqs):
                scanned_seqs.append(arg)
                next_args.extend(arg)
        args = next_args
    return False

class BottomClass(Abstract):
    bottom_hierarchy = 0

    def _bottom_key(self):
        return (self.bottom_hierarchy, self)
    
    def imerge(self, other):
        if not isinstance(other, BottomClass):
            # TODO: No deepcopy here?
            return other, True
        better = max(self, other, key = BottomClass._bottom_key)
        return better, better is other

class Bottom(Singleton, BottomClass):
    __slots__ = []

    bottom_hierarchy = 1

    def __nonzero__(self):
        return False
    # for python3:
    __bool__ = __nonzero__

class Default(Singleton, BottomClass):
    """
    The difference between Bottom, AcceptAll, and Default is in the parsing-dependency.
    When the _parse function returns Bottom, it means that it failed to calculate what it needs,
    and if it keeps happening with incrementation of 'process', an exception will be raised on
    'missing dependencies'.
    When the _parse function returns AcceptAll, it means that the calculation has finished, but
    nothing will be put in the context. Therefore other Psifases that depend on this context may
    not be executed until someone else puts a real value in that context - the context stays
    with Bottom.
    When the _parse function returns Default, the context's value is filled with Default. This
    value can dumb-merge with any other value. The other Psifases will be fully executed, and
    will se the value Default in that context.
    """
    __slots__ = []
    
    bottom_hierarchy = 2

Ignore = Default

class AcceptAll(Singleton, BottomClass):
    # bottom_hirerchy is 0 - never will be merged into any context value,
    # because they start with "Bottom".
    pass

class MaybeNumberType(Singleton, Abstract):
    def imerge(self, other):
        if operator.isNumberType(other) or other is None:
            return other, True
        if isinstance(other, BottomClass):
            return self, False
        raise MergeException("The value is not a number or None", other)
        

