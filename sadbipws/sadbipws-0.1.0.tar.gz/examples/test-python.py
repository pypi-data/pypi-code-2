#!/usr/bin/env python3

import sadbipws as sad

def eq(a, b):
    if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
        if len(a) != len(b):
            return False
        for i in range(len(a)):
            if not eq(a[i], b[i]):
                return False
        return True
    elif isinstance(a, dict) and isinstance(b, dict):
        av, bv = a.keys(), b.keys()
        if len(av) != len(bv):
            return False
        for x in av:
            if not eq(a[x], b[x]):
                return False
        return True
    else:
        return a == b

und = lambda t: print('\n' + t.center(70) + '\n' + ('=' * len(t)).center(70))
def check_all(*l):
    for x in l:
        ser = sad.serialize(x)
        deser = sad.deserialize(ser)
        print(repr(x), repr(ser), repr(deser), sep='\n', end='\n\n')
        assert eq(deser, x)

und('Abstract objects')
check_all(None,
          sad.Everything,
          True,
          False,
          float('inf'),
          float('-inf'))

und('Integers')
check_all(34,
          0,
          -2,
          2342342524235256236234235111123)

und('Floats')
check_all(3.123,
          0.0,
          -565.23452,
          11234523512312.23456)

und('Fractions')
from fractions import Fraction
class SubFraction(Fraction):
    pass
sad.add_alias(SubFraction, Fraction)

check_all(Fraction(4, 7),
          SubFraction(49, 3),
          Fraction(10, 5))

und('Complex numbers')
class SimpleComplex:
    def __init__(self, real, imag=0):
        self.real = real
        self.imag = imag

    def __eq__(self, o):
        return self.real == o.real and self.imag == o.imag

    def __repr__(self):
        return '{}{}{}i'.format(self.real, self.imag > -1 and '+' or '', self.imag)

sad.add_alias(SimpleComplex, complex)

check_all(complex(13, 3),
          complex(-23),
          SimpleComplex(3, -2))

und('Strings')
check_all('hello',
          '')

und('Byte strings')
check_all(b'hello',
          bytearray(b'hello'),
          '')

und('Lists')
check_all([2, 5, 1],
          (33, "it's..", complex(33, 34)),
          [],
          (b"'oh no'", Fraction(1), ['message in sublist', -32.22, ['utf8°'.encode('utf8'), 'ascii'.encode('ascii')]]))

und('Dictionaries')
check_all({'name': 'Pawy', 'age': 341},
          {34: (-34, {b'42': 24, (33, 22): 'aha'}, 53.32), complex(4): Fraction(44, 33), 34: [33.33, {34: [33.33]}]},
          {})


