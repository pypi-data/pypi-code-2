#!/usr/bin/env python3
# wrapnumpy3.py - module for Matrix class.

# Copyright (c) 2011 Algis Kabaila. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided and is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public Licence for more details.

__version__ = '0.0.3'

import numpy as np
from numpy import linalg as la

# Matrix class with its methods.---------------------


def printline(line):
    'Function to simmulate appending to a plainText widget.'
    print(line, end=' ')

class Matrix(list):
    def __init__(self, m=1, n=1):
        '''Create zero matrix of 
        m = no of rows, n = no of columns.'''
        self.m = m
        self.n = n  
        row = []
        for j in range(n):
            row.append(0.0)
        for i in range(m):
            self.append(row[:])
    
    def __getitem__(self, key):
        'get value of an indexed item.'
        if type(key) is int:
            return super().__getitem__(key)
        else:    
            if type(key) is tuple:
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
                    print('key is not int not or llen(tuple)>4-fail')
                    raise NotImplementedError()

    def __setitem__(self, key, value):
        'Set index value.'
        if type(key) is int:
            super().__setitem__(key, value)
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
        'Matrix string format for print function.'
        if type(self) != Matrix:
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
        'Matrix equality'
        if type(self) is Matrix and type(other) is Matrix:
            return self.matequal(other)
        else:
            return NotImplemented
       
    def __add__(self, other):
        'Matrix addition.'
        if (type(self) is Matrix) and (type(other) is Matrix):
            return self.matadd(other)
        else:
            return NotImplemented

    def __sub__(self, other):
        'Matrix subtraction.'
        if (type(self) is Matrix) and (type(other) is Matrix):
            return self.matsub(other)
        else:
            return NotImplemented
        
    def __mul__(self, other):
        '''Matrix multiplication: [ * ] when both self and other
        are matrices. When one is a scalar and the other is a
        matrix, scalar multiplicatin of a matrix. '''
        if (type(self) is Matrix) and (type(other) is Matrix):
            assert self.n == other.m, 'Not compatible for multiplication'
            return self.matmult(other)
        elif (type(self) is Matrix) and (type(other) in (float, int)):
            self.scalarmult(other)
            return self
        elif (type(self) in (float, int)) and type(other) is Matrix:
            return NotImplemented
        else:
            return NotImplemented
        
    def __rmul__(self, other):
        "number * matrix --> matrix"
        if (type(other) in (float, int)) and type(self) is (Matrix):
            self.scalarmult(other)
            return self

    def __invert__(self):
        '''
        [ ~ ] Matrix inversion).
        '''
        if type(self) is Matrix:
            return self.matinvert()
        else:
            return NotImplemented

    def __pow__(self, other):
        '''
        [ ** ] Equation solver x = self * rhs ).
        '''
        if type(self) is Matrix and type(other) is Matrix:
            return self.solve(other)
        else:
            return NotImplemented
                  
    def matmult(self, other):
        "self.matmult(other) --> matrix product self x other."
        assert self.n == other.m, 'incompatible for mat mult.'
        result = Matrix(self.m, other.n)
#        result = np.dot(self, other)
        tmp = np.dot(self, other)
        for i in range(self.m):
            result[i] = tmp[i]
        return result
        
    def matadd(self, other):
        'return (mat add) = self + other'
        assert self.m == other.m, 'must be same size'
        assert self.n == other.n, 'must be same size'
        result = Matrix(self.m, self.n)
#        result = np.add(self, other)
        tmp = np.add(self, other)
        for i in range(self.m):
            result[i] = tmp[i]
        return result
        
    def matsub(self, other):
        'return (mat Subtract) = self - other.'
        assert self.m == other.m, 'must be same size'
        assert self.n == other.n, 'must be same size'
        result = Matrix(self.m, self.n)
