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

S_CHAR_STRUCT = struct.Struct('b')

class UBInt(Psifas):
    def __init__(self, target, sizer = None):
        if operator.isNumberType(target):
            target = Segment(target)
        elif isinstance(target, str):
            target = Link('.../' + target)
        super(UBInt, self).__init__(Field(self.unique('%s_of' % (self.__class__.__name__.lower(),)), target),
                                    Field(self.unique('size'), sizer))
        if sizer is None:
            self._fields[1].psifas = CLink('%s/size' % (self._fields[0].name,))

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

    def _decipher(self, number, buf, size):
        if buf is not NoValue:
            size = len(buf)
            number = self._parse_by_size.get(size, self.parse_number)(buf)
        elif NoValue not in (number, size):
            buf = self._build_by_size.get(size, partial(self.build_number, size = size))(number)
        return number, buf, size

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

class UInt(Switch):
    def __init__(self, is_big_endian_psifas, *args, **kws):
        super(UInt, self).__init__(is_big_endian_psifas, {True: UBInt(*args, **kws), False: ULInt(*args, **kws)})

class SInt(Switch):
    def __init__(self, is_big_endian_psifas, *args, **kws):
        super(SInt, self).__init__(is_big_endian_psifas, {True: SBInt(*args, **kws), False: SLInt(*args, **kws)})

class BInt(Switch):
    def __init__(self, is_signed_psifas, *args, **kws):
        super(BInt, self).__init__(is_unsigned_psifas, {True: SBInt(*args, **kws), False: UBInt(*args, **kws)})

class LInt(Switch):
    def __init__(self, is_signed_psifas, *args, **kws):
        super(LInt, self).__init__(is_unsigned_psifas, {True: SLInt(*args, **kws), False: ULInt(*args, **kws)})

class GenericInt(Switch):
    def __init__(self, is_signed_psifas, is_big_endian_psifas, *args, **kws):
        super(GenericInt, self).__init__(is_signed_psifas, {True: SInt(is_big_endian_psifas, *args, **kws),
                                                            False: UInt(is_big_endian_psifas, *args, **kws)})

class Operator1(Psifas):
    def __init__(self, arg):
        if isinstance(arg, str):
            arg = Link('.../' + arg)
        super(Operator1, self).__init__(Field(self.unique('%s_of' % (self.__class__.__name__.lower(),)), arg))

    def _decipher(self, value, arg):
        value, arg = super(Operator1, self)._decipher(value, arg)
        if value is NoValue:
            return value, arg
        new_arg = self._build(value)
        if new_arg is NoValue:
            new_arg = arg
        return value, new_arg
    
    def _build(self, value):
        return NoValue

    def _parse(self, value):
        raise NotImplementedError

class Operator2(Psifas):
    def __init__(self, left, right):
        super(Operator2, self).__init__(Field(self.unique('%s_left'  % (self.__class__.__name__.lower(),)), left),
                                        Field(self.unique('%s_right'  % (self.__class__.__name__.lower(),)), right))

    def _decipher(self, value, left, right):
        value, left, right = super(Operator2, self)._decipher(value, left, right)

        if (value is NoValue) or ((left is NoValue) and (right is NoValue)):
            return value, left, right

        new_right = right
        if left is not NoValue:
            new_value = self._build_right(value, left)
            if new_value is not NoValue:
                new_right = new_value

        new_left = left
        if right is not NoValue:
            new_value = self._build_left(value, right)
            if new_value is not NoValue:
                new_left = new_value

        return value, new_left, new_right

    def _build_left(self, value, right):
        """
        You may override this function
        """
        return NoValue

    def _build_right(self, value, left):
        """
        You may override this function
        """
        return NoValue

    def _parse(self, left, right):
        """
        This function must be overriden
        """
        raise NotImplementedError

class OperatorN(Psifas):
    """
    Operators are a limited version of the generic Psifas.
    Like the _parse function in Psifas, which is called if all the fields
    are filled and calculates the result, there can be many build functions
    that will be called if the result is known and all the other fields
    are filled.

    However, if 2 fields are missing (or 1 field and the result-field),
    nothing will be evaluated (there is no generic _decipher function
    like in Psifas, that can receive multiple NoValues as input).

    A classic n-operator is Sum.

    Operator1 and Operator2 are more efficient implementations then OperatorN,
    (for n=1,2) but they basically do the same.
    """
    def __init__(self, *args):
        super(OperatorN, self).__init__(*(Field(self.unique('%s_arg%d' % (self.__class__.__name__.lower(), index)), arg)
                                          for (index, arg) in enumerate(args)))
    def _decipher(self, value, *args):
        super_results = super(OperatorN, self)._decipher(value, *args)
        value = super_results[0]
        args = super_results[1:]

        if value is NoValue:
            return super_results

        missing_index = None
        for index, arg in enumerate(args):
            if arg is not NoValue:
                continue
            if missing_index is not None:
                # 2 are missing
                return super_results
            missing_index = index
        if missing_index is not None:
            missing_value = self._build_index(missing_index, value, args[:missing_index] + args[missing_index+1:])
            if missing_value is NoValue:
                return super_results # building not implemented in this case..
            return (value,) + args[:missing_index] + (missing_value,) + args[missing_index+1:]
        # we have to test all possible builds
        rebuild_args = [self._build_index(missing_index, value, args[:missing_index] + args[missing_index+1:]) for missing_index in xrange(len(args))]
        return [value] + [rebuild_arg if rebuild_arg is not NoValue else old_arg for (rebuild_arg, old_arg) in izip(rebuild_args, args)]

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
        return NoValue

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
        return NoValue

    @staticmethod
    def _build_right(value, left):
        if value[:len(left)] == left:
            return value[len(left):]
        return NoValue

Psifas.__concat__ = lambda a,b: Concatenate(a,b)

class Add(Operator2):
    _parse = operator.add

    def _build_symmetric(self, value, arg):
        if operator.isNumberType(value) and operator.isNumberType(arg):
            return value - arg
        if isinstance(value, datetime):
            try:
                return value - arg
            except TypeError, e:
                pass
        return NoValue
        

    def _build_left(self, value, right):
        if operator.isSequenceType(value) and operator.isSequenceType(right):
            return Concatenate._build_left(value, right)
        return self._build_symmetric(value, right)

    def _build_right(self, value, left):
        if operator.isSequenceType(value) and operator.isSequenceType(left):
            return Concatenate._build_right(value, right)
        return self._build_symmetric(value, left)
Psifas.__add__ = lambda a, b: Add(a,b)

class Multiply(Operator2):
    _parse = operator.mul

    def _build(self, value, other):
        if other == 0:
            return NoValue
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
        return NoValue

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
        if value:
            return arg
        return NoValue

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

class Hasattr(Operator1):
    def _parse(self, value):
        return hasattr(value, attr_name)

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
        
    

