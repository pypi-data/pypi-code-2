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

from base import *
from switch import *
from datatypes.sparse import Prefix

import operator
import struct
import socket
from datetime import datetime
from functools import partial

UB_SHORT_STRUCT = struct.Struct('>H')
SB_SHORT_STRUCT = struct.Struct('>h')
UL_SHORT_STRUCT = struct.Struct('<H')
SL_SHORT_STRUCT = struct.Struct('<h')

UB_LONG_STRUCT = struct.Struct('>L')
SB_LONG_STRUCT = struct.Struct('>l')
UL_LONG_STRUCT = struct.Struct('<L')
SL_LONG_STRUCT = struct.Struct('<l')

FB_STRUCT = struct.Struct('>f')
FL_STRUCT = struct.Struct('<f')

DB_STRUCT = struct.Struct('>d')
DL_STRUCT = struct.Struct('<d')

S_CHAR_STRUCT = struct.Struct('b')

class UBInt(Psifas):
    def __init__(self, target):
        if operator.isNumberType(target):
            target = Segment(target)
        elif isinstance(target, str):
            target = Link('.../' + target)
        super(UBInt, self).__init__(UniqueField('payload', target))

    _parse_by_size = {0: lambda buf: 0,
                      1: ord,
                      2: lambda buf: UB_SHORT_STRUCT.unpack(buf)[0],
                      4: lambda buf: UB_LONG_STRUCT.unpack(buf)[0]}

    _build_by_size = {0: lambda num: '',
                      1: chr,
                      2: UB_SHORT_STRUCT.pack,
                      4: UB_LONG_STRUCT.pack}

    @staticmethod
    def _parse_iteration(x, y):
        return (x * 0x100) + ord(y)

    @classmethod
    def parse_number(cls, buf):
        return reduce(cls._parse_iteration, buf, 0)

    @staticmethod
    def build_number(number, size):
        return ''.join(chr((number >> (8 * index)) & 0xFF) for index in xrange(size - 1, -1, -1))

    @classmethod
    def _decipher(cls, location, number, buf):
        if not is_abstract(buf):
            number = cls._parse_by_size.get(len(buf), cls.parse_number)(buf)
        elif isinstance(buf, Prefix) and buf.is_hole_string() and not is_abstract(number):
            buf = cls._build_by_size.get(buf.min_length, partial(cls.build_number, size = buf.min_length))(number)
        return number, buf

class ULInt(UBInt):
    _parse_by_size = {0: lambda buf: 0,
                      1: ord,
                      2: lambda buf: UL_SHORT_STRUCT.unpack(buf)[0],
                      4: lambda buf: UL_LONG_STRUCT.unpack(buf)[0]}

    _build_by_size = {0: lambda num: '',
                      1: chr,
                      2: UL_SHORT_STRUCT.pack,
                      4: UL_LONG_STRUCT.pack}

    @classmethod
    def parse_number(cls, buf):
        return reduce(cls._parse_iteration, reversed(buf), 0)

    @staticmethod
    def build_number(number, size):
        return ''.join(chr((number >> (8 * index)) & 0xFF) for index in xrange(size))

class SBInt(UBInt):
    _parse_by_size = {0: lambda buf: 0,
                      1: lambda buf: S_CHAR_STRUCT.unpack(buf)[0],
                      2: lambda buf: SB_SHORT_STRUCT.unpack(buf)[0],
                      4: lambda buf: SB_LONG_STRUCT.unpack(buf)[0]}

    _build_by_size = {0: lambda num: '',
                      1: S_CHAR_STRUCT.pack,
                      2: SB_SHORT_STRUCT.pack,
                      4: SB_LONG_STRUCT.pack}

    @classmethod
    def parse_number(cls, buf):
        return reduce(cls._parse_iteration, buf[1:], S_CHAR_STRUCT.unpack(buf[0])[0])

    @staticmethod
    def build_number(number, size):
        return UBInt.build_number(number % (0x100 ** size), size)

class SLInt(ULInt):
    _parse_by_size = {0: lambda buf: 0,
                      1: lambda buf: S_CHAR_STRUCT.unpack(buf)[0],
                      2: lambda buf: SL_SHORT_STRUCT.unpack(buf)[0],
                      4: lambda buf: SL_LONG_STRUCT.unpack(buf)[0]}

    _build_by_size = {0: lambda num: '',
                      1: S_CHAR_STRUCT.pack,
                      2: SL_SHORT_STRUCT.pack,
                      4: SL_LONG_STRUCT.pack}

    @classmethod
    def parse_number(cls, buf):
        return reduce(cls._parse_iteration, buf[1:], S_CHAR_STRUCT.unpack(buf[0])[0])

    @staticmethod
    def build_number(number, size):
        return ULInt.build_number(number % (0x100 ** size), size)

