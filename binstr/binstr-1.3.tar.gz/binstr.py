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
#
# To test that everything is working e.g. before a commit run the unit tests
#   with some commands like:
#   cd binstr
#   python binstr_test.py
#   python3 binstr_test.py
#
# When binstr.py is executed as __main__ it will simply print the docstrings of
#   all the functions using documentation().
# The docstring for documentation() will not be printed.

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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert b_validate(B) == True, \
        'Invalid b_string : B : %(actual)s' % {'actual': str(B)}
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    
    return ''.join([str(int( bool(int(a)) and bool(int(b)) )) for (a, b) in zip(p, q)])
    # }}} End of b_and()

def b_nand(A='00000000', B='00000000', align='right'): #{{{
    '''
    Perform a bitwise NAND on two strings of binary digits, A and B.
    The align argument can be used to align the shortest of A and B to one
      side of the other.
    The returned string is the same length as the longest input.
    E.g. b_nand('0101', '0011') returns '1110'
         b_nand('01010000', '0011') returns '11111111'
         b_nand('01010000', '0011', align='left') returns '11101111'
    '''
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert b_validate(B) == True, \
        'Invalid b_string : B : %(actual)s' % {'actual': str(B)}
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert b_validate(B) == True, \
        'Invalid b_string : B : %(actual)s' % {'actual': str(B)}
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert b_validate(B) == True, \
        'Invalid b_string : B : %(actual)s' % {'actual': str(B)}
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert b_validate(B) == True, \
        'Invalid b_string : B : %(actual)s' % {'actual': str(B)}
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert b_validate(B) == True, \
        'Invalid b_string : B : %(actual)s' % {'actual': str(B)}
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
    if len(A) >= len(B): (p, q) = (A, B)
    else:                (p, q) = (B, A)
    del A, B
    
    if align == 'right': q = '0'*(len(p) - len(q)) + q
    else:                q = q + '0'*(len(p) - len(q))
    
    return ''.join([str(int( not( bool(int(a)) ^ bool(int(b)) ) )) for (a, b) in zip(p, q)])
    # }}} End of b_nxor()

def b_not(A='00000000'): # {{{
    '''
    Perform a bitwise NOT (inversion) on an input string.
    The returned string is the same length as the input.
    E.g. b_or() returns '11111111'
         b_or('0101') returns '1010'
    '''
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
       
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
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
    
    The endianess is big by default but can be set to little to return a
      bit reversal.
    
    The returned string is can be converted to an int in Python by setting
      the base to 2 e.g.:'int( int_to_b(...) , 2 )'.
       
    E.g. int_to_b() returns '00000000'
         int_to_b(5) returns '00000101'
         int_to_b(0xF5, width=10, endian='little') returns '1010111100'
         int_to_b(0xF5, width=7) returns '1110101'
         int_to_b(0xF5, width=7, chop='least') returns '1111010'
    '''
    assert type(num) is int or type(num) is long, \
        'Invalid type : num : Expected %(expect)s : %(actual)s' % {
                                                                   'expect': str(type(int())) + ' OR ' + str(type(long())),
                                                                   'actual': str(type(num)),
                                                                  }
    
    assert num >= 0, \
        'Invalid value : num : Expected %(expect)s : %(actual)s' % {
                                                                    'expect': 'num >= 0',
                                                                    'actual': str(num),
                                                                   }
    
    assert type(width) is int, \
        'Invalid type : width : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(int())),
                                                                     'actual': str(type(width)),
                                                                    }
    
    assert width >= 0, \
        'Invalid value : width : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': 'width >= 0',
                                                                      'actual': str(width),
                                                                     }
    
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    
    assert type(chop) is str, \
        'Invalid type : chop : Expected %(expect)s : %(actual)s' % {
                                                                    'expect': str(type(str())),
                                                                    'actual': str(type(chop)),
                                                                   }
    
    assert chop == 'most' or chop == 'least', \
        'Invalid value: chop : Expected %(expect)s : %(actual)s' % {
                                                                    'expect': '"most" OR "least"',
                                                                    'actual': str(chop),
                                                                   }
    
    # The actual conversion. Not dependent on the behaviour of bin().
    a = num
    b = ''
    while a:
        b += str(a % 2)
        a = int(a / 2)
    t = b[::-1]
    del a, b
    
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
    
    The returned string is can be converted to an int in Python by setting
      the base to 2 e.g.:'int( frac_to_b(...) , 2 )'.
    
    E.g. frac_to_b() returns 00000000
         frac_to_b(0.3, 5) returns 01010
         frac_to_b(0.5, width=10, endian='little') returns 0000000001
    '''
    assert type(num) is float, \
        'Invalid type : num : Expected %(expect)s : %(actual)s' % {
                                                                   'expect': str(type(float())),
                                                                   'actual': str(type(num)),
                                                                  }
    
    assert num < 1.0, \
        'Invalid value : num : Expected %(expect)s : %(actual)s' % {
                                                                    'expect': 'num < 1.0',
                                                                    'actual': str(num),
                                                                   }
    
    assert type(width) is int, \
        'Invalid type : width : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(int())),
                                                                     'actual': str(type(width)),
                                                                    }
    
    assert width >= 0, \
        'Invalid value : width : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': 'width >= 0',
                                                                      'actual': str(width),
                                                                     }
    
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    
    a = int(round(num * 2**width)) # Move the most significant bit to the correct place and round.
    b = ''
    while a:
        b += str(a % 2)
        a = int(a / 2)
    t = b[::-1]
    del a, b
    
    if len(t) > width: t = t[:width]                    # Remove least significant bits
    else:              t = '0'*(width - len(t)) + t     # Add padding zeros
    
    if endian == 'little': t = t[::-1]         # Reverse the string
    
    return t
    # }}} End of frac_to_b()

