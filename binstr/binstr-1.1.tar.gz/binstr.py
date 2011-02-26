#!/usr/bin/env python

###########################################################################
# Copyright (C) 2011  David McEwan
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program. If not, see <http://www.gnu.org/licenses/>.
###########################################################################

# This file contains some utility functions for creating and operating
#   on strings of binary digits.
# It is not intended to be the fastest or most efficient.
# It has been designed to be completely predictable, i.e. Strange inputs
#   will cause an AssertionError to be raised.
#
# However, it is useful for ensuring the correctness of each bit in an
#   easy-to-use and easily printable manner.
# This fits in well when generating code in other languages like Verilog,
#   C and Assembler.
# Obviously the other main use would be if you already have strings of
#   binary that you need to fiddle with.

# Bitwise Operations {{{

def b_and(A='00000000', B='00000000', align='right'): #{{{
    '''
    Perform a bitwise AND on two strings of binary digits, A and B.
    The align argument can be used to align the shortest of A and B to one
      side of the other.
    The returned string is the same length as the longest input.
    E.g. b_and('0101', '0011') returns '0001'
         b_and('01010000', '0011') returns '00000000'
         b_and('01010000', '0011', align='left') returns '00010000'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert type(B) is str, 'B is not a string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert len(A) >= 1, 'A has no digits'
    assert len(B) >= 1, 'B has no digits'
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: "%s". Must only contain "0"s or "1"s.' % B
    del re_compile, pattern
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    assert len(p) == len(q), 'Error in this function! len(p) must equal len(q). Oh dear.'
    
    return ''.join([str(int( bool(int(a)) and bool(int(b)) )) for (a, b) in zip(p, q)])
    # }}} End of b_and()

def b_nand(A='00000000', B='00000000', align='right'): #{{{
    '''
    Perform a bitwise NAND on two strings of binary digits, A and B.
    The align argument can be used to align the shortest of A and B to one
      side of the other.
    The returned string is the same length as the longest input.
    E.g. b_and('0101', '0011') returns '1110'
         b_and('01010000', '0011') returns '11111111'
         b_and('01010000', '0011', align='left') returns '11101111'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert type(B) is str, 'B is not a string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert len(A) >= 1, 'A has no digits'
    assert len(B) >= 1, 'B has no digits'
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: "%s". Must only contain "0"s or "1"s.' % B
    del re_compile, pattern
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    assert len(p) == len(q), 'Error in this function! len(p) must equal len(q). Oh dear.'
    
    return ''.join([str(int( not( bool(int(a)) and bool(int(b)) ) )) for (a, b) in zip(p, q)])
    # }}} End of b_nand()

def b_or(A='00000000', B='00000000', align='right'): # {{{
    '''
    Perform a bitwise OR on two strings of binary digits, A and B.
    The align argument can be used to align the shortest of A and B to one
      side of the other.
    The returned string is the same length as the longest input.
    E.g. b_or('0101', '0011') returns '0111'
         b_or('01010000', '0011') returns '01010011'
         b_or('01010000', '0011', align='left') returns '01110000'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert type(B) is str, 'B is not a string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert len(A) >= 1, 'A has no digits'
    assert len(B) >= 1, 'B has no digits'
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: "%s". Must only contain "0"s or "1"s.' % B
    del re_compile, pattern
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    assert len(p) == len(q), 'Error in this function! len(p) must equal len(q). Oh dear.'
    
    return ''.join([str(int( bool(int(a)) or bool(int(b)) )) for (a, b) in zip(p, q)])
    # }}} End of b_or()

def b_nor(A='00000000', B='00000000', align='right'): # {{{
    '''
    Perform a bitwise NOR on two strings of binary digits, A and B.
    The align argument can be used to align the shortest of A and B to one
      side of the other.
    The returned string is the same length as the longest input.
    E.g. b_or('0101', '0011') returns '1000'
         b_or('01010000', '0011') returns '10101100'
         b_or('01010000', '0011', align='left') returns '10001111'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert type(B) is str, 'B is not a string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert len(A) >= 1, 'A has no digits'
    assert len(B) >= 1, 'B has no digits'
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: "%s". Must only contain "0"s or "1"s.' % B
    del re_compile, pattern
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    assert len(p) == len(q), 'Error in this function! len(p) must equal len(q). Oh dear.'
    
    return ''.join([str(int( not( bool(int(a)) or bool(int(b)) ) )) for (a, b) in zip(p, q)])
    # }}} End of b_nor()

