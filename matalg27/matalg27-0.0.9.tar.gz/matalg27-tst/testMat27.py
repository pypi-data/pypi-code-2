#!/usr/bin/env python
# testMat27.py - verify that Matalg27 works ok

# Copyright (C) 2011 Algis Kabaila 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later 
# version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free 
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor, 
# Boston, MA  02110-1301  USA
# You can contact the author by email algis.kabaila@gmail.com or
# paper mail PO Box 279 Jamison Centre ACT 214 Australia.

'''/dat/work/linalg/testMatalg.py - test module Matalg which is in the same
diretory
>>> amat = Matrix(3, 3)
>>> amat[0] = [25., 5., 1.]
>>> amat[1] = [64., 8., 1.]
>>> amat[2] = [144., 12., 1.]
>>> print 'amat[2, 0] =', amat[2, 0]
amat[2, 0] = 144.0
>>> print('amat = ')
amat = 
>>> amat.matprint()
[[25.0, 5.0, 1.0]
 [64.0, 8.0, 1.0]
 [144.0, 12.0, 1.0]]
>>> row = Matrix(1, 3)
>>> row[0] = [106.8, 177.2, 279.2]
>>> rhs = row.mattranspose()
>>> print('rhs matrix = ')
rhs matrix = 
>>> rhs.matprint()
[[106.8]
 [177.2]
 [279.2]]
>>> x = amat.solve(rhs)
>>> # x = (solved with pivoting)
>>> x.matprint()
[[0.2904761904761916]
 [19.690476190476172]
 [1.0857142857143396]]
>>> # Neater method of input/output:
>>> # Set one term
>>> x[1, 0] = 19.7
>>> x.matprint()
[[0.2904761904761916]
 [19.7]
 [1.0857142857143396]]
>>> cmat = Matrix(3, 3)
>>> cmat[0] = [5,  6, 7]
>>> cmat[1] = [10, 12, 3]
>>> cmat[2] = [20,  17, 19]
>>> cmat.matprint()
[[5, 6, 7]
 [10, 12, 3]
 [20, 17, 19]]
>>> rhs = Matrix(3, 1)
>>> rhs[0][0] = 18
>>> rhs[1][0] = 25
>>> rhs[2, 0] = 56
>>> x = cmat.solve(rhs)
>>> x.matprint()
[[1.0]
 [1.0]
 [1.0]]
'''
from matalg27 import Matalg27 as _m
Matrix = _m.Matrix

import doctest
doctest.testmod()

def printline(line):
    print line, 
    
printline('This works, if no failures reported...\n')
