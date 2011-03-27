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

from pytilities.overloading import \
    overloaded, Overload, Param, CompositeParam
from pytilities.types import NumberType
from pytilities.aop import AOPMeta

class _RectangleBase(object, metaclass=AOPMeta):

    def __copy__(self):
        return self.__class__(*(self.bounds))

    copy = __copy__

    @property
    def bounds(self):
        """Read-write, all rectangle coordinates
        
        Returns (left, top, right, bottom)

        Overloaded, set parameters:

        :a:
            `left` :: float | int
            `top` :: float | int
            `right` :: float | int
            `bottom` :: float | int

        :b:
            `top_left` :: Vector
            `bottom_right` :: Vector
        """
        return (self.left, self.top, self.right, self.bottom)

    def __set_bounds_numbers(self, left, top, right, bottom):
        (self.left, self.top, self.right, self.bottom) = \
            (left, top, right, bottom)

        assert self.left < self.right, \
            "given top_left isn't the top left corner"
        assert self.top < self.bottom, \
            "given top_left isn't the top left corner"

    def __set_bounds_points(self, top_left, bottom_right):
        self.__set_bounds_numbers(*(top_left.xy + bottom_right.xy))

    @bounds.setter
    @overloaded((
        Overload(__set_bounds_numbers,
            CompositeParam("args", (
                Param("left", NumberType),
                Param("top", NumberType),
                Param("right", NumberType),
                Param("bottom", NumberType)))),
        Overload(__set_bounds_points,
            CompositeParam("args", (
                Param("top_left"),
                Param("bottom_right"))))))
    def bounds(self):
        pass

    @property
    def center(self):
        """
        Read-write, center of the rectangle :: bound Vector

        Changing the center does not change the size.
        """
        return self._center

    @center.setter
    def center(self, v):
        self._center.assign(v)

    @property
    def size(self):
        """Read-write, size of the rectangle :: bound Vector"""
        return self._size

    @size.setter
    def size(self, value):
        self._size.assign(value)
        
    @property
    def left(self):
        """Read-write, left edge of rectangle"""
        return self._left

    @left.setter
    def left(self, value):
        self._left = value
        
    @property
    def top(self):
        """Read-write, top edge of rectangle"""
        return self._top

    @top.setter
    def top(self, value):
        self._top = value
        
    @property
    def right(self):
        """Read-write, right edge of rectangle"""
        return self._right

    @right.setter
    def right(self, value):
        self._right = value
        
    @property
    def bottom(self):
        """Read-write, bottom edge of rectangle"""
        return self._bottom

    @bottom.setter
    def bottom(self, value):
        self._bottom = value
        
    @property
    def top_left(self):
        """Read-write, top-left corner :: bound Vector"""
        return self._top_left

    @top_left.setter
    def top_left(self, value):
        return self._top_left.assign(value)

    @property
    def top_right(self):
        """Read-write, top-right corner :: bound Vector"""
        return self._top_right

    @top_right.setter
    def top_right(self, value):
        return self._top_right.assign(value)

    @property
    def top_left(self):
        """Read-write, top-left corner :: bound Vector"""
        return self._top_left

    @top_left.setter
    def top_left(self, value):
        return self._top_left.assign(value)

    @property
    def top_right(self):
        """Read-write, top-right corner :: bound Vector"""
        return self._top_right

    @top_right.setter
    def top_right(self, value):
        return self._top_right.assign(value)

    @property
    def bottom_left(self):
        """Read-write, bottom-left corner :: bound Vector"""
        return self._bottom_left

    @bottom_left.setter
    def bottom_left(self, value):
        return self._bottom_left.assign(value)

    @property
    def bottom_right(self):
        """Read-write, bottom-right corner :: bound Vector"""
        return self._bottom_right

    @bottom_right.setter
    def bottom_right(self, value):
        return self._bottom_right.assign(value)

    def contains(self, v):
        """
        Returns `True` if `v` is inside the rectangle.
        
        Parameters:

            `v` :: Vector
        """
        x,y = v.xy
        return (self.left <= x <= self.right and
                self.top <= y <= self.bottom)

    def overlaps(self, rect):
        """
        Returns `True` if `rect` overlaps with this rectangle.

        Parameters:

            `rect` :: Rectangle
        """
        return (self.right > rect.left and self.left < rect.right and
                self.top < rect.bottom and self.bottom > rect.top)

    def __inflate_number(self, n):
        self.left -= n
        self.top -= n
        self.right += n
        self.bottom += n

    def __inflate_vector(self, v):
        x, y = v.xy
        self.left -= x
        self.top -= y
        self.right += x
        self.bottom += y

    @overloaded((
        Overload(__inflate_number,
                Param("n", NumberType)),
        Overload(__inflate_vector,
                Param("v"))))
    def inflate(self):
        """
        Inflate the rectangle

        Overloaded, parameters:

        :a:
            n :: number
                Extend all sides by n points
        :b:
            v :: Vector
                extend left and right sides by v.x and top and bottom sides by
                v.y
        """

    def move_to(self, v):
        """
        Move the top_left corner to `v`, without changing size

        Parameters:

            `v` :: Vector
                the spot to move to
        """
        bottom_right = self.bottom_right + v - self.top_left
        (self.left, self.top) = v.xy
        (self.right, self.bottom) = bottom_right.xy

    def move_by(self, v):
        """
        Move the top_left corner by `v`, without changing size

        Parameters:

            `v` :: Vector
                the amount to move by
        """
        self.left += v.x
        self.right += v.x
        self.top += v.y
        self.bottom += v.y

    def __str__( self ):
        return "<%s (%s,%s)-(%s,%s)>" % (self.__class__.__name__,
                                         self.left, self.top,
                                           self.right, self.bottom)

    def __repr__(self):
        return "%s(%s, %s, %s, %s)" % (self.__class__.__name__,
                                 self.left, self.top,
                                   self.right, self.bottom)

