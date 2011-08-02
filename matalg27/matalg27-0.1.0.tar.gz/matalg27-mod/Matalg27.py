#!/usr/bin/env python2.7
'''Matalg27.py - module for Matrix ("mat") class.
Version for Python2.7.
'''
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

import sys

__version__ = '0.1.0'

# Utility functions. --------------------------------
def find_max(lst):
    '''Find maximum *absolute* value of entries in a list, together
    with its offsetfrom origin.'''
    lst2 = [abs(v) for v in lst]
    index = lst2.index(max(lst2))
    amax = lst[index]
    return amax, index

def printline(line):
    'Function to simmulate appending to a plainText widget.'
    print line,

# Matrix class with its methods.---------------------
class Matrix(list):
    '''"Matrix" creates a (m x n) matrix of float 0.'s'''
    def __init__(self, m=1, n=1):
        '''m = no of rows, n = no of columns.'''
        self.m = m
        self.n = n  
        row = []
        for j in range(n):
            row.append(0.0)
        for i in range(m):
            self.append(row[:])
        self.flag = ' '  # flag signals type of binary operation

    def __getitem__(self, key):
        if isinstance(key, int):
            return super(Matrix, self).__getitem__(key)
        else:    
            if isinstance(key, tuple):
                if len(key) == 2:
                    i, j = key
                    return self[i][j]
                elif len(key) == 3:
                    i, j, k = key
                    return self[i][j][k]
                elif len(key) == 4:
                    i, j, k, l = key
                    return self[i][j][k][l]       
                else:
                    print('key is not int nor llen(tuple)>4-fail')
                    raise NotImplementedError()

    def __setitem__(self, key, value):
##        value = float(value)
        if isinstance(key, int):
            super(Matrix, self).__setitem__(key, value)
        elif type(key) is tuple:
            if len(key) == 2:
                i, j = key
                self[i][j] = value
            elif len(key) == 3:
                i, j, k = key
                self[i][j][k] = value
            elif len(key) == 4:
                i,j,k,l = key
                self[i][j][k][l] = value                        
            else:
                raise NotImplementedError()
            
    def __str__(self):
        if not isinstance(self, Matrix):
            return NotImplemented
        else:           
            s = ''
            for i in range(self.m):
                if i == self.m - 1:
                    s += self[i].__str__()
                else:
                    s += self[i].__str__() + '\n'
            return s    

    def __eq__(self, other):
        if isinstance(self, Matrix) and isinstance(other, Matrix):
            return self.matequal(other)
        else:
            return NotImplemented
      
    def __add__(self, other):
        if isinstance(self, Matrix) and isinstance(other, Matrix):
            return self.matadd(other)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(self, Matrix) and isinstance(other, Matrix):
            return self.matsub(other)
        else:
            return NotImplemented
        
    def __mul__(self, other):
        '''Matrix multiplication: [ * ] when both self and other
        are matrices. When one is a scalar and the other is a
        matrix, scalar multiplicatin of a matrix.
        '''
        if isinstance(self, Matrix) and isinstance(other, Matrix):
            assert self.n == other.m, 'Not compatible for multiplication'
##          Matrix multiplication
            return self.matmult(other)
        elif isinstance(self, Matrix) and (type(other) in (float, int)):
            return self.scalarmult(other)
##            return self
        elif (type(self) in (float, int)) and isinstance(other, Matrix):
            return NotImplemented
        else:
            return NotImplemented
        
    def __rmul__(self, other):
        "number * matrix --> matrix"
        if (type(other) in (float, int)) and isinstance(self, Matrix):
            return self.scalarmult(other)