def b_xor(A='00000000', B='00000000', align='right'): # {{{
    '''
    Perform a bitwise XOR on two strings of binary digits, A and B.
    The align argument can be used to align the shortest of A and B to one
      side of the other.
    The returned string is the same length as the longest input.
    E.g. b_or('0101', '0011') returns '0110'
         b_or('01010000', '0011') returns '01010011'
         b_or('01010000', '0011', align='left') returns '01100000'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert type(B) is str, 'B is not a string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert len(A) >= 1, 'A has no digits'
    assert len(B) >= 1, 'B has no digits'
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: "%s". Must only contain "0"s or "1"s.' % B
    del re_compile, pattern
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    assert len(p) == len(q), 'Error in this function! len(p) must equal len(q). Oh dear.'
    
    return ''.join([str(int( bool(int(a)) ^ bool(int(b)) )) for (a, b) in zip(p, q)])
    # }}} End of b_xor()

def b_nxor(A='00000000', B='00000000', align='right'): # {{{
    '''
    Perform a bitwise NXOR on two strings of binary digits, A and B.
    The align argument can be used to align the shortest of A and B to one
      side of the other.
    The returned string is the same length as the longest input.
    E.g. b_or('0101', '0011') returns '1001'
         b_or('01010000', '0011') returns '10101100'
         b_or('01010000', '0011', align='left') returns '10011111'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert type(B) is str, 'B is not a string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert len(A) >= 1, 'A has no digits'
    assert len(B) >= 1, 'B has no digits'
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: "%s". Must only contain "0"s or "1"s.' % B
    del re_compile, pattern
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    assert len(p) == len(q), 'Error in this function! len(p) must equal len(q). Oh dear.'
    
    return ''.join([str(int( not( bool(int(a)) ^ bool(int(b)) ) )) for (a, b) in zip(p, q)])
    # }}} End of b_nxor()

def b_not(A='00000000'): # {{{
    '''
    Perform a bitwise NOT (inversion) on an input string.
    The returned string is the same length as the input.
    E.g. b_or('0101') returns '1010'
         b_or() returns '11111111'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert len(A) >= 1, 'A has no digits'
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    del re_compile, pattern
    
    return ''.join([str(int( not( bool(int(a)) ) )) for a in A])
    # }}} End of b_not()

# }}} End of Bitwise Operations

# Logical Operations {{{

def b_land(A='0'): #{{{
    '''
    Perform a logical AND on a string of binary digits.
    
    The returned string is always one digit in length.
    E.g. b_and('11111111') returns '1'
         b_and('01010000') returns '0'
         b_and('00000000') returns '0'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert len(A) >= 1, 'A has no digits'
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    del re_compile, pattern
    
    if len(A) >= 1 and A.find('0') < 0: return '1'
    else: return '0'
    # }}} End of b_land()

def b_lnand(A='0'): #{{{
    '''
    Perform a logical NAND on a string of binary digits.
    
    The returned string is always one digit in length.
    E.g. b_and('11111111') returns '0'
         b_and('01010000') returns '1'
         b_and('00000000') returns '1'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert len(A) >= 1, 'A has no digits'
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    del re_compile, pattern
    
    if len(A) >= 1 and A.find('0') < 0: return '0'
    else: return '1'
    # }}} End of b_lnand()

def b_lor(A='0'): #{{{
    '''
    Perform a logical OR on a string of binary digits.
    
    The returned string is always one digit in length.
    E.g. b_and('11111111') returns '1'
         b_and('01010000') returns '1'
         b_and('00000000') returns '0'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert len(A) >= 1, 'A has no digits'
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    del re_compile, pattern
    
    if len(A) >= 1 and A.find('1') < 0: return '0'
    else: return '1'
    # }}} End of b_lor()

