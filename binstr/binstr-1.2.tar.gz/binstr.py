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
#
#----------------------
# Implementation Notes:
#----------------------
# The term b_string is used to refer to a string containing only 0s and 1s.
# In functions the letters A and B always refers to an input b_string.
# The variable t used in most functions stands for temporary.
# In the gray conversion functions the variables b and g are used instead of
#   t for clarity.
#
# The function naming scheme is as follows:
#    - 'b_' prefix means that a valid b_string must be given as input.
#    - '_b' suffix means that a valid b_string will be returned as the output
#        where the input was not a valid b_string.
#    - The rest of the name describes the operation of the function.

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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert b_validate(B) == True, 'B is not a valid b_string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert b_validate(B) == True, 'B is not a valid b_string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert b_validate(B) == True, 'B is not a valid b_string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert b_validate(B) == True, 'B is not a valid b_string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert b_validate(B) == True, 'B is not a valid b_string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert b_validate(B) == True, 'B is not a valid b_string: %s' % str(B)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
       
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    
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
         int_to_b(5) returns '00000101'
         int_to_b(0xF5, width=10, endian='little') returns '1010111100'
         int_to_b(0xF5, width=7) returns '1110101'
         int_to_b(0xF5, width=7, chop='least') returns '1111010'
    '''
    assert type(num) is int or type(num) is long,  'num is not an integer: %s' % str(num)
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
    assert b_validate(prefix, fail_empty=False) == True, 'prefix is not a valid b_string: %s' % str(prefix)
    assert b_validate(suffix, fail_empty=False) == True, 'suffix is not a valid b_string: %s' % str(suffix)
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

# Gray Conversion {{{

def b_bin_to_gray(A='00000000', endian='big'): # {{{
    '''
    Convert from binary coding to Gray coding.
    
    The returned string will always be the same length as the input string.
    Both the input and output strings will have the same bit-endianness,
      which can be specifed with the endian argument.
    
    E.g. b_bin_to_gray() returns '00000000'
         b_bin_to_gray('1111') returns '1000'
         b_bin_to_gray('1101', endian='big') returns '1011'
         b_bin_to_gray('1101', endian='little') returns '0111'
    '''
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert type(endian) is str,  'endian is not a string: %s'  % str(endian)
    
    assert endian == 'little' or endian == 'big', 'Invalid endian: "%s". Use either "little" or "big"' % endian
    
    if endian == 'little': A = A[::-1] # Make sure endianness is big before conversion
    
    g = A[0]
    for i in range(1, len(A)): g += str( int(A[i-1] != A[i]) )
    
    assert len(A) == len(g), 'Error in this function! len(A) must equal len(g). Oh dear.'
    
    if endian == 'little': g = g[::-1] # Convert back to little endian if necessary
    
    return g
    # }}} End of b_bin_to_gray()

def b_gray_to_bin(A='00000000', endian='big'): # {{{
    '''
    Convert from Gray coding to binary coding.
    
    The returned string will always be the same length as the input string.
    Both the input and output strings will have the same bit-endianness,
      which can be specifed with the endian argument.
    
    E.g. b_gray_to_bin() returns '00000000'
         b_gray_to_bin('1111') returns '1010'
         b_gray_to_bin('1101', endian='big') returns '1001'
         b_gray_to_bin('1101', endian='little') returns '1011'
    '''
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert type(endian) is str,  'endian is not a string: %s'  % str(endian)
    
    assert endian == 'little' or endian == 'big', 'Invalid endian: "%s". Use either "little" or "big"' % endian
    
    if endian == 'little': A = A[::-1] # Make sure endianness is big before conversion
    
    b = A[0]
    for i in range(1, len(A)): b += str( int(b[i-1] != A[i]) )
    
    assert len(A) == len(b), 'Error in this function! len(A) must equal len(b). Oh dear.'
    
    if endian == 'little': b = b[::-1] # Convert back to little endian if necessary
    
    return b
    # }}} End of b_gray_to_bin()

# }}} End of Gray Conversion

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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert b_validate(B) == True, 'B is not a valid b_string: %s' % str(B)
    assert type(endian) is str, 'endian is not a string: %s' % str(endian)
    
    assert endian == 'little' or endian == 'big', 'Invalid endian: "%s". Use either "little" or "big"' % str(endian)
    
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
    assert b_validate(A) == True, 'A is not a valid b_string: %s' % str(A)
    assert b_validate(B) == True, 'B is not a valid b_string: %s' % str(B)
    assert type(endian) is str, 'endian is not a string: %s' % str(endian)
    
    assert endian == 'little' or endian == 'big', 'Invalid endian: "%s". Use either "little" or "big"' % str(endian)
    
    if endian == 'little':                     # Ensure both inputs are big endian before the add 
        A = A[::-1]
        B = B[::-1]
    
    if len(A) >= len(B): l = A
    else:                l = B
    
    return int_to_b(num=(int(A, 2) * int(B, 2)), width=(len(l) * 2), endian=endian, chop='most')
    # }}} End of b_mul()

# }}} End of Arithmetic Operations

# Base Conversion {{{

def b_to_baseX(A='00000000', base=64, alphabet='', pad='=', align='left', b_pad='0'): # {{{
    '''
    Convert from binary coding to another base.
    
    The input string will ALWAYS be padded out to a multiple of 8 bits.
    The alignment of this padding can be controlled with the align argument,
      which can either be 'left' (default) or 'right'.
    The padding digit can be controlled be the b_pad argument which can either
      be '0' (default) or '1'.
    
    The base used can either be 4, 8, 16, 32 or 64 (default) and is controlled
      by the base argument.
    A user-defined alphabet can be supplied containing any characters in any
      order as long at the length is equal to the base using the alphabet
      argument.
    Supplying an empty input string will return in the alphabet which is used
      for that base.
    The default alphabets for bases 32 and 64 are taken from RCF 3548 and
      the alphabets used for bases 4, 8 and 16 are standard.
    Note that base 32 in RFC 3548 is not compatible with Python's
      int(<input_string>, 32) function which uses 0-9,A-V.
    The highest base that Python's int() function supports is 36 (0-9,A-Z).
    
    The padding character is '=' by default though this can be changed with the
      pad argument.
    This padding can be turned off by setting pad to an empty string.
    
    E.g. b_to_baseX() returns 'AA=='
         b_to_baseX('') returns 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
         b_to_baseX('', base=4) returns '0123'
         b_to_baseX('', base=8) returns '01234567'
         b_to_baseX('', base=16) returns '0123456789ABCDEF'
         b_to_baseX('', base=32) returns 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
         b_to_baseX('', base=64) returns 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
         b_to_baseX('00011011', base=4) returns '0123'
         b_to_baseX('000110111', base=4) returns '01232000'
         b_to_baseX('0001101110', base=4) returns '01232000'
         b_to_baseX('000001010011100101110111', base=8) returns '01234567'
         b_to_baseX('0000010110101111', base=16) returns '05AF'
         b_to_baseX('0000010110101111', base=32) returns 'AWXQ==='
         b_to_baseX(int_to_b(int('14FB9C03D97E', 16), width=48)) returns 'FPucA9l+'
         b_to_baseX(int_to_b(int('14FB9C03D9', 16), width=40)) returns 'FPucA9k='
         b_to_baseX(int_to_b(int('14FB9C03', 16), width=32)) returns 'FPucAw=='
         b_to_baseX(int_to_b(int('14FB9C03', 16), width=32), pad='') returns 'FPucAw'
         b_to_baseX('00011011', base=4, alphabet='abcd') returns 'abcd'
    '''
    
    # These are the default alphabets.
    # 4 is standard radix-4 notation.
    # 8 is standard octal notation.
    # 16 is standard hexadecimal notation (uppercase). This also appears in RFC 3548.
    # 32 and 64 are taken from RFC 3548.
    base_alphabets = {
                      '4'  : '0123',
                      '8'  : '01234567',
                      '16' : '0123456789ABCDEF',
                      '32' : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                      '64' : 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
                     }
    
    assert b_validate(A, fail_empty=False) == True, 'A is not a valid b_string: %s' % str(A)
    assert type(base) is int, 'base is not a positive integer: %s'  % str(base)
    assert type(pad) is str, 'pad is not a string: %s'  % str(pad)
    assert type(alphabet) is str, 'alphabet is not a string: %s'  % str(alphabet)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    assert type(b_pad) is str, 'b_pad is not a string: %s' % str(b_pad)
    
    assert base in [4, 8, 16, 32, 64], 'base must be either 4, 8, 16, 32 or 64: %d' % base
    assert len(pad) <= 1, 'pad is more that one character long: %s' % pad
    
    if not len(alphabet): alphabet = base_alphabets[str(base)] # Allow user to specify their own alphabet else use default.
    assert len(alphabet) == base, 'alphabet is not %d characters long: %s' % (base, alphabet)
    
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    assert b_pad == '0' or b_pad == '1', 'Invalid b_pad: "%s". Use either "0" or "1"' % b_pad
    
    # Return the active alphabet on empty input string.
    if not len(A): return alphabet
    
    from math import log, floor
    bits_per_char = int(floor(log(base, 2))) # Calculate the number of bits each character will represent.
    del log, floor
    
    bits_per_byte = 8 # Yes. this is obvious but I think it makes the following code more readable.
    
    # Calculate lowest common multiple using Euclid's method which is the group size in bits.
    a = bits_per_char
    b = bits_per_byte
    c = a * b
    while b: a, b = b, a % b
    group_size_bits = c / a                                 # Number of bits in each group
    group_size_bytes = group_size_bits / bits_per_byte      # Number of bytes per group
    del a, b, c, group_size_bits
    
    # Pad out the input b_string to be a multiple of 8 (bits_per_byte) bits long.
    lA = len(A)
    if align == 'left': A = A + b_pad * ((bits_per_byte - (lA % bits_per_byte)) % bits_per_byte)
    else:               A = b_pad * ((bits_per_byte - (lA % bits_per_byte)) % bits_per_byte) + A
    lA = len(A)
    
    # Make a temporary A sting which is padded on the right with zeros to make it a multiple of bits_per_char bits.
    Ac = A + '0' * ((bits_per_char - (lA % bits_per_char)) % bits_per_char)
    lA_c = len(Ac)
    
    # Generate string of new base.
    t = ''
    for i in range(0, lA_c, bits_per_char): t += alphabet[int(Ac[i:i+bits_per_char], 2)]
    del i, A, Ac, lA_c, bits_per_char
    
    # Add padding
    if len(pad): t += pad * ((group_size_bytes - ((lA / bits_per_byte) % group_size_bytes)) % group_size_bytes)
    
    return t
    # }}} End of b_to_baseX()

def baseX_to_b(instr='A', base=64, alphabet='', pad='='): # {{{
    '''
    Convert from another base to binary coding.
    
    This is performs to opposite function to b_to_baseX().
    The input base can be either 4, 8, 16, 32 or 64 (default).
    A user-defined alphabet can be supplied containing any characters in any
      order as long at the length is equal to the base using the alphabet
      argument.
    Supplying an empty input string will return in the alphabet which is used
      for that base.
    The default alphabets for bases 32 and 64 are taken from RCF 3548 and
      the alphabets used for bases 4, 8 and 16 are standard.
    If a character is used in the input string it must be specified using the
      pad argument.
    
    E.g. baseX_to_b() returns '00000000'
         baseX_to_b('') returns 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
         baseX_to_b('', base=4) returns '0123'
         baseX_to_b('', base=8) returns '01234567'
         baseX_to_b('', base=16) returns '0123456789ABCDEF'
         baseX_to_b('', base=32) returns 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
         baseX_to_b('', base=64) returns 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
         baseX_to_b('0123', base=4) returns '00011011'
         baseX_to_b('01234567', base=8) returns '000001010011100101110111'
         baseX_to_b('05AF', base=16) returns '0000010110101111'
         baseX_to_b('AZ27', base=32) returns '00000110011101011111'
         baseX_to_b('TWFu', base=64) returns '010011010110000101101110'
    '''
    
    # These are the default alphabets.
    # 4 is standard radix-4 notation.
    # 8 is standard octal notation.
    # 16 is standard hexadecimal notation (uppercase). This also appears in RFC 3548.
    # 32 and 64 are taken from RFC 3548.
    base_alphabets = {
                      '4'  : '0123',
                      '8'  : '01234567',
                      '16' : '0123456789ABCDEF',
                      '32' : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
                      '64' : 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
                     }
    
    assert type(base) is int, 'base is not a positive integer: %s'  % str(base)
    assert type(pad) is str, 'pad is not a string: %s'  % str(pad)
    assert type(alphabet) is str, 'alphabet is not a string: %s'  % str(alphabet)
    
    assert base in [4, 8, 16, 32, 64], 'base must be either 4, 8, 16, 32 or 64: %d' % base
    assert len(pad) <= 1, 'pad is more that one character long: %s' % pad
    
    if not len(alphabet): alphabet = base_alphabets[str(base)] # Allow user to specify their own alphabet else use default.
    assert len(alphabet) == base, 'alphabet is not %d characters long: %s' % (base, alphabet)
    
    # Return the active alphabet on empty input string.
    if not len(instr): return alphabet
    
    if len(pad): instr = instr.rstrip(pad)

    # Validate instr
    from re import compile as re_compile
    pattern = re_compile('[^' + alphabet + ']')
    assert bool(pattern.search(instr)) == False, 'instr contains characters not in the given alphabet'
    del re_compile, pattern
    
    from math import log, floor
    bits_per_char = int(floor(log(base, 2))) # Calculate the number of bits each character will represent.
    del log, floor
    
    # Generate string of new base.
    t = ''
    for c in instr: t += int_to_b(alphabet.find(c), width=bits_per_char)
    
    assert b_validate(t) == True, 'Something wrong in this function. t is not a valid b_string: %s' % str(t)
    
    return t
    # }}} End of baseX_to_b()

# }}} End of Base Conversion

# Miscellaneous Functions {{{

def b_blockify(A='', size=4, sep=' ', pad='', align='left'): # {{{
    '''
    Separate a string of binary digits into blocks.
    
    The size of the block is 4 by default but can be specified as any
      positive integer greater than 0.
    The alignment of the string can be specified as either left or right,
      and is left by default.
    The separating character is a space be default but can be specified
      as an arbitrary string (not required to be just a single character).
    There is no padding character by default but can also be specified as
      an arbitrary string.
    
    If the input is an empty string then an empty string will be returned.
    
    E.g. b_blockify() returns ''
         b_blockify('00000000') returns '0000 0000'
         b_blockify('0'*9) returns '0000 0000 0'
         b_blockify('0'*9, pad='x') returns '0000 0000 0xxx'
         b_blockify('0'*9, pad='x', align='right') returns 'xxx0 0000 0000'
         b_blockify('0'*9, sep='_') returns '0000_0000_0'
         b_blockify('0'*9, size='3') returns '000 000 000'
    '''
    assert b_validate(A, fail_empty=False) == True, 'A is not a valid b_string: %s' % str(A)
    assert type(size)  is int,  'size is not an integer: %s' % str(size)
    assert type(sep) is str, 'sep is not a string: %s' % str(sep)
    assert type(pad) is str, 'pad is not a string: %s' % str(pad)
    assert type(align) is str, 'align is not a string: %s' % str(align)
    
    assert size > 0, 'size is not a positive integer greater than zero: %d' % size
    assert align == 'right' or align == 'left', 'Invalid align: "%s". Use either "right" or "left"' % align
    
    if align == 'right': A = A[::-1]                                    # This is the most simple way to deal with alignment
    
    t = ''
    lenA = len(A)                                                       # Pre-calculate this to save doing it every iteration
    for i, c in enumerate(A):
        t += c
        if ((i + 1 + size) % size == 0) and (i < (lenA - 1)): t += sep  # Add separator
        del i, c
    
    t += pad*((size - (lenA % size)) % size)                            # Add padding
    
    del A, lenA

    if align == 'right': t = t[::-1]                                    # Correct alignment
    
    return t
    # }}} End of b_blockify()

def b_validate(A='', fail_empty=True): # {{{
    '''
    Validate that a given string contains only 0s and 1s.
    
    This will return True if the string is valid, otherwise it returns False.
    
    E.g. b_validate() returns False
         b_validate('') returns False
         b_validate('', fail_empty=False) returns True
         b_validate('01010101') returns True
         b_validate('010120101') returns False
         b_validate('0101 0101') returns False
    '''
    # Assertions cannot be used in here because when optimisation is turned on they
    #   will be compiled out.
    t = True
    
    if t and not(type(A) is str): t = False
    if t and fail_empty and not(len(A) > 0): t = False
    
    if t:
        from re import compile as re_compile
        pattern = re_compile('[^01]')
        t = not( bool(pattern.search(A)) )
        del re_compile, pattern
    
    return t
    # }}} End of b_validate()

# }}} End of Miscellaneous Functions

def run_self_test(): # {{{
    
    # Bitwise Operations {{{
    
    print('\nb_and()...')
    print(b_and.__doc__)
    print('\tTests:')
    print('\tb_and(\'0101\', \'0011\') = %s'                            % b_and('0101', '0011')                         )
    print('\tb_and(\'01010000\', \'0011\') = %s'                        % b_and('01010000', '0011')                     )
    print('\tb_and(\'01010000\', \'0011\', align=\'left\') = %s'        % b_and('01010000', '0011', align='left')       )
    
    print('\nb_nand()...')
    print(b_nand.__doc__)
    print('\tTests:')
    print('\tb_nand(\'0101\', \'0011\') = %s'                           % b_nand('0101', '0011')                        )
    print('\tb_nand(\'01010000\', \'0011\') = %s'                       % b_nand('01010000', '0011')                    )
    print('\tb_nand(\'01010000\', \'0011\', align=\'left\') = %s'       % b_nand('01010000', '0011', align='left')      )
    
    print('\nb_or()...')
    print(b_or.__doc__)
    print('\tTests:')
    print('\tb_or(\'0101\', \'0011\') = %s'                             % b_or('0101', '0011')                          )
    print('\tb_or(\'01010000\', \'0011\') = %s'                         % b_or('01010000', '0011')                      )
    print('\tb_or(\'01010000\', \'0011\', align=\'left\') = %s'         % b_or('01010000', '0011', align='left')        )
    
    print('\nb_nor()...')
    print(b_nor.__doc__)
    print('\tTests:')
    print('\tb_nor(\'0101\', \'0011\') = %s'                            % b_nor('0101', '0011')                         )
    print('\tb_nor(\'01010000\', \'0011\') = %s'                        % b_nor('01010000', '0011')                     )
    print('\tb_nor(\'01010000\', \'0011\', align=\'left\') = %s'        % b_nor('01010000', '0011', align='left')       )
                                                                                                                        
    print('\nb_xor()...')                                                                                               
    print(b_xor.__doc__)                                                                                                
    print('\tTests:')                                                                                                   
    print('\tb_xor(\'0101\', \'0011\') = %s'                            % b_xor('0101', '0011')                         )
    print('\tb_xor(\'01010000\', \'0011\') = %s'                        % b_xor('01010000', '0011')                     )
    print('\tb_xor(\'01010000\', \'0011\', align=\'left\') = %s'        % b_xor('01010000', '0011', align='left')       )
    
    print('\nb_nxor()...')
    print(b_nxor.__doc__)
    print('\tTests:')
    print('\tb_nxor(\'0101\', \'0011\') = %s'                           % b_nxor('0101', '0011')                        )
    print('\tb_nxor(\'01010000\', \'0011\') = %s'                       % b_nxor('01010000', '0011')                    )
    print('\tb_nxor(\'01010000\', \'0011\', align=\'left\') = %s'       % b_nxor('01010000', '0011', align='left')      )
    
    print('\nb_not()...')
    print(b_not.__doc__)
    print('\tTests:')
    print('\tb_not(\'0101\') = %s'                                      % b_not('0101')                                 )
    print('\tb_not() = %s'                                              % b_not()                                       )
    
    # }}} End of Bitwise Operations
    
    # Logical Operations {{{
    
    print('\nb_land()...')
    print(b_land.__doc__)
    print('\tTests:')
    print('\tb_land(\'11111111\') = %s'                                 % b_land('11111111')                            )
    print('\tb_land(\'01010000\') = %s'                                 % b_land('01010000')                            )
    print('\tb_land(\'00000000\') = %s'                                 % b_land('00000000')                            )
    
    print('\nb_lnand()...')
    print(b_lnand.__doc__)
    print('\tTests:')
    print('\tb_lnand(\'11111111\') = %s'                                % b_lnand('11111111')                           )
    print('\tb_lnand(\'01010000\') = %s'                                % b_lnand('01010000')                           )
    print('\tb_lnand(\'00000000\') = %s'                                % b_lnand('00000000')                           )
    
    print('\nb_lor()...')
    print(b_lor.__doc__)
    print('\tTests:')
    print('\tb_lor(\'11111111\') = %s'                                  % b_lor('11111111')                             )
    print('\tb_lor(\'01010000\') = %s'                                  % b_lor('01010000')                             )
    print('\tb_lor(\'00000000\') = %s'                                  % b_lor('00000000')                             )
    
    print('\nb_lnor()...')
    print(b_lnor.__doc__)
    print('\tTests:')
    print('\tb_lnor(\'11111111\') = %s'                                 % b_lnor('11111111')                            )
    print('\tb_lnor(\'01010000\') = %s'                                 % b_lnor('01010000')                            )
    print('\tb_lnor(\'00000000\') = %s'                                 % b_lnor('00000000')                            )
    
    print('\nb_lxor()...')
    print(b_lxor.__doc__)
    print('\tTests:')
    print('\tb_lxor(\'11111111\') = %s'                                 % b_lxor('11111111')                            )
    print('\tb_lxor(\'01010000\') = %s'                                 % b_lxor('01010000')                            )
    print('\tb_lxor(\'01110000\') = %s'                                 % b_lxor('01110000')                            )
    print('\tb_lxor(\'00000001\') = %s'                                 % b_lxor('00000001')                            )
    print('\tb_lxor(\'00000000\') = %s'                                 % b_lxor('00000000')                            )
    
    print('\nb_lnxor()...')
    print(b_lnxor.__doc__)
    print('\tTests:')
    print('\tb_lnxor(\'11111111\') = %s'                                % b_lnxor('11111111')                           )
    print('\tb_lnxor(\'01010000\') = %s'                                % b_lnxor('01010000')                           )
    print('\tb_lnxor(\'01110000\') = %s'                                % b_lnxor('01110000')                           )
    print('\tb_lnxor(\'00000001\') = %s'                                % b_lnxor('00000001')                           )
    print('\tb_lnxor(\'00000000\') = %s'                                % b_lnxor('00000000')                           )
    
    # }}} End of Logical Operations
    
    # Convertions To Binary Strings {{{
    
    print('\nint_to_b()...')
    print(int_to_b.__doc__)
    print('\tTests:')
    print('\tint_to_b() = %s'                                           % int_to_b()                                    )
    print('\tint_to_b(5) = %s'                                          % int_to_b(5)                                   )
    print('\tint_to_b(0xF5, width=10, endian=\'little\') = %s'          % int_to_b(0xF5, width=10, endian='little')     )
    print('\tint_to_b(0xF5, width=7) = %s'                              % int_to_b(0xF5, width=7)                       )
    print('\tint_to_b(0xF5, width=7, chop=\'least\') = %s'              % int_to_b(0xF5, width=7, chop='least')         )
    
    print('\nfrac_to_b()...')
    print(frac_to_b.__doc__)
    print('\tTests:')
    print('\tfrac_to_b() = %s'                                          % frac_to_b()                                   )
    print('\tfrac_to_b(0.3, 5) = %s'                                    % frac_to_b(0.3, 5)                             )
    print('\tfrac_to_b(0.5, width=10, endian=\'little\') = %s'          % frac_to_b(0.5, width=10, endian='little')     )
    
    print('\nstr_to_b()...')
    print(str_to_b.__doc__)
    print('\tTests:')
    print('\tstr_to_b() = %s'                                           % str_to_b()                                    )
    print('\tstr_to_b(\'\\x00\') = %s'                                  % str_to_b('\x00')                              )
    print('\tstr_to_b(\'abc\') = %s'                                    % str_to_b('abc')                               )
    print('\tstr_to_b(\'U\') = %s'                                      % str_to_b('U')                                 )
    print('\tstr_to_b(\'U\', endian=\'little\') = %s'                   % str_to_b('U', endian='little')                )
    print('\tstr_to_b(\'U\', char_width=7) = %s'                        % str_to_b('U', char_width=7)                   )
    print('\tstr_to_b(\'U\', prefix=\'1111\', suffix=\'0000\') = %s'    % str_to_b('U', prefix='1111', suffix='0000')   )
    print('\tstr_to_b(\'\\x00\', parity=\'pO\') = %s'                   % str_to_b('\x00', parity='pO')                 )
    print('\tstr_to_b(\'U\', parity=\'sE\') = %s'                       % str_to_b('U', parity='sE')                    )
    
    # }}} End of Convertions To Binary Strings
    
    # Gray Conversion {{{
    
    print('\nb_bin_to_gray()...')
    print(b_bin_to_gray.__doc__)
    print('\tTests:')
    print('\tb_bin_to_gray() = %s'                                      % b_bin_to_gray()                               )
    print('\tb_bin_to_gray(\'1111\') = %s'                              % b_bin_to_gray('1111')                         )
    print('\tb_bin_to_gray(\'1101\', endian=\'big\') = %s'              % b_bin_to_gray('1101', endian='big')           )
    print('\tb_bin_to_gray(\'1101\', endian=\'little\') = %s'           % b_bin_to_gray('1101', endian='little')        )
    
    print('\nb_gray_to_bin()...')
    print(b_gray_to_bin.__doc__)
    print('\tTests:')
    print('\tb_gray_to_bin() = %s'                                      % b_gray_to_bin()                               )
    print('\tb_gray_to_bin(\'1111\') = %s'                              % b_gray_to_bin('1111')                         )
    print('\tb_gray_to_bin(\'1101\', endian=\'big\') = %s'              % b_gray_to_bin('1101', endian='big')           )
    print('\tb_gray_to_bin(\'1101\', endian=\'little\') = %s'           % b_gray_to_bin('1101', endian='little')        )
    
    # }}} End of Gray Conversion
    
    # Arithmetic Operations {{{
    
    print('\nb_add()...')
    print(b_add.__doc__)
    print('\tTests:')
    print('\tb_add() = %s'                                              % b_add()                                       )
    print('\tb_add(\'0001\', \'0001\') = %s'                            % b_add('0001', '0001')                         )
    print('\tb_add(\'0001\', \'0001\', endian=\'little\') = %s'         % b_add('0001', '0001', endian='little')        )
    
    print('\nb_mul()...')
    print(b_mul.__doc__)
    print('\tTests:')
    print('\tb_mul() = %s'                                              % b_mul()                                       )
    print('\tb_mul(\'0001\', \'0001\') = %s'                            % b_mul('0001', '0001')                         )
    print('\tb_mul(\'0001\', \'0001\', endian=\'little\') = %s'         % b_mul('0001', '0001', endian='little')        )
    
    # }}} End of Arithmetic Operations
    
    # Base Conversion {{{
    
    print('\nb_to_baseX()...')
    print(b_to_baseX.__doc__)
    print('\tTests:')
    print('\tb_to_baseX() = %s'                                         % b_to_baseX()                                  )
    print('\tb_to_baseX(\'\') = %s'                                     % b_to_baseX('')                                )
    print('\tb_to_baseX(\'\', base=4) = %s'                             % b_to_baseX('', base=4)                        )
    print('\tb_to_baseX(\'\', base=8) = %s'                             % b_to_baseX('', base=8)                        )
    print('\tb_to_baseX(\'\', base=16) = %s'                            % b_to_baseX('', base=16)                       )
    print('\tb_to_baseX(\'\', base=32) = %s'                            % b_to_baseX('', base=32)                       )
    print('\tb_to_baseX(\'\', base=64) = %s'                            % b_to_baseX('', base=64)                       )
    print('\tb_to_baseX(\'00011011\', base=4) = %s'                     % b_to_baseX('00011011', base=4)                )
    print('\tb_to_baseX(\'000110111\', base=4) = %s'                    % b_to_baseX('000110111', base=4)               )
    print('\tb_to_baseX(\'0001101110\', base=4) = %s'                   % b_to_baseX('0001101110', base=4)              )
    print('\tb_to_baseX(\'000001010011100101110111\', base=8) = %s'     % b_to_baseX('000001010011100101110111', base=8))
    print('\tb_to_baseX(\'0000010110101111\', base=16) = %s'            % b_to_baseX('0000010110101111', base=16)       )
    print('\tb_to_baseX(\'0000010110101111\', base=32) = %s'            % b_to_baseX('0000010110101111', base=32)       )
    print('\tb_to_baseX(int_to_b(int(\'14FB9C03D97E\', 16), width=48)) = %s'
                                                                        % b_to_baseX(int_to_b(int('14FB9C03D97E', 16), width=48))       )
    print('\tb_to_baseX(int_to_b(int(\'14FB9C03D9\', 16), width=40)) = %s'
                                                                        % b_to_baseX(int_to_b(int('14FB9C03D9', 16), width=40))         )
    print('\tb_to_baseX(int_to_b(int(\'14FB9C03\', 16), width=32)) = %s'
                                                                        % b_to_baseX(int_to_b(int('14FB9C03', 16), width=32))           )
    print('\tb_to_baseX(int_to_b(int(\'14FB9C03\', 16), width=32), pad=\'\') = %s'
                                                                        % b_to_baseX(int_to_b(int('14FB9C03', 16), width=32), pad='')   )
    print('\tb_to_baseX(\'00011011\', base=4, alphabet=\'abcd\') = %s'  % b_to_baseX('00011011', base=4, alphabet='abcd')               )
    
    print('\nbaseX_to_b()...')
    print(baseX_to_b.__doc__)
    print('\tTests:')
    print('\tbaseX_to_b() = %s'                                         % baseX_to_b()                                  )
    print('\tbaseX_to_b(\'\') = %s'                                     % baseX_to_b('')                                )
    print('\tbaseX_to_b(\'\', base=4) = %s'                             % baseX_to_b('', base=4)                        )
    print('\tbaseX_to_b(\'\', base=8) = %s'                             % baseX_to_b('', base=8)                        )
    print('\tbaseX_to_b(\'\', base=16) = %s'                            % baseX_to_b('', base=16)                       )
    print('\tbaseX_to_b(\'\', base=32) = %s'                            % baseX_to_b('', base=32)                       )
    print('\tbaseX_to_b(\'\', base=64) = %s'                            % baseX_to_b('', base=64)                       )
    print('\tbaseX_to_b(\'0123\', base=4) = %s'                         % baseX_to_b('0123', base=4)                    )
    print('\tbaseX_to_b(\'01234567\', base=8) = %s'                     % baseX_to_b('01234567', base=8)                )
    print('\tbaseX_to_b(\'05AF\', base=16) = %s'                        % baseX_to_b('05AF', base=16)                   )
    print('\tbaseX_to_b(\'AZ27\', base=32) = %s'                        % baseX_to_b('AZ27', base=32)                   )
    print('\tbaseX_to_b(\'TWFu\', base=64) = %s'                        % baseX_to_b('TWFu', base=64)                   )
    
    # }}} End of Base Conversion
    
    # Miscellaneous Functions {{{
    
    print('\nb_blockify()...')
    print(b_blockify.__doc__)
    print('\tTests:')
    print('\tb_blockify() = %s'                                         % b_blockify()                                  )
    print('\tb_blockify(\'00000000\') = %s'                             % b_blockify('00000000')                        )
    print('\tb_blockify(\'0\'*9) = %s'                                  % b_blockify('0'*9)                             )
    print('\tb_blockify(\'0\'*9, pad=\'x\') = %s'                       % b_blockify('0'*9, pad='x')                    )
    print('\tb_blockify(\'0\'*9, pad=\'x\', align=\'right\') = %s'      % b_blockify('0'*9, pad='x', align='right')     )
    print('\tb_blockify(\'0\'*9, sep=\'_\') = %s'                       % b_blockify('0'*9, sep='_')                    )
    print('\tb_blockify(\'0\'*9, size=3) = %s'                          % b_blockify('0'*9, size=3)                     )
    
    print('\nb_validate()...')
    print(b_validate.__doc__)
    print('\tTests:')
    print('\tb_validate() = %s'                                         % b_validate()                                  )
    print('\tb_validate(\'\') = %s'                                     % b_validate('')                                )
    print('\tb_validate(\'\', fail_empty=False) = %s'                   % b_validate('', fail_empty=False)              )
    print('\tb_validate(\'01010101\') = %s'                             % b_validate('01010101')                        )
    print('\tb_validate(\'010120101\') = %s'                            % b_validate('010120101')                       )
    print('\tb_validate(\'0101 0101\') = %s'                            % b_validate('0101 0101')                       )
    
    # }}} End of Miscellaneous Functions
    
# }}} End of run_self_test()

if __name__ == '__main__': # {{{
    run_self_test()
# }}} End of __main__
