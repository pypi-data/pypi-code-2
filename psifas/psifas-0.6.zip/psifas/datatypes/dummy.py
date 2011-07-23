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

from itertools import count
from functools import wraps
from psifas_exceptions import EndOfStreamException, MergeException

from datatypes.pretty import Pretty
from datatypes.abstract import Abstract, Bottom
from datatypes.psifas_stream import PsifasStream

import datatypes.sparse

class DummyPayloadParent(Pretty):
    # TODO: think about keeping a map between every stream and its DummyPayloadParent (In order
    # to prevent from 2 parents using the same stream).
    def __init__(self, stream, payload = ''):
        super(DummyPayloadParent, self).__init__()
        self.stream = stream # should be PsifasStream
        self.payload = payload
        self.finished = False

    def __deepcopy__(self, memo):
        # avoid 2 parents with the same stream (which cannot be deepcopied)
        return self

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.stream, self.payload)

    def read_until(self, index, best_effort = False):
        if len(self.payload) < index + 1:
            try:
                self.payload += self.stream.read(index + 1 - len(self.payload), best_effort = best_effort)
            except EndOfStreamException, e:
                self.finished = True
                raise IndexError("Cannot evaluate dummy-payload-parent at given index", index, e)
        return self.payload[:index + 1]

    def read_all(self):
        self.payload += self.stream.read_all()
        self.finished = True
        return self.payload

class DummyPayload(str, Pretty):
    def __new__(cls, stream, payload = ''):
        if not isinstance(stream, PsifasStream):
            stream = PsifasStream(stream)
        return cls.from_parent(DummyPayloadParent(stream, payload), 0)

    def __deepcopy__(self, memo):
        instance = memo.get(self, None)
        if instance is not None:
            return instance
        memo[self] = instance = super(DummyPayload, self).__new__(self.__class__)
        instance.parent = deepcopy(self.parent, memo)
        instance.offset = deepcopy(self.offset, memo)
        instance.prefix = deepcopy(self.prefix, memo)
        return instance

    @classmethod
    def from_parent(cls, parent, offset, prefix = ''):
        assert offset >= 0, "DummyPayload should not be created with negative offset %r" % (offset,)
        if parent.finished:
            return prefix + parent.payload[offset:]
        instance = super(DummyPayload, cls).__new__(cls)
        instance.parent = parent
        instance.offset = offset
        instance.prefix = prefix
        return instance

    def __str__(self):
        return self.prefix + self.parent.read_all()[self.offset:]

    __repr__ = Pretty.__repr__

    def _read_until(self, index):
        if index >= len(self.prefix):
            return self.prefix + self.parent.read_until(self.offset - len(self.prefix) + index, best_effort = True)[self.offset:]
        return self.prefix[:index + 1]

    def __len__(self):
        return len(str(self))

    def __cmp__(self, other):
        if isinstance(other, DummyPayload):
            self_payload = self._payload()
            other_payload = other._payload()
            min_payload_length = min(len(self_payload), len(other_payload))
            prefix_compare = cmp(self_payload[:min_payload_length], other_payload[:min_payload_length])
            if prefix_compare != 0:
                return prefix_compare
            if self.prefix == other.prefix and self.parent == other.parent and self.offset == other.offset:
                return 0
            return cmp(str(self), str(other))
        if isinstance(other, str):
            return cmp(self._read_until(len(other)), other)
        return str.__cmp__(self, other)

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start
            step = key.step
            stop = key.stop

            if step is None:
                step = 1
            elif step == 0:
                raise ValueError("slice step cannot be zero", key)
            
            if step < 0:
                if (start is None) or (start < 0):
                    return self.read_all()[key]
                return self._read_until(start)[key]
            
            # step > 0
            if stop is not None:
                if (stop < 0) or ((start is not None) and (start < 0)):
                    return self.read_all()[key]
                return self._read_until(stop - step)[key]
            
            # stop is None
            if step != 1:
                return self.read_all()[key]
            
            if start is None:
                start = 0
            elif start < 0:
                return self.read_all()[key]
            if start < len(self.prefix):
                return self.from_parent(self.parent, self.offset, self.prefix[start:])
            return self.from_parent(self.parent, self.offset + start - len(self.prefix))
        if key < 0:
            return self.read_all()[key]
        return self._read_until(key)[key]

    def __iter__(self):
        for index in count():
            try:
                yield self[index]
            except IndexError:
                break

    def __add__(self, other):
        if isinstance(other, str) or isinstance(other, DummyPayload) or isinstance(other, sparse.SparseString) or isinstance(other, Prefix):
            return self.read_all() + other
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return self.from_parent(self.parent, self.offset, other + self.prefix)
        return NotImplemented

    def _payload(self):
        """
        returns the already read payload.
        """
        return self.prefix + self.parent.payload[self.offset:]

    def startswith(self, other):
        return self[:len(other)] == other


def str_wrapper(func):
    def new_func(self, *args, **kws):
        return func(str(self), *args, **kws)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    return new_func

for attr in dir(str):
    if attr in ('__class__', '__getattribute__', '__setattr__', '__init__', '__new__'):
        continue
    original_func = getattr(DummyPayload, attr)
    if getattr(str, attr) == original_func:
        setattr(DummyPayload, attr, str_wrapper(original_func))
            
            
class BottomTuple(Abstract):
    MINIMAL_LENGTH = 2
    
    def __new__(cls, length):
        if length < cls.MINIMAL_LENGTH:
            return (Bottom,) * length
        self = super(BottomTuple, cls).__new__(cls)
        self.length = length
        return self

    def __deepcopy__(self, memo):
        return self
        
    def __repr__(self):
        return "((Bottom,) * %d)" % (self.length,)

    def __len__(self):
        return self.length

    def __iter__(self):
        for index in xrange(self.length):
            yield Bottom

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.indices(self.length)
            return BottomTuple((stop - start) / step)
        if key < 0:
            key = self.length + key
        if key >= self.length:
            raise IndexError("BottomTuple out of range")
        return Bottom

    def evaluate(self):
        return (Bottom,) * self.length

    def __add__(self, other):
        if isinstance(other, BottomTuple):
            return BottomTuple(self.length + other.length)
        return self.evaluate() + other

    def __radd__(self, other):
        if other == ():
            return self
        return other + self.evaluate()

    def __mul__(self, other):
        return self.evaluate() * other

    def __cmp__(self, other):
        if isinstance(other, BottomTuple):
            return cmp(self.length, other.length)
        return cmp(self.evaluate(), other)

        
def length_compare(a, b):
    if not isinstance(a, DummyPayload):
        if not isinstance(b, DummyPayload):
            return cmp(len(a), len(b))
        return cmp(len(a), len(b[:len(a) + 1]))
    elif not isinstance(b, DummyPayload):
        return cmp(len(a[:len(b) + 1]), len(b))
    assert hasattr(a, '__len__') or hasattr(b, '__len__'), "length_compare was called on limitless objects: %r, %r" % (a, b)
    a_iter = iter(a)
    b_iter = iter(b)
    for couple in izip(a_iter, b_iter):
        pass
    try:
        a_iter.next()
        return 1
    except StopIteration:
        pass
    try:
        b_iter.next()
        return -1
    except StopIteration:
        pass
    return 0