def str_to_b(instr='', char_width=8, endian='big', prefix='', suffix='', parity='N'): # {{{
    '''
    Convert an ASCII string into a string of binary digits.
    
    The bit-endianness of each character can be set with the char_width and
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
    assert type(instr) is str, \
        'Invalid type : instr : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(instr)),
                                                                    }
    
    for (i, c) in enumerate(instr):
        assert ord(c) < 256, \
            'Invalid value : Character "%(c)s" (%(o)s) at position %(i)s is not valid ASCII (< 256)' % {
                                                                                                        'c': str(c),
                                                                                                        'o': ord(c),
                                                                                                        'i': str(i),
                                                                                                       }
    
    assert type(char_width) is int, \
        'Invalid type : char_width : Expected %(expect)s : %(actual)s' % {
                                                                          'expect': str(type(int())),
                                                                          'actual': str(type(char_width)),
                                                                         }
    
    assert char_width >= 0, \
        'Invalid value : char_width : Expected %(expect)s : %(actual)s' % {
                                                                           'expect': 'char_width >= 0',
                                                                           'actual': str(char_width),
                                                                          }
    
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    
    assert type(parity) is str, \
        'Invalid type : parity : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(parity)),
                                                                     }
    
    assert parity == 'N'  or \
           parity == 'pO' or \
           parity == 'sO' or \
           parity == 'pE' or \
           parity == 'sE', \
           'Invalid value: prefix : Expected %(expect)s : %(actual)s.' % {
                                                                          'expect': '"N" OR "pO" OR "sO" OR "pE" OR "sE"',
                                                                          'actual': str(prefix),
                                                                         }
    assert b_validate(prefix, fail_empty=False) == True, \
        'Invalid b_string : prefix : %(actual)s' % {'actual': str(prefix)}
    
    assert b_validate(suffix, fail_empty=False) == True, \
        'Invalid b_string : suffix : %(actual)s' % {'actual': str(suffix)}
    
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

def bytes_to_b(inbytes='', char_width=8, endian='big', prefix='', suffix='', parity='N'): # {{{
    '''
    Convert an byte sequence into a string of binary digits.
    When used in Python 2.x, where there is no support for bytes type this will
      simply return str_to_b().
    This should allow the same code to be compatible with Python 2 and 3 for reading files.
    E.g. bytes_to_b(open(<filename>, 'r').read())
    
    The bit-endianness of each character can be set with the char_width and
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

    E.g. bytes_to_b() returns ''
         bytes_to_b(b'\\x00') returns '00000000'
         bytes_to_b(b'abc') returns '011000010110001001100011'
         bytes_to_b(b'U') returns '01010101'
         bytes_to_b(b'U', endian='little') returns '10101010'
         bytes_to_b(b'U', char_width=7) returns '1010101'
         bytes_to_b(b'U', prefix='1111', suffix='0000') returns '1111010101010000'
         bytes_to_b(b'\\x00', parity='pO') returns '100000000'
         bytes_to_b(b'U', parity='sE') returns '010101010'
    '''
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    
    assert type(char_width) is int, \
        'Invalid type : char_width : Expected %(expect)s : %(actual)s' % {
                                                                          'expect': str(type(int())),
                                                                          'actual': str(type(char_width)),
                                                                         }
    
    assert char_width >= 0, \
        'Invalid value : char_width : Expected %(expect)s : %(actual)s' % {
                                                                           'expect': 'char_width >= 0',
                                                                           'actual': str(char_width),
                                                                          }
    
    assert type(parity) is str, \
        'Invalid type : parity : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(parity)),
                                                                     }
    
    assert parity == 'N'  or \
           parity == 'pO' or \
           parity == 'sO' or \
           parity == 'pE' or \
           parity == 'sE', \
           'Invalid value: prefix : Expected %(expect)s : %(actual)s.' % {
                                                                          'expect': '"N" OR "pO" OR "sO" OR "pE" OR "sE"',
                                                                          'actual': str(prefix),
                                                                         }
    
    assert b_validate(prefix, fail_empty=False) == True, \
        'Invalid b_string : prefix : %(actual)s' % {'actual': str(prefix)}
    
    assert b_validate(suffix, fail_empty=False) == True, \
        'Invalid b_string : suffix : %(actual)s' % {'actual': str(suffix)}
    
    if type(inbytes) is str:
        return str_to_b(instr=inbytes, char_width=char_width, endian=endian, prefix=prefix, suffix=suffix, parity=parity)
    else:
        assert type(inbytes) is bytes, \
            'Invalid type : inbytes : Expected %(expect)s : %(actual)s' % {
                                                                           'expect': str(type(bytes())),
                                                                           'actual': str(type(inbytes)),
                                                                          }
    t = ''
    for i, b in enumerate(inbytes):
        assert int(b) < 256, \
            'Invalid value : byte "%(b)s" at position %(i)s is not a valid byte (< 256)' % {
                                                                                            'b': str(b),
                                                                                            'i': str(i),
                                                                                           }
        b_c = int_to_b(int(b), width=char_width, endian=endian, chop='most')
        
        t += prefix
        
        if   parity == 'pO': t += b_lnxor(b_c)
        elif parity == 'pE': t += b_lxor(b_c)
        
        t += b_c
        
        if   parity == 'sO': t += b_lnxor(b_c)
        elif parity == 'sE': t += b_lxor(b_c)
        
        t += suffix
    
    return t
    # }}} End of bytes_to_b()

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
    
    E.g. baseX_to_b() returns '000000'
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
    
    assert type(base) is int, \
        'Invalid type : base : Expected %(expect)s : %(actual)s' % {
                                                                    'expect': str(type(int())),
                                                                    'actual': str(type(base)),
                                                                   }
    
    assert base in [4, 8, 16, 32, 64], \
        'Invalid value: base : Expected %(expect)s : %(actual)s' % {
                                                                    'expect': '4 OR 8 OR 16 OR 32 OR 64',
                                                                    'actual': str(base),
                                                                   }
    
    assert type(pad) is str, \
        'Invalid type : pad : Expected %(expect)s : %(actual)s' % {
                                                                   'expect': str(type(str())),
                                                                   'actual': str(type(pad)),
                                                                  }
    
    assert len(pad) <= 1, \
        'Invalid value: pad : Expected %(expect)s : %(actual)s' % {
                                                                   'expect': 'len(pad) <= 1',
                                                                   'actual': str(len(pad)),
                                                                  }
    
    assert type(alphabet) is str, \
        'Invalid type : alphabet : Expected %(expect)s : %(actual)s' % {
                                                                        'expect': str(type(str())),
                                                                        'actual': str(type(alphabet)),
                                                                       }
    
    if not len(alphabet): alphabet = base_alphabets[str(base)] # Allow user to specify their own alphabet else use default.
    assert len(alphabet) == base, \
        'Invalid value: alphabet : Expected %(expect)s : %(actual)s' % {
                                                                        'expect': 'len(alphabet) == base',
                                                                        'actual': str(len(alphabet)),
                                                                       }
    
    assert type(instr) is str, \
        'Invalid type : instr : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(instr)),
                                                                    }
    # Return the active alphabet on empty input string.
    if not len(instr): return alphabet
    
    if len(pad): instr = instr.rstrip(pad) # Remove padding characters

    # Validate instr
    from re import compile as re_compile
    pattern = re_compile('[^' + alphabet + ']')
    assert bool(pattern.search(instr)) == False, \
        'Invalid value: instr : Contains characters not in given alphabet'
    del re_compile, pattern
    
    from math import log
    bits_per_char = int(log(base, 2)) # Calculate the number of bits each character will represent.
    del log
    
    # Generate string of new base.
    t = ''
    for c in instr: t += int_to_b(alphabet.find(c), width=bits_per_char)
    
    return t
    # }}} End of baseX_to_b()

# }}} End of Convertions To Binary Strings

# Convertions From Binary Strings {{{

def b_to_int(A='0', endian='big'): # {{{
    '''
    Convert binary string of digits to an integer.
    
    The endianess is big by default but can be set to little to return a
      bit reversal.
    
    This is basically just a wrapper for the inbuilt Python function int()
      which is defined for completeness.
       
    E.g. b_to_int('00000000') returns 0
         b_to_int('0101') returns 5
         b_to_int('0101', endian='little') returns 10
    '''
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    t = ''
    if endian == 'big': t = A
    else:               t = A[::-1]
    return int(t, 2)
    # }}} End of b_to_int()

def b_to_frac(A='0', endian='big'): # {{{
    '''
    Convert a binary string to a positive float which is less than 1.0.
    
    The endianess is little by default but can be set to big to return a
      bit reversal.
    
    E.g. b_to_frac('00000000') returns 0.0
         b_to_frac('0101') returns 0.3125
    '''
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    
    if endian == 'little': A = A[::-1]
    
    t = 0.0
    for i, b in enumerate(A):
        if b == '1': t += 1.0 / 2**(i+1)
    
    return t
    # }}} End of b_to_frac()

def b_to_str(A='', align='left', b_pad='0'): # {{{
    '''
    Convert a b_string to an ASCII string suitable for writing to a file in
      binary mode.
    
    The input will be padded to a multiple of 8 bits long and can be controlled
      with the arguments align and b_pad.

    E.g. b_to_str() returns ''
         b_to_str('') returns ''
         b_to_str('0') returns '\\x00'
         b_to_str('1') returns '\\x80'
         b_to_str('01010101') returns 'U'
         b_to_str('011000010110001001100011') returns 'abc'
         b_to_str('0110000101100010011000111') returns 'abc\\x80'
    '''
    assert b_validate(A, fail_empty=False) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
    assert type(b_pad) is str, \
        'Invalid type : b_pad : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(b_pad)),
                                                                    }
    
    assert b_pad == '0' or b_pad == '1', \
        'Invalid value: b_pad : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"0" OR "1"',
                                                                     'actual': str(len(b_pad)),
                                                                    }
    
    # Pad out the input b_string to be a multiple of 8 (bits_per_byte) bits long.
    if align == 'left': A = A + b_pad * ((8 - (len(A) % 8)) % 8)
    else:               A = b_pad * ((8 - (len(A) % 8)) % 8) + A
    
    t = ''
    for i in range(0, len(A), 8): t += chr(int(A[i:i+8], 2))
       
    return t
    # }}} End of b_to_str()

def b_to_bytes(A='', align='left', b_pad='0'): # {{{
    '''
    Convert a b_string to an byte sequence suitable for writing to a file in
      binary mode.
    
    The input will be padded to a multiple of 8 bits long and can be controlled
      with the arguments align and b_pad.

    E.g. b_to_bytes() returns b''
         b_to_bytes('') returns b''
         b_to_bytes('0') returns b'\\x00'
         b_to_bytes('1') returns b'\\x01'
         b_to_bytes('01010101') returns b'U'
         b_to_bytes('011000010110001001100011') returns b'abc'
         b_to_bytes('0110000101100010011000111') returns b'abc\\x80'
    '''
    assert b_validate(A, fail_empty=False) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
    assert type(b_pad) is str, \
        'Invalid type : b_pad : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(b_pad)),
                                                                    }
    
    assert b_pad == '0' or b_pad == '1', \
        'Invalid value: b_pad : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"0" OR "1"',
                                                                     'actual': str(len(b_pad)),
                                                                    }
    
    if type(bytes()) is str:
        return b_to_str(A=A, align=align, b_pad=b_pad)
    else:
        # Pad out the input b_string to be a multiple of 8 (bits_per_byte) bits long.
        if align == 'left': A = A + b_pad * ((8 - (len(A) % 8)) % 8)
        else:               A = b_pad * ((8 - (len(A) % 8)) % 8) + A
        
        t = []
        for i in range(0, len(A), 8): t.append(int(A[i:i+8], 2))
        
        return bytes(t)
    # }}} End of b_to_bytes()

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
    
    assert b_validate(A, fail_empty=False) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert type(base) is int, \
        'Invalid type : base : Expected %(expect)s : %(actual)s' % {
                                                                    'expect': str(type(int())),
                                                                    'actual': str(type(base)),
                                                                   }
    
    assert base in [4, 8, 16, 32, 64], \
        'Invalid value: base : Expected %(expect)s : %(actual)s' % {
                                                                    'expect': '4 OR 8 OR 16 OR 32 OR 64',
                                                                    'actual': str(base),
                                                                   }
    
    assert type(pad) is str, \
        'Invalid type : pad : Expected %(expect)s : %(actual)s' % {
                                                                   'expect': str(type(str())),
                                                                   'actual': str(type(pad)),
                                                                  }
    
    assert len(pad) <= 1, \
        'Invalid value: pad : Expected %(expect)s : %(actual)s' % {
                                                                   'expect': 'len(pad) <= 1',
                                                                   'actual': str(len(pad)),
                                                                  }
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
    assert type(b_pad) is str, \
        'Invalid type : b_pad : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(b_pad)),
                                                                    }
    
    assert b_pad == '0' or b_pad == '1', \
        'Invalid value: b_pad : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"0" OR "1"',
                                                                     'actual': str(len(b_pad)),
                                                                    }
    
    assert type(alphabet) is str, \
        'Invalid type : alphabet : Expected %(expect)s : %(actual)s' % {
                                                                        'expect': str(type(str())),
                                                                        'actual': str(type(alphabet)),
                                                                       }
    
    if not len(alphabet): alphabet = base_alphabets[str(base)] # Allow user to specify their own alphabet else use default.
    assert len(alphabet) == base, \
        'Invalid value: alphabet : Expected %(expect)s : %(actual)s' % {
                                                                        'expect': 'len(alphabet) == base',
                                                                        'actual': str(len(alphabet)),
                                                                       }
    
    # Return the active alphabet on empty input string.
    if not len(A): return alphabet
    
    from math import log
    bits_per_char = int(log(base, 2)) # Calculate the number of bits each character will represent.
    del log
    
    bits_per_byte = 8 # Yes. this is obvious but I think it makes the following code more readable.
    
    # Calculate lowest common multiple using Euclid's method which is the group size in bits.
    a = bits_per_char
    b = bits_per_byte
    c = a * b
    while b: a, b = b, a % b
    group_size_bits = int(c / a)                            # Number of bits in each group
    group_size_bytes = int(group_size_bits / bits_per_byte) # Number of bytes per group
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
    if len(pad): t += pad * ((group_size_bytes - (int(lA / bits_per_byte) % group_size_bytes)) % group_size_bytes)
    
    return t
    # }}} End of b_to_baseX()

# }}} End of Convertions From Binary Strings

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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    
    if endian == 'little': A = A[::-1] # Make sure endianness is big before conversion
    
    g = A[0]
    for i in range(1, len(A)): g += str( int(A[i-1] != A[i]) )
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert b_validate(B) == True, \
        'Invalid b_string : B : %(actual)s' % {'actual': str(B)}
    
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    
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
    assert b_validate(A) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert b_validate(B) == True, \
        'Invalid b_string : B : %(actual)s' % {'actual': str(B)}
    
    assert type(endian) is str, \
        'Invalid type : endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': str(type(str())),
                                                                      'actual': str(type(endian)),
                                                                     }
    
    assert endian == 'little' or endian == 'big', \
        'Invalid value: endian : Expected %(expect)s : %(actual)s' % {
                                                                      'expect': '"little" OR "big"',
                                                                      'actual': str(endian),
                                                                     }
    
    if endian == 'little':                     # Ensure both inputs are big endian before the add 
        A = A[::-1]
        B = B[::-1]
    
    if len(A) >= len(B): l = A
    else:                l = B
    
    return int_to_b(num=(int(A, 2) * int(B, 2)), width=(len(l) * 2), endian=endian, chop='most')
    # }}} End of b_mul()

# }}} End of Arithmetic Operations

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
      an arbitrary string (not required to be just a single character).
    
    If the input is an empty string then an empty string will be returned.
    
    E.g. b_blockify() returns ''
         b_blockify('00000000') returns '0000 0000'
         b_blockify('0'*9) returns '0000 0000 0'
         b_blockify('0'*9, pad='x') returns '0000 0000 0xxx'
         b_blockify('0'*9, pad='x', align='right') returns 'xxx0 0000 0000'
         b_blockify('0'*9, sep='_') returns '0000_0000_0'
         b_blockify('0'*9, size='3') returns '000 000 000'
    '''
    assert b_validate(A, fail_empty=False) == True, \
        'Invalid b_string : A : %(actual)s' % {'actual': str(A)}
    
    assert type(size) is int, \
        'Invalid type : size : Expected %(expect)s : %(actual)s' % {
                                                                    'expect': str(type(int())),
                                                                    'actual': str(type(size)),
                                                                   }
    
    assert size > 0, \
        'Invalid value : size : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': 'size > 0',
                                                                     'actual': str(size),
                                                                    }
    
    assert type(sep) is str, \
        'Invalid type : sep : Expected %(expect)s : %(actual)s' % {
                                                                   'expect': str(type(str())),
                                                                   'actual': str(type(sep)),
                                                                  }
    
    assert type(pad) is str, \
        'Invalid type : pad : Expected %(expect)s : %(actual)s' % {
                                                                   'expect': str(type(str())),
                                                                   'actual': str(type(pad)),
                                                                  }
    
    assert type(align) is str, \
        'Invalid type : align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': str(type(str())),
                                                                     'actual': str(type(align)),
                                                                    }
    
    assert align == 'right' or align == 'left', \
        'Invalid value: align : Expected %(expect)s : %(actual)s' % {
                                                                     'expect': '"left" OR "right"',
                                                                     'actual': str(align),
                                                                    }
    
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

