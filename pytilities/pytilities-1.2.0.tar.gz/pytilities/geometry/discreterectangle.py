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
from .discretevector import DiscreteVector

class DiscreteRectangle(_RectangleBase):

    '''
    A rectangle with discrete coordinates.

    This rectangle greatly resembles `Rectangle`, but works with a discrete
    coordinate space. All results are floored.
    '''

    def __init__(self, *args):
        """
        Construct a dicrete rectangle.
        
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

        self._size = DiscreteVector(
            BoundDescriptor(DiscreteRectangle.width, self), 
            BoundDescriptor(DiscreteRectangle.height, self))

        self._center = DiscreteVector(
            BoundDescriptor(DiscreteRectangle._center_x, self), 
            BoundDescriptor(DiscreteRectangle._center_y, self))

        self._top_left = DiscreteVector(
            BoundDescriptor(_RectangleBase.left, self), 
            BoundDescriptor(_RectangleBase.top, self))
        
        self._top_right = DiscreteVector(
            BoundDescriptor(_RectangleBase.right, self), 
            BoundDescriptor(_RectangleBase.top, self))

        self._bottom_left = DiscreteVector(
            BoundDescriptor(_RectangleBase.left, self), 
            BoundDescriptor(_RectangleBase.bottom, self))

        self._bottom_right = DiscreteVector(
            BoundDescriptor(_RectangleBase.right, self), 
            BoundDescriptor(_RectangleBase.bottom, self))

    @property
    def width(self):
        """Read-write, width of the rectangle"""
        return self.right - self.left + 1

    @width.setter
    def width(self, value):
        self.right = self.left + value - 1
        
    @property
    def height(self):
        """Read-write, height of the rectangle"""
        return self.bottom - self.top + 1

    @height.setter
    def height(self, value):
        self.bottom = self.top + value - 1

    @property
    def _center_x(self):
        return (self.left + self.right) // 2

    @_center_x.setter
    def _center_x(self, value):
        cx = self.size.x - 1
        self.left = value - cx//2
        self.right = self.left + cx  # this way we maintain our size

    @property
    def _center_y(self):
        return (self.top + self.bottom) // 2

    @_center_y.setter
    def _center_y(self, value):
        cy = self.size.y - 1
        self.top = value - cy//2
        self.bottom = self.top + cy  # this way we maintain our size

