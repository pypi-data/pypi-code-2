#!/usr/bin/env python3
# testMat.py - verify that wrapnumpy works ok

# Copyright (c) 2011 Algis Kabaila. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided and is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public Licence for more details.

'''
>>> print('testing...')
testing...
>>> utils = _m.Utilities() 
>>> mat = utils.enterdata(2, 2, [ [-0.5714285714285714, 0.7142857142857142],\
                [0.42857142857142855, -0.2857142857142857] ])
Echo check of enterdata
A matrix of dimensions (m x n), where m, n, LineLen =  2 2 5 
  -5.71429E-01   7.14286E-01 
   4.28571E-01  -2.85714E-01 
<BLANKLINE>
>>> mat.neatprint()
A matrix of dimensions (m x n), where m, n, LineLen =  2 2 5 
  -5.71429E-01   7.14286E-01 
   4.28571E-01  -2.85714E-01 
<BLANKLINE> 
>>> amat = utils.enterdata(3, 3,\
            [ [25.0, 5.0, 1.0],\
            [64.0, 8.0, 1.0],\
            [144.0, 12.0, 1.0] ])
Echo check of enterdata
A matrix of dimensions (m x n), where m, n, LineLen =  3 3 5 
   2.50000E+01   5.00000E+00   1.00000E+00 
   6.40000E+01   8.00000E+00   1.00000E+00 
   1.44000E+02   1.20000E+01   1.00000E+00 
<BLANKLINE>
>>> rhs = utils.enterdata(3, 1,\
            [[106.8], [177.2], [279.2]])
Echo check of enterdata
A matrix of dimensions (m x n), where m, n, LineLen =  3 1 5 
   1.06800E+02 
   1.77200E+02 
   2.79200E+02 
<BLANKLINE> 
>>> x = amat ** rhs
>>> print('solution x =')
solution x =
>>> x.neatprint()
A matrix of dimensions (m x n), where m, n, LineLen =  3 1 5 
   2.90476E-01 
   1.96905E+01 
   1.08571E+00 
<BLANKLINE> 
>>> print('Matrix inverse. amat = ')
Matrix inverse. amat = 
>>> amat.neatprint()
A matrix of dimensions (m x n), where m, n, LineLen =  3 3 5 
   2.50000E+01   5.00000E+00   1.00000E+00 
   6.40000E+01   8.00000E+00   1.00000E+00 
   1.44000E+02   1.20000E+01   1.00000E+00 
<BLANKLINE>  
>>> print('Inverse of amat = ')
Inverse of amat = 
>>> result = ~amat
>>> result.neatprint()
A matrix of dimensions (m x n), where m, n, LineLen =  3 3 5 
   4.76190E-02  -8.33333E-02   3.57143E-02 
  -9.52381E-01   1.41667E+00  -4.64286E-01 
   4.57143E+00  -5.00000E+00   1.42857E+00 
<BLANKLINE> 
>>> x = result * rhs
>>> x.neatprint()
A matrix of dimensions (m x n), where m, n, LineLen =  3 1 5 
   2.90476E-01 
   1.96905E+01 
   1.08571E+00 
<BLANKLINE>
>>> print('Matrix addition and subtraction.')
Matrix addition and subtraction.
>>> amat = utils.enterdata(2, 3,\
            [ [3, 5, 1,], \
              [ 3, 6, 7]])
Echo check of enterdata
A matrix of dimensions (m x n), where m, n, LineLen =  2 3 5 
   3.00000E+00   5.00000E+00   1.00000E+00 
   3.00000E+00   6.00000E+00   7.00000E+00 
<BLANKLINE>
>>> bmat = utils.enterdata(2, 3, \
            [ [3, 6, 7], \
              [4, 5, 4]])
Echo check of enterdata
A matrix of dimensions (m x n), where m, n, LineLen =  2 3 5 
   3.00000E+00   6.00000E+00   7.00000E+00 
   4.00000E+00   5.00000E+00   4.00000E+00 
<BLANKLINE>
>>> rmat = amat + bmat
>>> print('amat + bmat =')
amat + bmat =
>>> rmat.neatprint()
A matrix of dimensions (m x n), where m, n, LineLen =  2 3 5 
   6.00000E+00   1.10000E+01   8.00000E+00 
   7.00000E+00   1.10000E+01   1.10000E+01 
<BLANKLINE>
>>> x = rmat - amat
>>> x.neatprint()
A matrix of dimensions (m x n), where m, n, LineLen =  2 3 5 
   3.00000E+00   6.00000E+00   7.00000E+00 
   4.00000E+00   5.00000E+00   4.00000E+00 
<BLANKLINE>
'''

if __name__ == '__main__':
    from wrapnumpy3 import wrapnumpy3 as _m

    Matrix = _m.Matrix
    
    import doctest
    doctest.testmod()
    
    print('This works, if no failures reported...')
    
