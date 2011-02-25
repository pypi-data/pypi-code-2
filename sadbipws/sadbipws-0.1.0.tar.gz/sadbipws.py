#!/usr/bin/env python3

# sadbipws: an implementation of the SADBIPWS serializer
# Copyright (C) 2011 Niels Serup

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

## Version:...... 0.1.0
## Website:...... http://metanohi.org/projects/sadbipws/
## Development:.. http://gitorious.org/sadbipws
## Maintainer:... Niels Serup <ns@metanohi.org>

"""
sadbipws is an implementation of the SADBIPWS serializer. It is also
the reference implementation as well as the specification (a proper
specification must be created at some point in the near future, but I
haven't bothered yet ~~~~Niels).
"""

__version__ = '0.1.0'
__all__ = ['base_encode', 'base_decode', 'serialize', 'deserialize',
           'add_alias', 'Everything']
__copyright__ = '''
Copyright (C) 2011 Niels Serup

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import itertools
import functools
import math
from fractions import Fraction
import struct
import json
try:
    import zlib
except ImportError:
    zlib = None
import bz2

_glob_dict = sys.modules[__name__].__dict__

inf = float('inf')
minf = float('-inf')
class Everything:
    def __repr__(self):
        return 'Everything'
Everything = Everything()
_ffb = b'\xff'
_ffb2 = _ffb * 2
_00b = b'\x00'
_01b = b'\x01'
_bchr = lambda n: bytes((ord(chr(n)),))
_floating_format = 'd' # double
_int_format = 'L' # long
_floating_size = struct.Struct(_floating_format).size # should be 8
_int_size = struct.Struct(_int_format).size # should be 4
_float_pack = functools.partial(struct.pack, '>' + _floating_format)
_int_pack = functools.partial(struct.pack, '>' + _int_format)
_float_unpack = lambda x: functools.partial(struct.unpack, '>' + _floating_format)(x)[0]
_int_unpack = lambda x: functools.partial(struct.unpack, '>' + _int_format)(x)[0]
_mul2_bases = tuple(2**i for i in range(9))

class _AnotherSerializerNeeded(Exception):
    def __init__(self, func):
        self.func = func
def _runandbedone(func):
    # Used as a decorator function, so that variables can be created
    # locally within a function, which is run at once. The function
    # name does not matter.
    func()

_serialize_funcs = {}
_aliases = {}
_deserialize_funcs = {}

# Serializing codes
_serialize_info = lambda: {
    (type(None), type(Everything), bool): (1, 'abstract'),
    int: (2, 'int'),
    float: (3, 'float'),
    Fraction: (4, 'fraction'),
    complex: (5, 'complex'),
    str: (6, 'str'),
    (bytes, bytearray): (7, 'bytes'),
    (list, tuple): (8, 'list'),
    dict: (9, 'dict')
    }

# Abstract codes
_abstract_codes = {
    None: 0,
    Everything: 1,
    True: 2,
    False: 3,
    inf: 4,
    minf: 5
    }

_abstract_codes = {key: _bchr(val) for key, val in _abstract_codes.items()}
_abstract_codes_rev = {val: key for key, val in _abstract_codes.items()}

def serialize(obj, bz2_out=False, gzip_out=False, json_in=False):
    """
    serialize(obj : object, bz2_out : bool=False, gzip_out :
              bool=False, json_in : bool=False) -> bytes

    Serialize a Python object or convert a JSON string into a
    SADBIPWS-formatted bytestring. Optionally, compress with bz2 or
    gzip.
    """
    if json_in:
        obj = json.loads(obj)

    code, data = _run_serialize_func(obj)
    out = code + data

    if bz2_out:
        out = bz2.compress(out, 9)
    elif gzip_out:
        out = zlib.compress(out, 9)
    return out

def deserialize(b, bz2_in=False, gzip_in=False, json_out=False,
                lists_as_tuples=False):
    """
    serialize(b : bytes, bz2_in : bool=False, gzip_in : bool=False,
              json_out : bool=False, lists_as_tuples : bool=False) ->
              object

    Deserialize a SADBIPWS bytestring into either a Python object or a
    JSON string. Optionally, decompress with bz2 or gzip. By setting
    lists_as_tuples to True, this function will convert all lists (not
    just those posing as dictionary keys) to tuples before returning
    the data.
    """
    if bz2_in:
        b = bz2.decompress(b)
    elif gzip_in:
        b = zlib.decompress(b)

    global _convert_lists_to_tuples
    _convert_lists_to_tuples = lists_as_tuples
    code, data = b[0], b[1:]
    obj = _run_deserialize_func(code, data)

    if json_out:
        obj = json.dumps(obj)
    return obj

def _abstract_serialize(obj):
    try:
        return _abstract_codes[obj]
    except KeyError:
        raise ValueError('{} is not a valid abstract value'.format(repr(obj)))

def _abstract_deserialize(b):
    try:
        return _abstract_codes_rev[b]
    except KeyError:
        raise ValueError('{} is not a valid abstract serialized value'.format(
                repr(b)))

def _int_serialize(obj):
    if obj < 0:
        obj *= -1
        sign = _00b
    else:
        sign = _01b
    bs = b256_encode(obj)
    return sign + bs

def _int_deserialize(b):
    sign = b[0]
    n = b256_decode(b[1:])
    if sign == 0:
        n *= -1
    return n

def _float_serialize(obj):
    if obj == inf or obj == minf:
        raise _AnotherSerializerNeeded(_abstract_serialize)
    return _float_pack(obj)

def _float_deserialize(b):
    return _float_unpack(b)

def _fraction_serialize(obj):
    numer_bs = b256_encode(obj.numerator)
    denom_bs = b256_encode(obj.denominator)
    return _len_encode(numer_bs) \
        + numer_bs + denom_bs

def _fraction_deserialize(b):
    ffp = b.find(_ffb)
    numer_len = b255_decode(b[:ffp])
    numer = b256_decode(b[ffp + 1:ffp + 1 + numer_len])
    denom = b256_decode(b[ffp + 1 + numer_len:])
    return Fraction(numer, denom)

def _complex_serialize(obj):
    return _float_pack(obj.real) + _float_pack(obj.imag)

def _complex_deserialize(b):
    return complex(_float_unpack(b[:_floating_size]),
                   _float_unpack(b[_floating_size:]))

def _str_serialize(obj):
    bs = b''
    for x in obj:
        bs += _int_pack(ord(x))
    return bs

def _str_deserialize(b):
    return ''.join(chr(_int_unpack(b[i:i + _int_size]))
                   for i in range(0, len(b), _int_size))

def _bytes_serialize(obj):
    return obj

def _bytes_deserialize(b):
    return b

def _list_serialize(obj):
    pos = 0
    h_bs = b'' # Head
    b_bs = b'' # Body
    for x in obj:
        code, data = _run_serialize_func(x)
        h_bs += code + _sepnum_encode(pos)
        b_bs += data
        pos += len(data)
    return h_bs + _ffb + b_bs

def _list_deserialize(b):
    ff2p = b.find(_ffb2)
    code_pos = ((x[0], b255_decode(x[1:])) for x in b[:ff2p].split(_ffb))
    body = b[ff2p + 2:]
    lst = []
    try:
        code, pos = next(code_pos)
    except IndexError:
        return lst
    for next_code, next_pos in code_pos:
        lst.append(_run_deserialize_func(code, body[pos:next_pos]))
        code, pos = next_code, next_pos
    lst.append(_run_deserialize_func(code, body[pos:]))
    if _convert_lists_to_tuples: # Global
        lst = tuple(lst)
    return lst

def _dict_serialize(obj):
    return _list_serialize(itertools.chain(*obj.items()))

def _dict_deserialize(b):
    objs = _list_deserialize(b)
    return {(tuple(objs[i]) if isinstance(objs[i], list) else objs[i]):
                objs[i + 1] for i in range(0, len(objs), 2)}

@_runandbedone
def _():
    global _serialize_funcs, _deserialize_funcs
    for key, vals in _serialize_info().items():
        name = vals[1]
        code_num = vals[0]
        code = _bchr(code_num)
        func = _glob_dict['_{}_serialize'.format(name)]
        defunc = _glob_dict['_{}_deserialize'.format(name)]
        func.format_name = name
        func.format_code = code
        if isinstance(key, tuple):
            for key in key:
                _serialize_funcs[key] = func
        else:
            _serialize_funcs[key] = func
        _deserialize_funcs[code_num] = defunc

def add_alias(new, match):
    """
    add_alias(new : type, match : type)

    Add an alias for a type.
    """
    if not match in _serialize_funcs:
        raise ValueError('{} is not an existing type'.format(repr(match)))
    _aliases[new] = match

def _run_serialize_func(obj):
    try:
        func = _serialize_funcs[type(obj)]
    except KeyError:
        try:
            func = _serialize_funcs[_aliases[type(obj)]]
        except KeyError:
            raise ValueError('the type of {} cannot be recognized'.format(repr(obj)))
    while True:
        try:
            funcd = func(obj)
            break
        except _AnotherSerializerNeeded as e:
            func = e.func
    # if func.format_name in ('list', 'dict'):
    #     funcd = _len_encode(funcd) + funcd
    return func.format_code, funcd

def _run_deserialize_func(code, data):
    return _deserialize_funcs[code](data)

def base_encode(n, base):
    """
    base_encode(n : int, base : int) -> bytes

    Convert a number to its byte representation in some base.
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError('n must be a non-negative integer')
    if not isinstance(base, int) or base < 1:
        raise ValueError('base must be a positive integer')
    elif n == 0:
        return b''
        
    l = math.ceil(math.log(n + 1, base))
    b = bytearray(l)

    if base in _mul2_bases:
        blm1 = base.bit_length() - 1
        for i in range(l):
            b[-i - 1] = n % base
            n >>= blm1
    else:
        for i in range(l):
            b[-i - 1] = n % base
            n //= base
    return bytes(b)

def base_decode(b, base):
    """
    base_decode(b : bytes, base : int) -> int

    Convert bytes in some base to their integer representation.
    """
    if not (isinstance(b, bytes) or isinstance(b, bytearray)):
        raise ValueError('b must be a bytes object or a bytearray object')
    if not isinstance(base, int) or base < 1:
        raise ValueError('base must be a positive integer')
    elif not b:
        return 0
    n = b[-1]
    t = 1
    for x in b[-2::-1]:
        t *= base
        n += x * t
    return n

def _sepnum_encode(num):
    return b255_encode(num) + _ffb

def _len_encode(obj):
    return _sepnum_encode(len(obj))

@_runandbedone
def _():
    for i in range(255, 257):
        for x in ('en', 'de'):
            name = 'base_{}code'.format(x)
            func = functools.partial(
                _glob_dict[name], base=i)
            name = 'b{}_{}code'.format(i, x)
            func.__doc__ = '''
    {}(int) -> bytes

    Convert a number to its byte representation in base {}.
    '''.format(name, i)
            _glob_dict[name] = func
            __all__.append(name)


del _ # Done.