def b_lnor(A='0'): #{{{
    '''
    Perform a logical NOR on a string of binary digits.
    
    The returned string is always one digit in length.
    E.g. b_and('11111111') returns '0'
         b_and('01010000') returns '0'
         b_and('00000000') returns '1'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert len(A) >= 1, 'A has no digits'
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    del re_compile, pattern
    
    if len(A) >= 1 and A.find('1') < 0: return '1'
    else: return '0'
    # }}} End of b_lnor()

def b_lxor(A='0'): #{{{
    '''
    Perform a logical XOR on a string of binary digits.
    
    The returned string is always one digit in length.
    E.g. b_and('11111111') returns '0'
         b_and('01010000') returns '0'
         b_and('01110000') returns '1'
         b_and('00000001') returns '1'
         b_and('00000000') returns '0'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert len(A) >= 1, 'A has no digits'
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    del re_compile, pattern
    
    if len(A) >= 1 and A.count('1') % 2 == 0: return '0'
    else: return '1'
    # }}} End of b_lxor()

def b_lnxor(A='0'): #{{{
    '''
    Perform a logical NXOR on a string of binary digits.
    
    The returned string is always one digit in length.
    E.g. b_and('11111111') returns '1'
         b_and('01010000') returns '1'
         b_and('01110000') returns '0'
         b_and('00000001') returns '0'
         b_and('00000000') returns '1'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert len(A) >= 1, 'A has no digits'
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % A
    del re_compile, pattern
    
    if len(A) >= 1 and A.count('1') % 2 == 0: return '1'
    else: return '0'
    # }}} End of b_lnxor()

# }}} End of Logical Operations

# Convertions To Binary Strings {{{

def int_to_b(num=0, width=8, endian='big', chop='most'): # {{{
    '''
    Convert a positive integer to a binary string.
    
    The width can be set to an arbitrary value but defaults to 8.
    If the width is less than the number of bits required to represent num
      then only the least significant bits are returned.
    However, by setting chop to 'least' only the most significant bits are
      returned.
    Clearly, chop is only relevant when the width is specified to be less
      then the width of num.
    
    The endianess is little by default but can be set to big to return a
      bit reversal.
    
    The returned string is can be converted to an int in python by setting
      the base to 2 e.g.:'int( int_to_b(...) , 2 )'.
       
    E.g. int_to_b() returns '00000000'
         int_to_b(5) returns '0101'
         int_to_b(0xF5, width=10, endian='little') returns '1010111100'
         int_to_b(0xF5, width=7) returns '1110101'
         int_to_b(0xF5, width=7, chop='least') returns '1111010'
    '''
    assert type(num)    is int,  'num is not an integer: %s'   % str(num)
    assert type(width)  is int,  'width is not an integer: %s' % str(width)
    assert type(endian) is str,  'endian is not a string: %s'  % str(endian)
    assert type(chop)   is str,  'chop is not a string: %s'    % str(chop)
    
    assert num >= 0,   'num is not a positive integer: %d'   % num
    assert width >= 0, 'width is not a positive integer: %d' % width
    assert endian == 'little' or endian == 'big', 'Invalid endian: "%s". Use either "little" or "big"' % endian
    assert chop == 'most' or chop == 'least', 'Invalid chop: "%s". Use either "most" or "least"'   % chop
    
    t = bin(num)                        # bin() returns a string with a '0b' prefix that we don't want
    assert t[:2] == '0b',               'bin() is not behaving as expected. bin(num) = %s' % t
    t = t[2:]
    
    if len(t) > width:
        if   chop == 'most': t = t[(-1 * width):]   # Remove most significant bits
        elif chop == 'least': t = t[:width]         # Remove least significant bits
    else: t = '0'*(width - len(t)) + t      # Add padding zeros
    
    if endian == 'little': t = t[::-1]         # Reverse the string
    
    return t
    # }}} End of int_to_b()

def frac_to_b(num=0.0, width=8, endian='big'): # {{{
    '''
    Convert a positive float which is less than 1.0 to a binary string.
    The returned value is 0xFF*num represented as a binary string
      when the width is 8 (default).
    This is useful for simulating fixed point arithmetic.
    
    The endianess is little by default but can be set to big to return a
      bit reversal.
    
    The returned string is can be converted to an int in python by setting
      the base to 2 e.g.:'int( frac_to_b(...) , 2 )'.
    
    E.g. frac_to_b() returns 00000000
         frac_to_b(0.3, 5) returns 01010
         frac_to_b(0.5, width=10, endian='little') returns 0000000001
    '''
    assert type(num)    is float, 'num is not an float: %s'     % str(num)
    assert type(width)  is int,   'width is not an integer: %s' % str(width)
    assert type(endian) is str,   'endian is not a string: %s'  % str(endian)
    
    assert num < 1.0,  'num is not less than 1.0: %d'        % str(num)
    assert width >= 0, 'width is not a positive integer: %d' % str(width)
    assert endian ==   'little' or endian == 'big', 'Invalid endian: "%s". Use either "little" or "big"' % str(endian)
    
    num *= 2**width
    t = bin(int(round(num)))            # bin() returns a string with a '0b' prefix that we don't want
    assert t[:2] == '0b',               'bin() is not behaving as expected. bin(num) = %s' % t
    t = t[2:]
    
    if len(t) > width: t = t[:width]                    # Remove least significant bits
    else:              t = '0'*(width - len(t)) + t     # Add padding zeros
    
    if endian == 'little': t = t[::-1]         # Reverse the string
    
    return t
    # }}} End of frac_to_b()

def str_to_b(instr='', char_width=8, endian='big', prefix='', suffix='', parity='N'): # {{{
    '''
    Convert an ASCII string into a string of binary digits.
    
    The bit-endianness of each character can be set the char_width and
      endian arguments although these are set to 8 bits wide and big
      endian by default.
    
    A prefix and suffix can also be specified to be added to each character.
    This can be useful for simulating start and stop bits.
    
    The parity argument can be used to add a parity bit.
    The allowed options are;
         N = None. No parity bit will be inserted.
        pO = prefixed Odd. Odd parity bit will be prefixed to sequence.
        sO = suffixed Odd. Odd parity bit will be suffixed to character.
        pE = prefixed Even. Even parity bit will be prefixed to character.
        sE = suffixed Even. Even parity bit will be suffixed to character.
    Mark and Space parity bits can be included with the prefix and suffix
      arguments as they are always fixed to either 1 or 0.

    E.g. str_to_b() returns ''
         str_to_b('\\x00') returns '00000000'
         str_to_b('abc') returns '011000010110001001100011'
         str_to_b('U') returns '01010101'
         str_to_b('U', endian='little') returns '10101010'
         str_to_b('U', char_width=7) returns '1010101'
         str_to_b('U', prefix='1111', suffix='0000') returns '1111010101010000'
         str_to_b('\\x00', parity='pO') returns '100000000'
         str_to_b('U', parity='sE') returns '010101010'
    '''
    assert type(instr) is str,          'instr is not a string: %s'         % str(instr)
    assert type(char_width)  is int,    'char_width is not an integer: %s'  % str(char_width)
    assert type(endian) is str,         'endian is not a string: %s'        % str(endian)
    assert type(prefix) is str,         'prefix is not a string: %s'        % str(prefix)
    assert type(suffix) is str,         'suffix is not a string: %s'        % str(suffix)
    assert type(parity) is str,         'parity is not a string: %s'        % str(parity)
    
    for (i, c) in enumerate(instr):
        assert ord(c) < 256, 'character "%(c)s" (%(o)s) at position %(i)s is not valid ASCII.' % {'c': str(c), 'o': ord(c), 'i': str(i)}
    
    assert char_width >= 0, 'char_width is not a positive integer: %d' % str(char_width)
    assert endian ==   'little' or endian == 'big', 'Invalid endian: "%s". Use either "little" or "big"' % str(endian)
    assert parity == 'N'  or \
           parity == 'pO' or \
           parity == 'sO' or \
           parity == 'pE' or \
           parity == 'sE', 'Invalid prefix: "%s".' % str(prefix)
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(prefix)) == False, 'Invalid prefix: "%s". Must only contain "0"s or "1"s.' % prefix
    assert bool(pattern.search(suffix)) == False, 'Invalid suffix: "%s". Must only contain "0"s or "1"s.' % suffix
    del re_compile, pattern
    
    t = ''
    for c in (instr):
        b_c = int_to_b(ord(c), width=char_width, endian=endian, chop='most')
        
        t += prefix
        
        if   parity == 'pO': t += b_lnxor(b_c)
        elif parity == 'pE': t += b_lxor(b_c)
        
        t += b_c
        
        if   parity == 'sO': t += b_lnxor(b_c)
        elif parity == 'sE': t += b_lxor(b_c)
        
        t += suffix
    
    return t
    # }}} End of str_to_b()

# }}} End of Convertions To Binary Strings

# Arithmetic Operations {{{

def b_add(A='00000000', B='00000000', endian='big'): # {{{
    '''
    Perform an ADD operation on two input strings.
    
    The returned string is always one digit longer than the longest input.
    This means that the MSB of the returned string can be used as a
      carry flag.
    
    The endianess of both input strings as well as the output must be the
      same.
    
    E.g. b_add() returns '00000000'
         b_add('0001', '0001') returns '00010'
         b_add('0001', '0001', endian='little') returns '00001'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert type(B) is str, 'B is not a string: %s' % str(B)
    assert type(endian) is str, 'endian is not a string: %s' % str(endian)
    
    assert len(A) >= 1, 'A has no digits'
    assert len(B) >= 1, 'B has no digits'
    assert endian == 'little' or endian == 'big', 'Invalid endian: "%s". Use either "little" or "big"' % str(endian)
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % str(A)
    assert bool(pattern.search(B)) == False, 'Invalid B: "%s". Must only contain "0"s or "1"s.' % B
    del re_compile, pattern
    
    if endian == 'little':                     # Ensure both inputs are big endian before the add 
        A = A[::-1]
        B = B[::-1]
    
    if len(A) >= len(B): l = A
    else:                l = B
    
    return int_to_b(num=(int(A, 2) + int(B, 2)), width=(len(l) + 1), endian=endian, chop='most')
    # }}} End of b_add()

