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

import operator

from pytilities import mangle
from pytilities.types import NumberType
from pytilities.overloading import overloaded, Overload, Param
from pytilities.descriptors import AttributeDescriptor, DereferencedDescriptor
from pytilities.aop import AOPMeta

class _VectorBase(object, metaclass=AOPMeta):

    '''
    Note to inheritors: you should provide an _x property on your class
    '''

    def __init_xy(self, x, y):
        # set up our properties
        self.__x_property = _VectorBase._x # avoiding lookup
        self.__y_property = _VectorBase._y

        # set initial values
        self._x = x
        self._y = y

    def __init_bound_properties(self, x_property, y_property):
        self.__x_property = x_property
        self.__y_property = y_property

    @overloaded((
        Overload(__init_xy,
            Param("x", NumberType, default=0),
            Param("y", NumberType, default=0)),
        Overload(__init_bound_properties,
            Param("x_property"),
            Param("y_property"))))
    def __init__(self):
        """
        Constructs a 2D Vector

        Overloaded, parameters:

        :a:
            x :: float | int = 0
            y :: float | int = 0

        :b:
            x :: bound descriptor
                bound property that is used to store the x value in

            y :: bound descriptor
                bound property that is used to store the y value in
        """
        pass

    @property
    def _x(self):
        '''Read-write, x position'''
        return self.__x

    @_x.setter
    def _x(self, value):
        self.__x = value

    @property
    def _y(self):
        '''Read-write, y position'''
        return self.__y

    @_y.setter
    def _y(self, value):
        self.__y = value

    def move_to(self, x, y):
        """
        Set x, y coords

        Parameters:

            `x` :: float | int
                x position

            `y` :: float | int
                y position
        """
        self.x, self.y = x, y

    def move_by(self, x, y):
        """
        Move vector by (x, y)

        Parameters:

            `x` :: float | int
                x position

            `y` :: float | int
                y position
        """
        self.x += x
        self.y += y

    def __assign_xy(self, x, y):
        """
        Assigns the values to this vector

        :param x: x coordinate
        :type x: number
        :param y: y coordinate
        :type y: number
        """
        self.x = x
        self.y = y

    def __assign_v(self, v):
        """
        Assigns the values of another vector to this vector

        :param x: x coordinate
        :type x: number
        :param y: y coordinate
        :type y: number
        """
        self.x = v.x
        self.y = v.y

    @overloaded((
        Overload(__assign_v, Param('v')),
        Overload(__assign_xy, Param('x'), Param('y'))))
    def assign(self):
        '''
        Change the xy values

        Overloads:
            - `__assign_xy`
            - `__assign_v`
        '''

    def __str__( self ):
        return "<%s (%s,%s)>" % (self.__class__.__name__,
                                 self.x, self.y)

    def __copy__(self):
        return self.__class__(self.x, self.y)

    def copy(self):
        """Returns shallow copy :: Vector"""
        return self.__copy__()

    def __eq__(self, other):
        """other :: Vector"""
        return self.x == other.x and \
               self.y == other.y

    def __ne__(self, other):
        """other :: Vector"""
        return not self.__eq__(other)

    def __len__(self):
        return 2

    def __getitem__(self, key):
        return (self.x, self.y)[key]

    def __setitem__(self, key, value):
        (self.x, self.y)[key] = value

    def __iter__(self):
        """Iterates over its x and y value"""
        return iter((self.x, self.y))

    def __getattr__(self, name):
        try:
            return tuple([(self.x, self.y)['xy'.index(c)] \
                          for c in name])
        except ValueError:
            raise AttributeError(name)

    def __add__(self, other):
        """other :: Vector"""
        v = self._get_vector_operator(other)
        v.assign(self)
        v += other
        return v

    def __iadd__(self, other):
        """other :: Vector"""
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        return self + (-other)

    def __isub__(self, other):
        """other :: Vector"""
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, other):
        """other :: number"""
        v = self.copy()
        v *= other
        return v

    def __rmul__(self, other):
        """other :: number"""
        return self * other

    def __imul__(self, other):
        """other :: number"""
        self.x *= other
        self.y *= other
        return self

    def __floordiv__(self, other):
        """other :: number"""
        return self.__class__(self.x // other, self.y // other)

    def __ifloordiv__(self, other):
        """other :: number"""
        self.x //= other
        self.y //= other
        return self

    def __rfloordiv__(self, other):
        """other :: number"""
        return self.__class__(other // self.x, other // self.y)

    def __neg__(self):
        return self.__class__(-self.x, -self.y)

    def __pos__(self):
        return self.copy()
    
    def __hash__(self):
        return id(self)

_VectorBase.x = DereferencedDescriptor(
    AttributeDescriptor(mangle(_VectorBase, '__x_property')))
_VectorBase.y = DereferencedDescriptor(
    AttributeDescriptor(mangle(_VectorBase, '__y_property')))

#_get_vector_operator is imported from __init__ (yeah, it's kind of ugly

