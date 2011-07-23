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

from psifas_exceptions import MergeException
from scapy_packet import ScapyPacket, ScapyNoPayload

import datatypes
from datatypes.abstract import BottomClass, Bottom, is_abstract, MaybeNumberType

from scapy_packet import is_sequence_type

from itertools import izip
import operator

def imerge_sequence_sequence_min_length(a, b):
    new_a = list(a)
    total_merge_flag = False
    for index, (sub_a, sub_b) in enumerate(izip(a, b)):
        new_a[index], merge_flag = imerge_unwrapped(sub_a, sub_b)
        if merge_flag:
            total_merge_flag = True
    if isinstance(a, tuple):
        new_a = tuple(new_a)
    return new_a, total_merge_flag

def imerge_sequence_sequence(a, b):
    if len(a) != len(b):
        return MergeException("Sequences have different lengths", a, b)
    if isinstance(b, datatypes.dummy.BottomTuple):
        return a, False
    if isinstance(a, datatypes.dummy.BottomTuple):
        return b, True
    if tuple(a) == tuple(b):
        return a, False
    return imerge_sequence_sequence_min_length(a, b)

def imerge_sequence_sparselist(a, b):
    if len(a) < b.min_length():
        raise MergeException("Sparse list to merge contains non-bottom elements in indexes beyond the list's length", a, b)
    return imerge_sequence_sequence_min_length(a, b)

def imerge_sequence(a, b):
    if is_sequence_type(b):
        return imerge_sequence_sequence(a, b)
    # TODO: think again about the SparseString here... may be called from Prefix.imerge_sparsestring
    if isinstance(b, datatypes.sparse.SparseList) or isinstance(b, datatypes.sparse.SparseString):
        return imerge_sequence_sparselist(a, b)
    raise MergeException("Cannot merge sequence with this type of object", a, b)


def imerge_string_sparsestring(a, b):
    min_length = b.min_length()
    if len(a[:min_length]) < min_length:
        raise MergeException("Sparse string to merge contains non-bottom elements in indexes beyond the string's length", a, b)
    imerge_sequence_sequence_min_length(a, b)
    return a, False

def imerge_string_prefix(a, b):
    if len(a[:b.min_length]) < b.min_length:
        raise MergeException("The datatypes.sparse.Prefix object requires the string to be longer", a, b)
    if isinstance(b.inner, datatypes.sparse.SparseString):
        a_slice = a[:b.inner.min_length()]
        imerge_sequence_sequence_min_length(a_slice, b.inner)
    else:
        if datatypes.dummy.length_compare(a, b.inner) > 0:
            raise MergeException("The datatypes.sparse.Prefix object requires the string to be shorter", a, b)
        b_slice = b.inner[:len(a)]
        if a != b_slice:
            imerge_sequence_sequence(a, b_slice)
    return a, False

def imerge_string(a, b):
    if isinstance(b, str):
        # string with same string?
        if a == b:
            return a, False
        raise MergeException("Cannot merge different strings", a, b)
    elif isinstance(b, datatypes.sparse.SparseString):
        return imerge_string_sparsestring(a, b)
    elif isinstance(b, datatypes.sparse.Prefix):
        return imerge_string_prefix(a, b)
    elif isinstance(b, BottomClass):
        # A merge of any value with BottomClass will return the samve value.
        # If both values are BottomClass, their imerge will be called.
        return a, False
    raise MergeException("Cannot merge string with this type of object", a, b)
    

def _builtins_imerge(a, b):
    """
    How merge works for types that does not have the imerge function
    """
    common_imerge_func = _builtins_imerge_common.get((type(a), type(b)), None)
    if common_imerge_func is not None:
        return common_imerge_func(a, b)

    if isinstance(a, str):
        return imerge_string(a, b)

    if is_sequence_type(a):
        # list imerge
        return imerge_sequence(a, b)
            
    if operator.isNumberType(a):
        if operator.isNumberType(b) and (isinstance(a, float) or isinstance(b, float)):
            if abs(a - b) < 5e-15:
                return a, False
            raise MergeException("Different numbers: %r, %r" % (a, b))
        if b is MaybeNumberType:
            return a, False

    if isinstance(a, ScapyPacket) and isinstance(b, ScapyPacket) and str(a) == str(b):
        a_layer = a
        b_layer = b
        while not isinstance(a_layer, ScapyNoPayload) or not isinstance(b_layer, ScapyNoPayload):
            if a_layer.__class__ is not b_layer.__class__:
                break
            a_layer = a_layer.payload
            b_layer = b_layer.payload
        else:
            return a, False

    if a is None and b is MaybeNumberType:
        return a, False

    raise MergeException('different concrete values or abstract values that cannot be merged', a, b)

def imerge_unwrapped(a, b):
    """
    Tries to inclusive-merge 'a' with 'b'.
    Returns 2 values:
    - the merged value (if it was inclusive, it will be the object 'a')
    - a boolean whether the merge did any changes
    """
    if (a is b) or (a == b):
        return a, False
    if isinstance(b, BottomClass) and not isinstance(a, BottomClass):
        # A merge of any value with BottomClass will return the samve value.
        # If both values are BottomClass, their imerge will be called.
        return a, False
    return getattr(a.__class__, 'imerge', _builtins_imerge)(a, b)

def imerge(a, b):
    try:
        result, flag = imerge_unwrapped(a, b)
        if isinstance(result, datatypes.sparse.Prefix):
            if result.is_hole_string() and not is_abstract(result.inner):
                result = ''.join(result.inner)
        return result, flag
    except MergeException, e:
        raise MergeException("inner merge failure: %s" % (e.args[0],), a, b, *e.args[1:])

_builtins_imerge_common = {(list, list): imerge_sequence_sequence,
                           (tuple, tuple): imerge_sequence_sequence,
                           (list, tuple): imerge_sequence_sequence,
                           (tuple, list): imerge_sequence_sequence}
