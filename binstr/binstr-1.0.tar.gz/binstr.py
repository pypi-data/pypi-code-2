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
# It has been designed to be completely predictable, i.e. strange inputs
#   will cause an AssertionError to be raised.
#
# It is not intended to be the fastest or most efficient.
# In fact it should not be used unless you are specifically interested in
#   operating on strings.
#
# However, it is useful for ensuring the correctness of each bit in an
#   easy-to-use and easily printable manner.
# This fits in well when generating code in other languages like Verilog,
#   C and Assembler.
# Obviously the other main use would be if you already have strings of
#   binary that you need to fiddle with.

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
    assert endian == 'little' or endian == 'big', 'Invalid endian: \'%s\'. Use either \'little\' or \'big\'' % endian
    assert chop == 'most' or chop == 'least', 'Invalid chop: \'%s\'. Use either \'most\' or \'least\''   % chop
    
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
    assert endian ==   'little' or endian == 'big', 'Invalid endian: \'%s\'. Use either \'little\' or \'big\'' % str(endian)
    
    num *= 2**width
    t = bin(int(round(num)))            # bin() returns a string with a '0b' prefix that we don't want
    assert t[:2] == '0b',               'bin() is not behaving as expected. bin(num) = %s' % t
    t = t[2:]
    
    if len(t) > width: t = t[:width]                    # Remove least significant bits
    else:              t = '0'*(width - len(t)) + t     # Add padding zeros
    
    if endian == 'little': t = t[::-1]         # Reverse the string
    
    return t
    # }}} End of frac_to_b()

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
    assert align == 'right' or align == 'left', 'Invalid align: \'%s\'. Use either \'right\' or \'left\'' % align

    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: \'%s\'. Must only contain \'0\'s or \'1\'s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: \'%s\'. Must only contain \'0\'s or \'1\'s.' % B
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
    assert align == 'right' or align == 'left', 'Invalid align: \'%s\'. Use either \'right\' or \'left\'' % align

    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: \'%s\'. Must only contain \'0\'s or \'1\'s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: \'%s\'. Must only contain \'0\'s or \'1\'s.' % B
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
    assert align == 'right' or align == 'left', 'Invalid align: \'%s\'. Use either \'right\' or \'left\'' % align

    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: \'%s\'. Must only contain \'0\'s or \'1\'s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: \'%s\'. Must only contain \'0\'s or \'1\'s.' % B
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
    assert align == 'right' or align == 'left', 'Invalid align: \'%s\'. Use either \'right\' or \'left\'' % align

    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: \'%s\'. Must only contain \'0\'s or \'1\'s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: \'%s\'. Must only contain \'0\'s or \'1\'s.' % B
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
    assert align == 'right' or align == 'left', 'Invalid align: \'%s\'. Use either \'right\' or \'left\'' % align

    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: \'%s\'. Must only contain \'0\'s or \'1\'s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: \'%s\'. Must only contain \'0\'s or \'1\'s.' % B
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
    assert align == 'right' or align == 'left', 'Invalid align: \'%s\'. Use either \'right\' or \'left\'' % align

    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: \'%s\'. Must only contain \'0\'s or \'1\'s.' % A
    assert bool(pattern.search(B)) == False, 'Invalid B: \'%s\'. Must only contain \'0\'s or \'1\'s.' % B
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
    assert bool(pattern.search(A)) == False, 'Invalid A: \'%s\'. Must only contain \'0\'s or \'1\'s.' % A
    del re_compile, pattern

    return ''.join([str(int( not( bool(int(a)) ) )) for a in A])
    # }}} End of b_not()

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
    assert endian == 'little' or endian == 'big', 'Invalid endian: \'%s\'. Use either \'little\' or \'big\'' % str(endian)

    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: \'%s\'. Must only contain \'0\'s or \'1\'s.' % str(A)
    assert bool(pattern.search(B)) == False, 'Invalid B: \'%s\'. Must only contain \'0\'s or \'1\'s.' % B
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
    assert endian == 'little' or endian == 'big', 'Invalid endian: \'%s\'. Use either \'little\' or \'big\'' % str(endian)

    from re import compile as re_compile
    pattern = re_compile('[^01]')
    assert bool(pattern.search(A)) == False, 'Invalid A: \'%s\'. Must only contain \'0\'s or \'1\'s.' % str(A)
    assert bool(pattern.search(B)) == False, 'Invalid B: \'%s\'. Must only contain \'0\'s or \'1\'s.' % B
    del re_compile, pattern

    if endian == 'little':                     # Ensure both inputs are big endian before the add 
        A = A[::-1]
        B = B[::-1]
    
    if len(A) >= len(B): l = A
    else:                l = B

    return int_to_b(num=(int(A, 2) * int(B, 2)), width=(len(l) * 2), endian=endian, chop='most')
    # }}} End of b_mul()

def run_self_test(): # {{{
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

# }}} End of run_self_test()

if __name__ == '__main__': # {{{
    run_self_test()
# }}} End of __main__
