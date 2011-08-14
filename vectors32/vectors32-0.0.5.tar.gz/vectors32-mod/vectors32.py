#!/usr/bin/env python3
'''
vectors32.py - module for Vector class, basic operation of 
vector algebra. Python 3.2
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
# paper mail PO Box 279 Jamison Centre ACT 2614 Australia.

__version__ = '0.0.5'

import math

class Vector():
    __slots__ = ('x', 'y', 'z')
    
    def __init__(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __eq__(self, other):
        'Verify that two vectors are equal.'
        if type(self) is Vector and type(other) is Vector:
            return self.x == other.x and self.y == other.y and \
        self.z == other.z
        else:
            return NotImplemented
            
    def __str__(self):
        'Vector string for printing.'
        if type(self) is Vector:
            return 'Vector({}, {}, {})'.format(self.x, self.y, self.z)
        else:
            return NotImplemented
        
    def __repr__(self):
        if type(self) is Vector:
            return 'Vector({}, {}, {})'.format(self.x, self.y, self.z)
        else:
            return NotImplemented
        
    def __add__(self, other):
        'Vector addition.'
        if type(self) is Vector and type(other) is Vector:
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return NotImplemented


    def __sub__(self, other):
        'Vector subtraction.'
        if type(self) is Vector and type(other) is Vector:
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            return NotImplemented

    def __mul__(self, other):
        '''Scalar ("dot") product  [ * ].
        self [.] other when other is Vector,
        self * other when other is number,
        i.e. other==Vector --> x product self x other
        other==scalar --> multiply vector by scalar.
        This method is invoked by * symbol!
        '''
        if (type(self) is Vector) and (type(other) is Vector):
##          Scalar product of two vectors --> scalar
            return self.x * other.x + self.y * other.y\
                 + self.z * other.z
        elif (type(self) is Vector) and (type(other) in (float, int)):
##          Multiplication of vector by scalar --> vector
            return Vector(self.x * other, self.y * other, self.z * other)        
        else:
            return NotImplemented
        
    def __rmul__(self, other):
        "number * vector --> vector"
        if (type(other) in (float, int)) and type(self) is Vector:
            return Vector(self.x * other, self.y * other, self.z * other)
        else:
            return NotImplemented

    def __pow__(self, other):
        '''
        [ ** ] Vector product self x other.
        '''
        if (type(self) is Vector) and (type(other) is Vector):        
            return Vector(self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)
        else:
            return NotImplemented

    @property
    def size(self):
        '''Determine the magnitude ('size') of the vector
        and return it to the caller.
        '''
        return math.hypot(math.hypot(self.x, self.y), self.z)

    @property
    def normalize(self):
        '''
        Reduce vector size to 1.0 and return it to the caller.
        '''
        d = self.size
        return Vector(self.x / d,
                      self.y / d,
                      self.z / d)

if __name__ == '__main__':
    vxx = Vector(1, 2, 3)
    print(vxx)
    print('Tried to run as main.')
    
