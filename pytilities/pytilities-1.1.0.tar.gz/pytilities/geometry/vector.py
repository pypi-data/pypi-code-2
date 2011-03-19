# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

__docformat__ = 'reStructuredText'

import math
from pytilities.infinity import infinity

from ._vectorbase import _VectorBase

# Note: since py3, this class is now meant for continuous values only, the
# types of x and y no longer matter (which I find much more intuitive)
# (In previous versions the x and y types would have made it behave as either a
# more discrete one, or a countinuous one)
class Vector(_VectorBase):

    """
    2D Point/Vector with coordinates in a continuous space (float).

    Note on Vector, DiscreteVector operations: Vector op DiscreteVector returns
    Vector. DiscreteVector op DiscreteVector returns DiscreteVector.
    """

    def __init__(self, *args, **kwargs):
        _VectorBase.__init__(self, *args, **kwargs)

    def __abs__(self):
        return abs(self)

    @property
    def length(self):
        """
        Read-write, length of vector

        Returns :: float | int

        Set parameters:

            value :: number
                new length
        """
        return math.sqrt(self.x ** 2 + \
                         self.y ** 2)

    @length.setter
    def length(self, value):
        d = self.length * value
        self *= value

    @property
    def length_squared(self):
        """Read-only, length squared :: float | int"""
        return self.x ** 2 + \
               self.y ** 2

    def normalize(self):
        """
        Normalize vector
        
        Returns :: Vector
        """
        d = self.length

        if d:
            self /= d

        return self

    def normalized(self):
        """
        Get a normalized copy of this vector

        Returns :: Vector
        """
        v = self.copy()
        return v.normalize()

    def dot(self, other):
        """
        Get the dot product of this vector with `other`

        Parameters:

            `other` :: Vector
                the other vector

        Returns :: float | int
        """
        return self.x * other.x + \
               self.y * other.y

    def cross(self):
        return Vector(self.y, -self.x)

    def reflect(self, normal):
        # assume normal is normalized
        d = 2 * (self.x * normal.x + self.y * normal.y)
        return Vector(self.x - d * normal.x,
                       self.y - d * normal.y)

    def __truediv__(self, other):
        """other :: number"""
        return self.__class__(self.x / other, self.y / other)

    def __itruediv__(self, other):
        """other :: number"""
        self.x /= other
        self.y /= other
        return self

    def __rtruediv__(self, other):
        """other :: number"""
        return self.__class__(other / self.x, other / self.y)

from .immutablevector import immutable_vector_aspect

Vector.INFINITY = Vector(infinity, infinity)
'''immutable Vector of infinite size'''
immutable_vector_aspect.apply(Vector.INFINITY)
Vector.NULL = Vector(0, 0) # saves some vector spawning
'''immutable Vector (0, 0)'''
immutable_vector_aspect.apply(Vector.NULL)

