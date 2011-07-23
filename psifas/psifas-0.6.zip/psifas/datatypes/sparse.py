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
from datatypes.abstract import Abstract, Bottom, BottomClass, is_abstract
from datatypes.pretty import Pretty
from recursion_lock import recursion_lock
from datatypes.dummy import DummyPayload, BottomTuple, length_compare
from scapy_packet import is_sequence_type
import imerge

from sys import maxint


from itertools import izip
from copy import deepcopy

def sequence_sum(a, b):
    if type(a) != type(b):
        if not (isinstance(a, tuple) or isinstance(a, BottomTuple)):
            a = tuple(a)
        if not (isinstance(b, tuple) or isinstance(b, BottomTuple)):
            b = tuple(b)
    return a + b

class _SparseList(Abstract, Pretty):
    def __init__(self, inner = ()):
        super(_SparseList, self).__init__()
        self.inner = inner
        
    def listify(self):
        """
        Called whenever we want to make sure that the inner is a list.
        """
        if not isinstance(self.inner, list):
            self.inner = list(self.inner)

    def _hole(self, sequence):
        return sequence

    def __getitem__(self, key):
        if isinstance(key, slice):
            if (key.start is not None and key.start < 0) or (key.stop is not None and key.stop < 0):
                raise IndexError("Cannot retrieve a negative slice of a sparse-list - unknown length")
            step = key.step or 1
            if step > 0:
                if key.stop is None:
                    return self.__class__(self.inner[key])
                elif len(self.inner) == 0:
                    # TODO: is it ok to return a "tuple" here?
                    start, stop, step = key.indices(maxint)
                    # max(0, ..) is already done in BottomTuple.__new__
                    return self._hole(BottomTuple((stop - start / step)))
                else:
                    self.listify()
                    return self._hole((self.inner + ([Bottom] * key.stop))[key])
            else:
                if key.start is None:
                    raise IndexError("Cannot retrieve a slice with unknown start and negative step - unknown length")
                elif len(self.inner) == 0:
                    # TODO: is it ok to return a "tuple" here?
                    start, stop, step = key.indices(maxint)
                    return self._hole(BottomTuple((stop - start / step)))
                else:
                    self.listify()
                    return self._hole((self.inner + ([Bottom] * (key.start + 1)))[key])
        if key < 0:
            raise IndexError("Cannot retrieve a negative index in a sparse-list - unknown length")
        if key >= len(self.inner):
            return Bottom
        return self.inner[key]

    def __setitem__(self, key, value):
        self.listify()
        if isinstance(key, slice):
            if (key.start is not None and key.start < 0) or (key.stop is not None and key.stop < 0):
                raise IndexError("Cannot retrieve a negative slice of a sparse-list - unknown length")
            self.inner.extend(BottomTuple(max(key.start, key.stop) + 1 - len(self.inner)))
        elif key < 0:
            raise IndexError("Cannot retrieve a negative index in a sparse-list - unknown length")
        elif key >= len(self.inner):
            self.inner.extend(BottomTuple(key + 1 - len(self.inner)))
        return self.inner.__setitem__(key, value)

    def min_length(self):
        """
        returns the minimal length.
        """
        for index in xrange(len(self.inner), 0, -1):
            if self.inner[index - 1] is not Bottom:
                return index
        return 0

class SparseList(_SparseList):
    @recursion_lock(lambda self, other: (self, False))
    def imerge(self, other):
        if is_sequence_type(other):
            result, _ = imerge.imerge_sequence_sparselist(other, self)
            return result, True
        if isinstance(other, SparseList):
            self.listify()
            inner_prefix, flag = imerge.imerge_sequence_sequence_min_length(self.inner, other.inner)
            if len(self.inner) < len(other.inner):
                flag = True
                self.inner = inner_prefix
                self.inner.extend(other.inner[len(inner_prefix):])
            else:
                self.inner = inner_prefix + self.inner[len(other.inner):]
                
            return self, flag
        if isinstance(other, BottomClass):
            return self, False
        raise MergeException("Cannot merge %s" % (self.__class__.__name__,), self, other)

    def __add__(self, other):
        if is_sequence_type(other) or isinstance(other, SparseList):
            # TODO: anything better then deepcopy, which is still safe?
            # cannot get a more concrete value...
            return self
        return NotImplemented

    def __radd__(self, other):
        if is_sequence_type(other):
            return SparseList(list(other) + self.inner)
        return NotImplemented
    