##            return self

    def __invert__(self):
        '''
        [ ~ ] Matrix inversion).
        '''
        if isinstance(self, Matrix):
            return self.matinvert()
        else:
            return NotImplemented

    def __pow__(self, other):
        '''
        [ ** ] Equation solver for x = self * rhs ).
        '''
        if isinstance(self, Matrix) and isinstance(other, Matrix):
            return self.solve(other)
        else:
            return NotImplemented       

    
    def matprint(self):
        'Usage: to print amat issue amat.matprint() .'
        m = self.m
        if m < 2:
            print('[' + self[0].__str__() + ']')
        else:
            for i in range(m):
                if i == 0:
                    print('[' + self[i].__str__())                    
                elif i < (m-1):
                    print(' ' + self[i].__str__())
                else:
                    print(' ' + self[i].__str__() + ']')
                
    def matmult(self, other):
        "self.matmult(other) --> matrix product self x other."
        m = self.m
        n = self.n
        assert self.n == other.m, 'incompatible for mat mult.'
        k = other.n
        result = Matrix(m, k)
        for i in range(m):
            for j in range(k):
                result[i][j] = 0.0
                for l in range(n):
                    result[i][j] += self[i][l] * other[l][j]
        return result
        
    def matadd(self, other):
        'return (mat add) = self + other'
        assert self.m == other.m, 'must be same size'
        assert self.n == other.n, 'must be same size'
        self.flag = 'a'
        return self.matbinop(other)        
        
    def matsub(self, other):
        'return (mat Subtract) = self - other.'
        assert self.m == other.m, 'must be same size'
        assert self.n == other.n, 'must be same size'
        self.flag = 's'
        return  self.matbinop(other)
        
    def scalarmult(self, factor):
        '''Multiply matrix by scalar (in place).
           ("in place" is not a "good place"...
           better return the result in a new matrix!)
'''
        other = Matrix(self.m, self.n)
        for i in range(self.m):
            for j in range(self.n):
                other[i][j] = factor * self[i][j]
        return other
    
    def matcopy(self):
        'Creates and returns a copy of the matrix.'
        other = Matrix(self.m, self.n)
        for i in range(self.m):
            other[i] = self[i][:]
        return other
        
    def matbinop(self, other):
        'Mat addition and subtraction.'
        assert self.m == other.m, 'must be same size'
        assert self.n == other.n, 'must be same size'
        flag = self.flag
        result = Matrix(other.m, other.n)
        for i in range(other.m):
            for j in range(other.n):
                if flag == 'a': 
                    result[i][j] = self[i][j] + other[i][j]
                elif flag == 's':
                    result[i][j] = self[i][j] - other[i][j]
                else:
                    print('should never happen...')
                    sys.exit([1])
        return result
               
    def matunit(self):
        'Make self unit matrix and return it.'
        m = self.m
        n = self.n
        assert m == n, 'Unary matrix must be square.'
        for i in range(m):
            for j in range(n):
                self[i][j] = 0.0
                if i == j:
                    self[i][j] = 1.0
        return self

    def transp(self, other):
        print('"other" =', other)
        return other
                
    def mattranspose(self):
        'self.mattranspose --> returns transpose (self unchanged).'
        m = self.m
        n = self.n
        newmat = Matrix(n, m)
        for i in range(m):
            for j in range(n):
                newmat[j][i] = self[i][j]
        return newmat
    
#  --------------------------------------------
# Solution of equations and inverse
    def solve_obsolete(self, rhs):
        '''This is an obsolete method that may be useful
        for debugging; then to be removed.'''
        amat = self
        m = amat.m
        n = rhs.n
        aug = Matrix(m, m+n) # augmented mat
        for i in range(m):
            for j in range(m):
                aug[i][j] = amat[i][j]
        for i in range(m):
            for j in range((m+n)):
                aug[i][j] = rhs[i][j-m]            
