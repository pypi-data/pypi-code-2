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

"""
All sorts of geometry trinkets
"""

__docformat__ = 'reStructuredText'

from .vector import Vector
from .immutablevector import ImmutableVector, immutable_vector_aspect
from .discretevector import DiscreteVector
from .verbosevectoraspect import verbose_vector_aspect

from .rectangle import Rectangle
from .immutablerectangle import ImmutableRectangle, immutable_rectangle_aspect
from .discreterectangle import DiscreteRectangle
from .verboserectangleaspect import verbose_rectangle_aspect

# bit of nasty ugly code follows (huge coupling, but meh, it's contained to a
# small part)
from ._vectorbase import _VectorBase
from .functions import _get_vector_operator
_VectorBase._get_vector_operator = _get_vector_operator
del _get_vector_operator
del _VectorBase