class SparseString(_SparseList):
    @recursion_lock(lambda self, other: (self, False))
    def imerge(self, other):
        if isinstance(other, str):
            result, _ = imerge.imerge_string_sparsestring(other, self)
            return result, True
        if isinstance(other, Prefix):
            result, _ = other.imerge_sparsestring(self)
            return result, True
        if isinstance(other, SparseString):
            if self is other:
                return self, False
            self.inner, flag = imerge.imerge_sequence_sequence_min_length(self.inner, other.inner)
            if len(self.inner) < len(other.inner):
                flag = True
                self.listify()
                self.inner.extend(other.inner[len(self.inner):])
            return self, flag
        if isinstance(other, BottomClass):
            return self, False
        raise MergeException("Cannot merge SparseString with this type of object", self, other)

    def _hole(self, sequence):
        return HoleString(sequence)

    def __add__(self, other):
        if isinstance(other, str) or isinstance(other, SparseString) or isinstance(other, Prefix):
            # TODO: anything better then deepcopy, which is still safe?
            # cannot get a more concrete value
            return deepcopy(self)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return self.radd_iterable(other)
        return NotImplemented

    def radd_iterable(self, other):
        self_inner = self.inner

        return SparseString(sequence_sum(other, self.inner))


class Prefix(Abstract, Pretty):
    def __new__(cls, inner, min_length = 0):
        self = super(Prefix, cls).__new__(cls)
        self.inner = inner
        self.min_length = min_length
        return self.try_concrete()[0]

    def __deepcopy__(self, memo):
        instance = memo.get(self, None)
        if instance is not None:
            return instance
        memo[self] = instance = super(Prefix, self).__new__(self.__class__)
        instance.inner = deepcopy(self.inner, memo)
        instance.min_length = deepcopy(self.min_length, memo)
        return instance

    def is_hole_string(self):
        return not isinstance(self.inner, SparseString) and len(self.inner[:self.min_length + 1]) == self.min_length

    def __repr__(self):
        if self.is_hole_string():
            return self.__repr_holestring()
        return super(Prefix, self).__repr__()

    @recursion_lock(lambda self: 'HoleString(...)')
    def __repr_holestring(self):
        return 'HoleString(%r)' % (self.inner,)

    def try_concrete(self, flag = True):
        if not flag:
            return self, False
        # converts lists and tuples to strings if possible
        if not is_abstract(self.inner) and not isinstance(self.inner, str):
            self.inner = ''.join(self.inner)
            
        # Not allowed to have Prefix of objects without length
        # except for SparseString.
        # The inner_slice is required in the case of DummyPayload - don't read
        # unnecessary data.
        if not isinstance(self.inner, SparseString):
            inner_slice = self.inner[:self.min_length+1]
            inner_length = len(inner_slice)
            if inner_length == self.min_length:
                if not is_abstract(inner_slice):
                    return inner_slice, True
            elif inner_length < self.min_length:
                raise MergeException("There cannot be a payload longer then %r, which is a prefix of this payload" % (self.min_length,), self.inner)
        elif self.min_length == 0 and self.inner.min_length() == 0:
            # a prefix of an empty SparseString is equivalent to an empty SparseString
            return SparseString(), True
        return self, flag
        
    def imerge_sparsestring(self, other):
        other_min_length = other.min_length()
        # TODO: in case self.inner has __setitem__, should we make it more efficient?
        if is_abstract(self.inner):
            # slice setting may not be allowed...
            inner_prefix, flag = imerge.imerge_unwrapped(self.inner[:other_min_length], other)
            if isinstance(inner_prefix, Prefix):
                # both self.inner and were SparseStrings
                # limiting the size of self.inner created a HoleString
                inner_prefix = inner_prefix.inner
            if flag:
                inner_suffix = self.inner[other_min_length:]
                if isinstance(inner_suffix, SparseString):
                    self.inner = inner_suffix.radd_iterable(inner_prefix)
                else:
                    self.inner = sequence_sum(inner_prefix, inner_suffix)
        else:
            # not abstract, nothing to set.
            imerge.imerge_unwrapped(self.inner[:other_min_length], other)
            flag = False
            
        if self.min_length < other_min_length:
            self.min_length = other_min_length
            flag = True
        # in case inner is a DummyPayload, I don't want to read all of it...
        return self.try_concrete(flag)

    def imerge_prefix(self, other):
        # imerge with another prefix
        if self is other:
            return self, False
        flag = False
        if self.min_length < other.min_length:
            self.min_length = other.min_length
            flag = True
        if self.inner == other.inner:
            return self.try_concrete(flag)
            
        if isinstance(other.inner, BottomTuple):
            # This case is easy
            if length_compare(self.inner, other.inner) <= 0:
                # self.inner is shorter then other.inner
                return self.try_concrete(flag)
            self.inner = self.inner[:len(other.inner)]
            return self.try_concrete()

        # we have to do it the hard way: find the maximal sequence that matches both prefixes
        both_sparse_string = isinstance(self.inner, SparseString) and isinstance(other.inner, SparseString)
        if both_sparse_string:
            other_inner = other.inner[:max(self.inner.min_length(), other.inner.min_length())]
            if isinstance(other_inner, Prefix):
                # it must be a HoleString
                other_inner = other_inner.inner
        else:
            other_inner = other.inner
            test_longer = False
            if not flag:
                if isinstance(self.inner, SparseString):
                    flag = True # we're going to have a limited length prefix
                elif not isinstance(other.inner, SparseString):
                    test_longer = True
            
        new_inner = None
        bottom_tuple_length = 0
        self_inner_iter = iter(self.inner)
        for index, (self_element, other_element) in enumerate(izip(self_inner_iter, iter(other_inner))):
            try:
                new_element, new_flag = imerge.imerge_unwrapped(self_element, other_element)
            except MergeException:
                flag = True
                break
            if new_flag:
                flag = True
            if new_element is Bottom:
                if new_inner is None:
                    bottom_tuple_length += 1
                    continue
            elif new_inner is None:
                new_inner = [Bottom] * bottom_tuple_length
            new_inner.append(new_element)
                
        if new_inner is None:
            new_inner = BottomTuple(bottom_tuple_length)
                    
        if both_sparse_string:
            new_inner = SparseString(new_inner)
        elif test_longer and not flag:
            try:
                self_inner_iter.next()
            except StopIteration:
                pass
            else:
                # the inner length shrinked
                flag = True
            
        self.inner = new_inner
        return self.try_concrete(flag)
    
    def imerge(self, other):
        if isinstance(other, str):
            result, _ = imerge.imerge_string_prefix(other, self)
            return result, True
        if isinstance(other, SparseString):
            return self.imerge_sparsestring(other)
        if isinstance(other, Prefix):
            return self.imerge_prefix(other)
        if isinstance(other, BottomClass):
            return self, False
        raise MergeException("Cannot merge Prefix with this type of object", self, other)

    def __add__(self, other):
        # TODO: deepcopy of the inner[..] ?
        if not self.is_hole_string():
            if isinstance(other, str) or isinstance(other, SparseString) or isinstance(other, Prefix):
                return SparseString(self.inner[:self.min_length])
            return NotImplemented
        if isinstance(other, str):
            return HoleString(sequence_sum(self.inner, other))
        if isinstance(other, SparseString):
            return SparseString(sequence_sum(self.inner, other.inner))
        if isinstance(other, Prefix):
            if isinstance(other.inner, SparseString):
                return Prefix(other.inner.radd_iterable(self.inner),
                              min_length = self.min_length + other.min_length)
            return Prefix(sequence_sum(self.inner, other.inner),
                          min_length = self.min_length + other.min_length)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            if isinstance(self.inner, list):
                other = list(other)
            elif isinstance(self.inner, tuple) or isinstance(self.inner, BottomTuple):
                other = tuple(other)
            # otherwise, the inner may be SparseString
            return Prefix(other + self.inner, len(other) + self.min_length)
        return NotImplemented

def HoleString(sequence):
    if isinstance(sequence, Prefix) and sequence.is_hole_string():
        return sequence
    return Prefix(sequence, len(sequence))

def prefix_from_offset(sequence, offset):
    if isinstance(sequence, Prefix):
        # min_length = max(0, sequence.min_length - offset)
        return Prefix(sequence.inner[offset:])
    return Prefix(sequence[offset:])

def abstract_slice(sequence, start, stop = None):
    # assumes stop is None or stop > start
    if isinstance(sequence, Prefix):
        if stop is None:
            return Prefix(sequence.inner[start:], min_length = max(0, sequence.min_length - start))
        else:
            return HoleString(sequence.inner[start:stop])
    return sequence[start:stop]