class UInt(Psifas):
    def __init__(self, endian, target):
        if operator.isNumberType(target):
            target = Segment(target)
        elif isinstance(target, str):
            target = Link('.../' + target)
        if isinstance(endian, str):
            endian = Link('.../' + endian)
        super(UInt, self).__init__(UniqueField('endian', endian),
                                   UniqueField('payload', target))

    deciphers = {'BIG': UBInt._decipher,
                 'LITTLE': ULInt._decipher}
    
    def _decipher(self, location, number, endian, buf):
        if not is_abstract(endian):
            number, buf = self.deciphers[endian](self, number, buf)
        return number, endian, buf

class SInt(UInt):
    deciphers = {'BIG': SBInt._decipher,
                 'LITTLE': SLInt._decipher}

class BInt(Psifas):
    def __init__(self, target, is_signed):
        if operator.isNumberType(target):
            target = Segment(target)
        elif isinstance(target, str):
            target = Link('.../' + target)
        if isinstance(is_signed, str):
            is_signed = Link('.../' + is_signed)
        super(BInt, self).__init__(UniqueField('is_signed', is_signed),
                                   UniqueField('payload', target))

    deciphers = {True: SBInt._decipher,
                 False: UBInt._decipher}
    
    def _decipher(self, location, number, is_signed, buf):
        if not is_abstract(is_signed):
            number, buf = self.deciphers[is_signed](number, buf)
        return number, is_signed, buf

class LInt(BInt):
    deciphers = {True: SLInt._decipher,
                 False: ULInt._decipher}

class GenericInt(ConcretePsifas):
    def __init__(self, target, is_signed, endian, sizer = None):
        if operator.isNumberType(target):
            target = Segment(target)
        elif isinstance(target, str):
            target = Link('.../' + target)
        if isinstance(is_signed, str):
            is_signed = Link('.../' + is_signed)
        if isinstance(endian, str):
            endian = Link('.../' + endian)
        super(GenericInt, self).__init__(UniqueField('is_signed', is_signed),
                                         UniqueField('endian', is_signed),
                                         UniqueField('payload', target))

    deciphers = {(True, 'BIG'): SBInt._decipher,
                 (True, 'LITTLE'): SLInt._decipher,
                 (False, 'BIG'): UBInt._decipher,
                 (False, 'LITTLE'): ULInt._decipher}

    def _decipher(self, location, number, is_signed, endian, buf):
        if not is_abstract(is_signed, endian):
            number, buf = self.deciphers[is_signed, endian](number, buf)
        return number, is_signed, endian, buf
    

class Operator1(ConcretePsifas):
    def __init__(self, arg):
        if isinstance(arg, str):
            arg = Link('.../' + arg)
        super(Operator1, self).__init__(UniqueField('%s_of' % (self.__class__.__name__.lower(),), arg))

    def _decipher(self, location, value, arg):
        value, arg = super(Operator1, self)._decipher(location, value, arg)
        if value is Bottom:
            return value, arg
        arg = location.imerge(arg, self._build(value))
        return value, arg
    
    def _build(self, value):
        return Bottom

    def _parse(self, value):
        raise NotImplementedError

class Operator2(ConcretePsifas):
    def __init__(self, left, right):
        super(Operator2, self).__init__(UniqueField('%s_left'  % (self.__class__.__name__.lower(),), left),
                                        UniqueField('%s_right'  % (self.__class__.__name__.lower(),), right))

    def _decipher(self, location, value, left, right):
        value, left, right = super(Operator2, self)._decipher(location, value, left, right)

        if (value is Bottom) or ((left is Bottom) and (right is Bottom)):
            return value, left, right

        left_was_bottom = left is Bottom
        if not left_was_bottom:
            right = location.imerge(right, self._build_right(value, left))

        if right is not Bottom:
            left = location.imerge(left, self._build_left(value, right))

        if left_was_bottom and left is not Bottom:
            right = location.imerge(right, self._build_right(value, left))

        return value, left, right

    def _build_left(self, value, right):
        """
        You may override this function
        """
        return Bottom

    def _build_right(self, value, left):
        """
        You may override this function
        """
        return Bottom

    def _parse(self, left, right):
        """
        This function must be overriden
        """
        raise NotImplementedError