def b_mul(A='00000000', B='00000000', endian='big'): # {{{
    '''
    Perform a MUL (multiply) operation on two input strings.
    
    The returned string is always twice the length of the longest input.
    
    The endianess of both input strings as well as the output must be the
      same.
    
    E.g. b_mul() returns '0000000000000000'
         b_mul('0001', '0001') returns '00000001'
         b_mul('0001', '0001', endian='little') returns '00000010'
    '''
    assert type(A) is str, 'A is not a string: %s' % str(A)
    assert type(B) is str, 'B is not a string: %s' % str(B)
    assert type(endian) is str, 'endian is not a string: %s' % str(endian)
    
    assert len(A) >= 1, 'A has no digits'
    assert len(B) >= 1, 'B has no digits'
    assert endian == 'little' or endian == 'big', 'Invalid endian: "%s". Use either "little" or "big"' % str(endian)
    
    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: "%s". Must only contain "0"s or "1"s.' % str(A)
    assert bool(pattern.search(B)) == False, 'Invalid B: "%s". Must only contain "0"s or "1"s.' % B
    del re_compile, pattern
    
    if endian == 'little':                     # Ensure both inputs are big endian before the add 
        A = A[::-1]
        B = B[::-1]
    
    if len(A) >= len(B): l = A
    else:                l = B
    
    return int_to_b(num=(int(A, 2) * int(B, 2)), width=(len(l) * 2), endian=endian, chop='most')
    # }}} End of b_mul()

