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

from pytilities.infinity import infinity

from ._vectorbase import _VectorBase

class DiscreteVector(_VectorBase):

    """
    2D Point/Vector with coordinates in a discrete space (integer).

    Note on Vector, DiscreteVector operations: Vector op DiscreteVector returns
    Vector. DiscreteVector op DiscreteVector returns DiscreteVector.

    Note that a DiscreteVector does not support truediv (/), it does support
    floordiv(//) however.
    """

    def __init__(self, *args, **kwargs):
        _VectorBase.__init__(self, *args, **kwargs)

from .immutablevector import immutable_vector_aspect

DiscreteVector.INFINITY = DiscreteVector(infinity, infinity)
'''immutable DiscreteVector of infinite size'''
immutable_vector_aspect.apply(DiscreteVector.INFINITY)
DiscreteVector.NULL = DiscreteVector(0, 0) # saves some vector spawning
'''immutable DiscreteVector (0, 0)'''
immutable_vector_aspect.apply(DiscreteVector.NULL)