class OperatorN(ConcretePsifas):
    """
    Operators are a limited version of the generic Psifas.
    Like the _parse function in Psifas, which is called if all the fields
    are filled and calculates the result, there can be many build functions
    that will be called if the result is known and all the other fields
    are filled.

    However, if 2 fields are missing (or 1 field and the result-field),
    nothing will be evaluated (there is no generic _decipher function
    like in Psifas, that can receive multiple Bottom as input).

    A classic n-operator is Sum.

    Operator1 and Operator2 are more efficient implementations then OperatorN,
    (for n=1,2) but they basically do the same.
    """
    def __init__(self, *args):
        super(OperatorN, self).__init__(*(UniqueField('%s_arg%d' % (self.__class__.__name__.lower(), index), arg)
                                          for (index, arg) in enumerate(args)))
    def _decipher(self, location, value, *args):
        super_results = super(OperatorN, self)._decipher(location, value, *args)
        value = super_results[0]
        args = list(super_results[1:])

        if value is Bottom:
            return super_results

        missing_index = None
        for index, arg in enumerate(args):
            if arg is not Bottom:
                continue
            if missing_index is not None:
                # 2 are missing
                return super_results
            missing_index = index
        if missing_index is not None:
            args[missing_index] = missing_value = location.imerge(args[missing_index],
                                                                  self._build_index(missing_index, value, args[:missing_index] + args[missing_index + 1:]))
        rebuild_args = [(location.imerge(arg, self._build_index(index, value, args[:index] + args[index + 1:]))
                         if index != missing_index else missing_value)
                        for index, arg in enumerate(args)]
        return [value] + rebuild_args
    
    def _build_index(self, missing_index, value, args):
        raise NotImplementedError

class Sum(OperatorN):
    def _parse(self, *args):
        return sum(args)

    def _build_index(self, index, total_sum, args):
        return total_sum - sum(args)

class ModuloSum(OperatorN):
    def __init__(self, modulo, *args):
        super(ModuloSum, self).__init__(*args)
        self.modulo = modulo # notice - this is NOT a Psifas object.

    def _parse(self, *args):
        if len(self._fields) > 1:
            return sum(args) % self.modulo
        return sum(*args) % self.modulo

    def _build_index(self, index, total_sum, args):
        if len(self._fields) > 1:
            return (total_sum - sum(args)) % self.modulo
        return Bottom

class Length(Operator1):
    _parse = len
Len = Length

class Negative(Operator1):
    _parse = _build = operator.neg
Psifas.__neg__ = lambda self: Negative(self)

class Not(Operator1):
    _parse = operator.not_
    # cannot build: not(not(3)) != 3
Psifas.__not__ = Not

class Invert(Operator1):
    _parse = _build = operator.inv
Psifas.__invert__ = lambda self: Invert(self)

class Reversed(Operator1):
    def reverse(self, value):
        return value[::-1]
    _parse = _build = reverse

Reverse = Reversed

class Concatenate(Operator2):
    _parse = operator.concat

    @staticmethod
    def _build_left(value, right):
        if len(right) == 0:
            return value
        if value[-len(right):] == right:
            return value[:-len(right)]
        return Bottom

    @staticmethod
    def _build_right(value, left):
        if value[:len(left)] == left:
            return value[len(left):]
        return Bottom

Psifas.__concat__ = lambda a,b: Concatenate(a,b)

class Add(Operator2):
    _parse = operator.add

    def _build_symmetric(self, value, arg):
        if operator.isNumberType(value) and operator.isNumberType(arg):
            return value - arg
        if isinstance(value, datetime):
            try:
                return value - arg
            except TypeError:
                pass
        return Bottom
        

    def _build_left(self, value, right):
        if operator.isSequenceType(value) and operator.isSequenceType(right):
            return Concatenate._build_left(value, right)
        return self._build_symmetric(value, right)
    
    def _build_right(self, value, left):
        if operator.isSequenceType(value) and operator.isSequenceType(left):
            return Concatenate._build_right(value, left)
        return self._build_symmetric(value, left)
Psifas.__add__ = lambda a, b: Add(a,b)

class Multiply(Operator2):
    _parse = operator.mul

    def _build(self, value, other):
        if other == 0:
            return Bottom
        if operator.isNumberType(value):
            if value % other == 0:
                return value / other
            return operator.truediv(value, other)
        if operator.isSequenceType(value):
            if operator.isNumberType(other):
                if len(value) % other == 0:
                    if value == value[:len(value) / other] * other:
                        return value[:len(value) / other]
            elif operator.isSequenceType(other):
                if (len(other) != 0) and (len(value) % len(other) == 0):
                    if tuple(value) == tuple(other) * (len(value) / len(other)):
                        return len(value) / len(other)
        return Bottom

    _build_left = _build_right = _build
Psifas.__mul__ = lambda a, b: Multiply(a,b)

class Mod(Operator2):
    _parse = operator.mod
Psifas.__mod__ = lambda a,b: Mod(a,b)