# }}} End of Arithmetic Operations

def run_self_test(): # {{{
    
    # Bitwise Operations {{{
    
    print('\nb_and()...')
    print(b_and.__doc__)
    print('\tTests:')
    print('\tb_and(\'0101\', \'0011\') = %s'                        % b_and('0101', '0011')                         )
    print('\tb_and(\'01010000\', \'0011\') = %s'                    % b_and('01010000', '0011')                     )
    print('\tb_and(\'01010000\', \'0011\', align=\'left\') = %s'    % b_and('01010000', '0011', align='left')       )
    
    print('\nb_nand()...')
    print(b_nand.__doc__)
    print('\tTests:')
    print('\tb_nand(\'0101\', \'0011\') = %s'                        % b_nand('0101', '0011')                       )
    print('\tb_nand(\'01010000\', \'0011\') = %s'                    % b_nand('01010000', '0011')                   )
    print('\tb_nand(\'01010000\', \'0011\', align=\'left\') = %s'    % b_nand('01010000', '0011', align='left')     )
    
    print('\nb_or()...')
    print(b_or.__doc__)
    print('\tTests:')
    print('\tb_or(\'0101\', \'0011\') = %s'                         % b_or('0101', '0011')                          )
    print('\tb_or(\'01010000\', \'0011\') = %s'                     % b_or('01010000', '0011')                      )
    print('\tb_or(\'01010000\', \'0011\', align=\'left\') = %s'     % b_or('01010000', '0011', align='left')        )
    
    print('\nb_nor()...')
    print(b_nor.__doc__)
    print('\tTests:')
    print('\tb_nor(\'0101\', \'0011\') = %s'                         % b_nor('0101', '0011')                        )
    print('\tb_nor(\'01010000\', \'0011\') = %s'                     % b_nor('01010000', '0011')                    )
    print('\tb_nor(\'01010000\', \'0011\', align=\'left\') = %s'     % b_nor('01010000', '0011', align='left')      )
    
    print('\nb_xor()...')
    print(b_xor.__doc__)
    print('\tTests:')
    print('\tb_xor(\'0101\', \'0011\') = %s'                         % b_xor('0101', '0011')                        )
    print('\tb_xor(\'01010000\', \'0011\') = %s'                     % b_xor('01010000', '0011')                    )
    print('\tb_xor(\'01010000\', \'0011\', align=\'left\') = %s'     % b_xor('01010000', '0011', align='left')      )
    
    print('\nb_nxor()...')
    print(b_nxor.__doc__)
    print('\tTests:')
    print('\tb_nxor(\'0101\', \'0011\') = %s'                         % b_nxor('0101', '0011')                      )
    print('\tb_nxor(\'01010000\', \'0011\') = %s'                     % b_nxor('01010000', '0011')                  )
    print('\tb_nxor(\'01010000\', \'0011\', align=\'left\') = %s'     % b_nxor('01010000', '0011', align='left')    )
    
    print('\nb_not()...')
    print(b_not.__doc__)
    print('\tTests:')
    print('\tb_not(\'0101\') = %s'                                    % b_not('0101')                               )
    print('\tb_not() = %s'                                            % b_not()                                     )
    
    # }}} End of Bitwise Operations
    
    # Logical Operations {{{
    
    print('\nb_land()...')
    print(b_land.__doc__)
    print('\tTests:')
    print('\tb_land(\'11111111\') = %s'                             % b_land('11111111')                            )
    print('\tb_land(\'01010000\') = %s'                             % b_land('01010000')                            )
    print('\tb_land(\'00000000\') = %s'                             % b_land('00000000')                            )
    
    print('\nb_lnand()...')
    print(b_lnand.__doc__)
    print('\tTests:')
    print('\tb_lnand(\'11111111\') = %s'                            % b_lnand('11111111')                           )
    print('\tb_lnand(\'01010000\') = %s'                            % b_lnand('01010000')                           )
    print('\tb_lnand(\'00000000\') = %s'                            % b_lnand('00000000')                           )
    
    print('\nb_lor()...')
    print(b_lor.__doc__)
    print('\tTests:')
    print('\tb_lor(\'11111111\') = %s'                              % b_lor('11111111')                             )
    print('\tb_lor(\'01010000\') = %s'                              % b_lor('01010000')                             )
    print('\tb_lor(\'00000000\') = %s'                              % b_lor('00000000')                             )
    
    print('\nb_lnor()...')
    print(b_lnor.__doc__)
    print('\tTests:')
    print('\tb_lnor(\'11111111\') = %s'                             % b_lnor('11111111')                            )
    print('\tb_lnor(\'01010000\') = %s'                             % b_lnor('01010000')                            )
    print('\tb_lnor(\'00000000\') = %s'                             % b_lnor('00000000')                            )
    
    print('\nb_lxor()...')
    print(b_lxor.__doc__)
    print('\tTests:')
    print('\tb_lxor(\'11111111\') = %s'                             % b_lxor('11111111')                            )
    print('\tb_lxor(\'01010000\') = %s'                             % b_lxor('01010000')                            )
    print('\tb_lxor(\'01110000\') = %s'                             % b_lxor('01110000')                            )
    print('\tb_lxor(\'00000001\') = %s'                             % b_lxor('00000001')                            )
    print('\tb_lxor(\'00000000\') = %s'                             % b_lxor('00000000')                            )
    
    print('\nb_lnxor()...')
    print(b_lnxor.__doc__)
    print('\tTests:')
    print('\tb_lnxor(\'11111111\') = %s'                            % b_lnxor('11111111')                           )
    print('\tb_lnxor(\'01010000\') = %s'                            % b_lnxor('01010000')                           )
    print('\tb_lnxor(\'01110000\') = %s'                            % b_lnxor('01110000')                           )
    print('\tb_lnxor(\'00000001\') = %s'                            % b_lnxor('00000001')                           )
    print('\tb_lnxor(\'00000000\') = %s'                            % b_lnxor('00000000')                           )
    
    # }}} End of Logical Operations
    
    # Convertions To Binary Strings {{{
    
    print('\nint_to_b()...')
    print(int_to_b.__doc__)
    print('\tTests:')
    print('\tint_to_b() = %s'                                       % int_to_b()                                    )
    print('\tint_to_b(5) = %s'                                      % int_to_b(5)                                   )
    print('\tint_to_b(0xF5, width=10, endian=\'little\') = %s'      % int_to_b(0xF5, width=10, endian='little')     )
    print('\tint_to_b(0xF5, width=7) = %s'                          % int_to_b(0xF5, width=7)                       )
    print('\tint_to_b(0xF5, width=7, chop=\'least\') = %s'          % int_to_b(0xF5, width=7, chop='least')         )
    
    print('\nfrac_to_b()...')
    print(frac_to_b.__doc__)
    print('\tTests:')
    print('\tfrac_to_b() = %s'                                      % frac_to_b()                                   )
    print('\tfrac_to_b(0.3, 5) = %s'                                % frac_to_b(0.3, 5)                             )
    print('\tfrac_to_b(0.5, width=10, endian=\'little\') = %s'      % frac_to_b(0.5, width=10, endian='little')     )
    
    print('\str_to_b()...')
    print(str_to_b.__doc__)
    print('\tTests:')
    print('\tstr_to_b() = %s'                                       % str_to_b()                                    )
    print('\tstr_to_b(\'\\x00\') = %s'                               % str_to_b('\x00')                              )
    print('\tstr_to_b(\'abc\') = %s'                                % str_to_b('abc')                               )
    print('\tstr_to_b(\'U\') = %s'                                  % str_to_b('U')                                 )
    print('\tstr_to_b(\'U\', endian=\'little\') = %s'               % str_to_b('U', endian='little')                )
    print('\tstr_to_b(\'U\', char_width=7) = %s'                    % str_to_b('U', char_width=7)                   )
    print('\tstr_to_b(\'U\', prefix=\'1111\', suffix=\'0000\') = %s'% str_to_b('U', prefix='1111', suffix='0000')   )
    print('\tstr_to_b(\'\\x00\', parity=\'pO\') = %s'                % str_to_b('\x00', parity='pO')                 )
    print('\tstr_to_b(\'U\', parity=\'sE\') = %s'                   % str_to_b('U', parity='sE')                    )
    
    # }}} End of Convertions To Binary Strings
    
    # Arithmetic Operations {{{
    
    print('\nb_add()...')
    print(b_add.__doc__)
    print('\tTests:')
    print('\tb_add() = %s'                                            % b_add()                                     )
    print('\tb_add(\'0001\', \'0001\') = %s'                          % b_add('0001', '0001')                       )
    print('\tb_add(\'0001\', \'0001\', endian=\'little\') = %s'       % b_add('0001', '0001', endian='little')      )
    
    print('\nb_mul()...')
    print(b_mul.__doc__)
    print('\tTests:')
    print('\tb_mul() = %s'                                            % b_mul()                                     )
    print('\tb_mul(\'0001\', \'0001\') = %s'                          % b_mul('0001', '0001')                       )
    print('\tb_mul(\'0001\', \'0001\', endian=\'little\') = %s'       % b_mul('0001', '0001', endian='little')      )
    
    # }}} End of Arithmetic Operations
    
# }}} End of run_self_test()

if __name__ == '__main__': # {{{
    run_self_test()
# }}} End of __main__