#        result = np.add(self, np.negative(other))
        tmp = np.add(self, np.negative(other))
        for i in range(self.m):
            result[i] = tmp[i]
        return result
        
    def scalarmult(self, factor):
        '''Multiply matrix by scalar (in place).'''
        for i in range(self.m):
            for j in range(self.n):
                self[i][j] = factor * self[i][j]
                
    def matcopy(self):
        'Creates and returns a copy of the matrix.'
        other = Matrix(self.m, self.n)
        for i in range(self.m):
            other[i] = self[i][:]
        return other
        
               
    def matunit(self):
        'Make self the unit matrix (in place).'
        m = self.m
        n = self.n
        assert m == n, 'Unary matrix must be square.'
        for i in range(m):
            for j in range(n):
                self[i][j] = 0.0
                if i == j:
                    self[i][j] = 1.0

# Wrapping of mattranspose from numpy is suspicious and suspended.
# This is it.
#    def mattranspose(self):
#        'self.mattranspose --> returns transpose (self unchanged).'
#        m = self.m
#        n = self.n
#        newmat = Matrix(n, m)
#        tmp = np.transpose(self)
#        for i in range(self.m):
#            newmat[i] = tmp[i]
#        return newmat

# Original mattranspose from Matalg
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
        
    def solve(self, other):
        'other is rhs and is returned as solution. Partial pivoting.'
        assert self.m == self.n, 'self must be a square matrix'
        assert self.n == other.m, 'self.n must be equal to other m'
        tmp = la.solve(self, other)
        result = Matrix(other.m, other.n)
        for i in range(self.m):
            result[i] =tmp[i]
        return result
    
    def matinvert(self):
        '''amat.matinvert() --> inverse of amat.'''       
        other = Matrix(self.m, self.n)
        tmp = la.inv(self)
        for i in range(self.m):
            other[i] = tmp[i]
        return other
    
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
    Neatly prints matrix self of size (m x n).'''
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

class Utilities():
    
    def enterdata(self, m, n, datalist, autoprint=True):
        '''datalist --> create store matrix and enter data into store.'''
        assert m == len(datalist),\
                'Data list does not match matrix space.'
        mat = Matrix(m, n)
        for i in range(m):
            assert n == len(datalist[i])
            mat[i] = datalist[i]
        if autoprint:
            print('Echo check of enterdata')
            mat.neatprint()
        return mat  

    def printline(self, line):
        'Function to simmulate appending to a plainText widget.'
        print(line, end=' ')


if __name__ == '__main__':
    print('testing...')
    utils = Utilities()
    utils.printline('Start of testing\n') 
    tmp = Matrix(2, 2)
    tmp[0, 0] = 12.3
    tmp[1, 1] = 45.6
    print('tmp = ', tmp)
    print('tmp[1, 1] = ', tmp[1, 1])

    mat = utils.enterdata(2, 2, [ [-0.5714285714285714, 0.7142857142857142],\
                    [0.42857142857142855, -0.2857142857142857] ])
    print('reprint data in rough format = \n', mat)
    print('----------------------------------------')    

    print('Try solution of equations') 
    amat = utils.enterdata(3, 3,\
            [ [25.0, 5.0, 1.0],\
            [64.0, 8.0, 1.0],\
            [144.0, 12.0, 1.0] ])

    rhs = utils.enterdata(3, 1,\
            [[106.8], [177.2], [279.2]])
    result = la.solve(amat, rhs)
    print('result of solution directly by numpy = \n', result)
    result = amat.solve(rhs)
    print('result by calling Matrix.solve(rhs) of the module = ')
    result.neatprint()
    print('----------------------------------------')
    print('Matrix inverse. amat = ')
    amat.neatprint()
    print('Inverse of amat = ')
    result = amat.matinvert()
    result.neatprint()
    print('''Repeated solution of preceeding equations by
    multiplication of inverse with the rhs = ''')
    x = result.matmult(rhs)
    x.neatprint()
    print('----------------------------------------')
    print('\nAnother example of solution of equations:')
    cmat = utils.enterdata(3, 3, \
            [ [5, 6, 7],\
            [10, 12, 3],\
            [20, 17, 19] ])
            
    rhs = utils.enterdata(3, 1, \
                   [ [18],\
                     [25],\
                     [56]])
    
    x = cmat.solve(rhs)
    x.neatprint()
    print('----------------------------------------')
    print('Matrix addition and subtraction.')
    amat = utils.enterdata(2, 3,\
            [ [3, 5, 1,], \
              [ 3, 6, 7]])
              
    bmat = utils.enterdata(2, 3, \
            [ [3, 6, 7], \
              [4, 5, 4]])                           
    rmat = amat.matadd(bmat)
    print('amat + bmat =')    
    rmat.neatprint()
    print('rmat - amat = bmat =')
    x = rmat.matsub(amat)
    x.neatprint()
    print('----------------------------------------')
    print('Transpose of matrix amat.\n amat =')
    amat.neatprint()
    dmat = amat.mattranspose()
    print('Transpose of amat =')
    dmat.neatprint()
    print('----------------------------------------')
    print('Matrix multiplication.\n amat =')
    amat.neatprint()
    print(' bmat =')
    bmat = bmat.mattranspose()
    bmat.neatprint()
    result = amat.matmult(bmat)
    print('amat x bmat =')
    result.neatprint()
    print('----------------------------------------')  
    print('Create a 4x4 unit matrix, onemat.')  
    onemat = Matrix(4, 4)
    onemat.matunit()
    onemat.neatprint()
    print('----------------------------------------') 
    print('Create another unit matrix, twomat and verify equality.')
    twomat = Matrix(4, 4)
    twomat.matunit()
    twomat.neatprint()
    if twomat.matequal(onemat):
        print('twomat is term by term equal to onemat.')
    print('==================================================')
    print('Matrix algebra using usual scalar algebra symbols.')
    print('For instance, "*" to multiply, "+" to add etc.')
    print('==================================================')    
    print('Try solution of equations') 
    amat = utils.enterdata(3, 3,\
            [ [25.0, 5.0, 1.0],\
            [64.0, 8.0, 1.0],\
            [144.0, 12.0, 1.0] ])

    rhs = utils.enterdata(3, 1,\
            [[106.8], [177.2], [279.2]])
    x = amat ** rhs
    print('solution x =')
    x.neatprint()
    print('----------------------------------------')
    print('Matrix inverse. amat = ')
    amat.neatprint()
    print('Inverse of amat = ')
    result = ~amat
    result.neatprint()
    print('''Repeated solution of preceeding equations by
    multiplication of inverse with the rhs = ''')
    x = result * rhs
    x.neatprint()
    print('----------------------------------------')
    print('\nAnother example of solution of equations:')
    cmat = utils.enterdata(3, 3, \
            [ [5, 6, 7],\
            [10, 12, 3],\
            [20, 17, 19] ])
            
    rhs = utils.enterdata(3, 1, \
                   [ [18],\
                     [25],\
                     [56]])
    
    x = cmat ** rhs
    x.neatprint()
    print('----------------------------------------')
    print('Matrix addition and subtraction.')
    amat = utils.enterdata(2, 3,\
            [ [3, 5, 1,], \
              [ 3, 6, 7]])
              
    bmat = utils.enterdata(2, 3, \
            [ [3, 6, 7], \
              [4, 5, 4]])                           
    rmat = amat + bmat
    print('amat + bmat =')    
    rmat.neatprint()
    print('rmat - amat = bmat =')
    x = rmat - amat
    x.neatprint()
    print('----------------------------------------')    
    print('Matrix multiplication.\n amat =')
    amat.neatprint()
    print(' bmat =')
    bmat = bmat.mattranspose()
    bmat.neatprint()
    result = amat * bmat
    print('amat x bmat =')
    result.neatprint()
    print('----------------------------------------')  
    print('Create a 4x4 unit matrix, onemat.')  
    onemat = Matrix(4, 4)
    onemat.matunit()
    onemat.neatprint()
    print('----------------------------------------') 
    print('Create another unit matrix, twomat and verify equality.')
    twomat = Matrix(4, 4)
    twomat.matunit()
    twomat.neatprint()
    if twomat == onemat:
        print('twomat is term by term equal to onemat.')
    print('----------------------------------------')   