class Div(Operator2):
    _parse = operator.div
Psifas.__div__ = lambda a,b: Div(a,b)

class And_(Operator2):
    _parse = operator.and_
Psifas.__and__ = lambda a,b: And_(a,b)

class Or_(Operator2):
    _parse = operator.or_
Psifas.__or__ = lambda a,b: Or_(a,b)


class Equal(Operator2):
    _parse = operator.eq

    def _build(self, value, arg):
        if value is True:
            return arg
        return Bottom

    _build_right = _build_left = _build

class GreaterThan(Operator2):
    _parse = operator.gt
Psifas.__gt__ = lambda a, b: GreaterThan(a, b)

class GreaterEqual(Operator2):
    _parse = operator.ge
Psifas.__ge__ = lambda a, b: GreaterEqual(a, b)

class LessEqual(Operator2):
    _parse = operator.le
Psifas.__le__ = lambda a, b: LessEqual(a, b)

class LessThan(Operator2):
    _parse = operator.lt
Psifas.__lt__ = lambda a, b: LessThan(a, b)

class LeftShift(Operator2):
    _parse = operator.lshift

    def _build_left(self, value, right):
        return value >> right
Psifas.__lshift__ = lambda a, b: LeftShift

class RightShift(Operator2):
    _parse = operator.rshift
Psifas.__rshift__ = lambda a, b: RightShift
        
class Contains(Operator2):
    _parse = operator.contains





class Ord(Operator1):
    """
    Works on sequences.
    For a single char, use ULInt.
    """
    def _parse(self, buf):
        return [ord(c) for c in buf]

    def _build(self, numbers):
        return ''.join(chr(number) for number in numbers)

class SumSeq(Operator1):
    _parse = sum

class Hex(Operator1):
    def _parse(self, value):
        return value.encode('hex').upper()

    def _build(self, value):
        return value.decode('hex')

class String(Operator1):
    def _parse(self, value):
        return ''.join(value)

    def _build(self, value):
        return tuple(value)

class Upper(Operator1):
    def _parse(self, value):
        return value.upper()

class Lower(Operator1):
    def _parse(self, value):
        return value.lower()

class ToSigned(Operator2):
    """
    converts unsigned numbers to signed numbers
    """
    def _parse(self, unsigned_number, number_of_bits):
        return ((unsigned_number - 2 **(number_of_bits - 1)) % (2**number_of_bits)) - 2 ** (number_of_bits - 1)

    def _build_left(self, signed_number, number_of_bits):
        return signed_number % (2**number_of_bits)

class ToUnsigned(Operator2):
    def _parse(self, signed_number, number_of_bits):
        return signed_number % (2**number_of_bits)

    def _build_left(self, unsigned_number, number_of_bits):
        return ((unsigned_number - 2**(number_of_bits - 1)) % (2**number_of_bits)) - 2 ** (number_of_bits - 1)

class IPAddress(Operator1):
    def __init__(self):
        super(IPAddress, self).__init__(Segment(4))

    _parse = socket.inet_ntoa
    _build = socket.inet_aton

class IPChecksum(Operator1):
    @staticmethod
    def leftover_sum(a, b):
        """
        Assumes a, b < 0x10000
        """
        return ((a + b) & 0xFFFF) + ((a + b) >> 1)

    def _parse(self, buf):
        if len(buf) % 2 == 1:
            buf += '\x00'
        return 0xFFFF - reduce(self.leftover_sum , struct.unpack('>%dH' % (len(buf) / 2,), buf))
        

class GetIndex(Psifas):
    def __init__(self, target, index):
        if isinstance(target, str):
            target = Link('.../' + target)
        if isinstance(index, str):
            index = Link('.../' + index)
        super(GetIndex, self).__init__(UniqueField('target', target),
                                       UniqueField('index', index))

    def _decipher_location(self, location, all_fields):
        values = super(GetIndex, self)._decipher_location_set(location, all_fields)
        # the target can be a abstract
        return all((v is AcceptAll or not is_abstract(v)) for v in (values[:1] + values[2:]))

    def _decipher(self, location, element, target, index):
        if is_abstract(index):
            return element, target, index

        if is_sequence_type(target) or ((isinstance(target, SparseList) or isinstance(target, SparseString)) and
                                        ((not isinstance(index, slice)) or ((index.start is None or index.start < 0) and
                                                                            (index.stop is None or index.stop < 0)))):
            try:
                sliced_target = target[index]
            except IndexError:
                pass
            else:
                element = location.imerge(element, sliced_target)
        try:
            new_target = SparseList()
            new_target[index] = element
        except IndexError:
            pass
        else:
            target = location.imerge(target, new_target)
        
        return element, target, index

    