def documentation(): # {{{
    '''
    Return all the docstrings in a string suitable for printing to STDOUT.
    '''
    t = ''

    # Bitwise Operations {{{
    
    t += '\nb_and()...'     + b_and.__doc__
    t += '\nb_nand()...'    + b_nand.__doc__
    t += '\nb_or()...'      + b_or.__doc__
    t += '\nb_nor()...'     + b_nor.__doc__
    t += '\nb_xor()...'     + b_xor.__doc__
    t += '\nb_nxor()...'    + b_nxor.__doc__
    t += '\nb_not()...'     + b_not.__doc__
    
    # }}} End of Bitwise Operations
    
    # Logical Operations {{{
    
    t += '\nb_land()...'    + b_land.__doc__
    t += '\nb_lnand()...'   + b_lnand.__doc__
    t += '\nb_lor()...'     + b_lor.__doc__
    t += '\nb_lnor()...'    + b_lnor.__doc__
    t += '\nb_lxor()...'    + b_lxor.__doc__
    t += '\nb_lnxor()...'   + b_lnxor.__doc__
    
    # }}} End of Logical Operations
    
    # Convertions To Binary Strings {{{
    
    t += '\nint_to_b()...'      + int_to_b.__doc__
    t += '\nfrac_to_b()...'     + frac_to_b.__doc__
    t += '\nstr_to_b()...'      + str_to_b.__doc__
    t += '\nbytes_to_b()...'    + bytes_to_b.__doc__
    t += '\nbaseX_to_b()...'    + baseX_to_b.__doc__
    
    # }}} End of Convertions To Binary Strings
    
    # Convertions From Binary Strings {{{
    
    t += '\nb_to_int()...'      + b_to_int.__doc__
    t += '\nb_to_frac()...'     + b_to_frac.__doc__
    t += '\nb_to_str()...'      + b_to_str.__doc__
    t += '\nb_to_bytes()...'    + b_to_bytes.__doc__
    t += '\nb_to_baseX()...'    + b_to_baseX.__doc__
    
    # }}} End of Convertions From Binary Strings
    
    # Gray Conversion {{{
    
    t += '\nb_bin_to_gray()...' + b_bin_to_gray.__doc__
    t += '\nb_gray_to_bin()...' + b_gray_to_bin.__doc__
    
    # }}} End of Gray Conversion
    
    # Arithmetic Operations {{{
    
    t += '\nb_add()...' + b_add.__doc__
    t += '\nb_mul()...' + b_mul.__doc__
    
    # }}} End of Arithmetic Operations
    
    # Miscellaneous Functions {{{
    
    t += '\nb_blockify()...'    + b_blockify.__doc__
    t += '\nb_validate()...'    + b_validate.__doc__
    
    # }}} End of Miscellaneous Functions
    
    return t
    
# }}} End of documentation()

if __name__ == '__main__': # {{{
    print(documentation())
# }}} End of __main__