# The naive method - no pivoting, simplest code, solves SOME equations
        for ii in range(m):
            pivot = aug[ii][ii]
            for jj in range(m+n):
                aug[ii][jj] = aug[ii][jj] / pivot
            for i in range(m):
                factor = aug[i][ii]
                for j in range(m+n):
                    if ii != i:
                        aug[i][j] = aug[i][j] - factor * aug[ii][j]
        for i in range(m):
            rhs[i] = aug[i][m:]
        return rhs
        
    def solve(self, other):
        'other is rhs and is returned as solution. Partial pivoting.'
        assert self.m == self.n, 'self must be a square matrix'
        assert self.n == other.m, 'self.n must be equal to other m'
        m = self.m
        n = other.n
        for i in range(m):
            for j in range(m):
                self[i][j] = float(self[i][j])
        aug = Matrix(m, m+n) # augmented mat
        done = []
        for i in range(m):
            for j in range(m):
                aug[i][j] = self[i][j]
        for i in range(m):
            for j in range(m, (m+n)):
                aug[i][j] = other[i][j-m]  
# Partial Pivoting - somewhat better solver
        for ii in range(m):
            pivcol = []
            rowindeces = []
            for k in range(m):
                if not k in done:
                    pivcol.append(aug[k][ii])
                    rowindeces.append(k) 
            pivot, index = find_max(pivcol)
            cii = rowindeces[index]
            done.append(cii)            
            for jj in range(m+n):
                aug[cii][jj] = aug[cii][jj] / pivot
            for i in range(m):
                factor = aug[i][ii]
                for j in range(m+n):
                    if i != cii:
                        aug[i][j] = aug[i][j] - factor * aug[cii][j]
        for i in range(m):
            other[i] = aug[done[i]][m:]
        return other

    def matinvert(self):
        '''amat.matinvert() --> inverse of amat.
'''       
        other = self.matcopy()
        other.matunit()        
        return self.solve(other)

    def matequal(self, other):
        'Matrices are equal, return True or False.'
        if self.m != other.m or self.n != other.n:
            return False
        else:
            for i in range(self.m):
                for j in range(self.n):
                    try:
                        assert self[i][j] == other[i][j]
                    except AssertionError: 
                        return False
            return True

    def neatprint(self, prnt=printline, LineLen=5):        
        '''prinline = the line printing function.
    Neatly prints matrix self of size (m x n).
    Line length variable, default is 5. '''
        m, n = self.m, self.n
        tmp = 'A matrix of dimensions (m x n), where m, n, LineLen =  %i %i %i ' % (m, n, LineLen)
        prnt(tmp + '\n')
        for i in range(m):
            line = ''
            for j in range(n):
                line += ' %12.5E ' % (self[i][j])
                if ( (j+1) % LineLen) == 0 or ((j + 1) == n): 
                    prnt(line + '\n')
                    if j < (n - 1):
                        line = ''
                if (j==(n - 1)) and ((j + 1) > LineLen) : 
                    prnt(' \n')

# -------------------------------- class end ---------------
# global (utility) functions.
##autoprint = True

def mkzeromat(m, n, autoprint=False):
    'm, n --> make (mxn) zero matrix and print by default.'
    mat = Matrix(m, n)
    if autoprint:
        print('Echo check of mkzeromat:')
        mat.matprint()
    return mat

def mkunitmat(m, autoprint=True):
    'm --> make (mxm) unit matrix and print by default.'
    mat = Matrix(m, m)
    mat.matunit()
    if autoprint:
        mat.matprint()        
    return mat
    
def enterdata(m, n, datalist, autoprint=True):
    '''datalist --> create store matrix and enter data into store.'''
    assert m == len(datalist),\
            'Data list does not match matrix space.'
    mat = mkzeromat(m, n)
    for i in range(m):
        assert n == len(datalist[i])
        mat[i] = datalist[i]
    if autoprint:
        print('Echo check of enterdata', mat)
    return mat  

def printmat(message, mat):
    '''Convenience method. Non-essential.
    '''
    print(message)
    print(mat)
            
if __name__ == '__main__':

    import doctest
    doctest.testmod()
    amat = Matrix(3, 3)
    amat.matprint()
    amat.neatprint()

    
