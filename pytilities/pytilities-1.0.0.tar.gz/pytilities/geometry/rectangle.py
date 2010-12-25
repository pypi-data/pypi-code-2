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

from pytilities.descriptors import BoundDescriptor

from ._rectanglebase import _RectangleBase
from .vector import Vector

class Rectangle(_RectangleBase):

    def __init__(self, *args):
        """
        Construct a rectangle.
        
        Overloaded, parameters:

        :a:
            `left` :: float | int
            `top` :: float | int
            `right` :: float | int
            `bottom` :: float | int

        :b:
            `top_left` :: Vector
            `bottom_right` :: Vector
        """
        _RectangleBase.__init__(self)

        self.bounds = args

        self._size = Vector(
            BoundDescriptor(Rectangle.width, self), 
            BoundDescriptor(Rectangle.height, self))

        self._center = Vector(
            BoundDescriptor(Rectangle._center_x, self), 
            BoundDescriptor(Rectangle._center_y, self))

        self._top_left = Vector(
            BoundDescriptor(_RectangleBase.left, self), 
            BoundDescriptor(_RectangleBase.top, self))
        
        self._top_right = Vector(
            BoundDescriptor(_RectangleBase.right, self), 
            BoundDescriptor(_RectangleBase.top, self))

        self._bottom_left = Vector(
            BoundDescriptor(_RectangleBase.left, self), 
            BoundDescriptor(_RectangleBase.bottom, self))

        self._bottom_right = Vector(
            BoundDescriptor(_RectangleBase.right, self), 
            BoundDescriptor(_RectangleBase.bottom, self))

    @property
    def width(self):
        """Read-write, width of the rectangle"""
        return self.right - self.left

    @width.setter
    def width(self, value):
        self.right = self.left + value
        
    @property
    def height(self):
        """Read-write, height of the rectangle"""
        return self.bottom - self.top

    @height.setter
    def height(self, value):
        self.bottom = self.top + value

    @property
    def _center_x(self):
        return (self.left + self.right) / 2

    @_center_x.setter
    def _center_x(self, value):
        cx = self.size.x
        self.left = value - cx/2
        self.right = self.left + cx  # this way we maintain our size

    @property
    def _center_y(self):
        return (self.top + self.bottom) / 2

    @_center_y.setter
    def _center_y(self, value):
        cy = self.size.y
        self.top = value - cy/2
        self.bottom = self.top + cy  # this way we maintain our size
