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
Various types

Classes:

- `NumericType`: Represents any numeric type.
- `NumberType`: Represents any number type.
- `SequenceType`: Represents any ordered sequence.
- all types from the standard types package
"""

from types import *

# custom types
from ._numerictypemeta import _NumericTypeMeta
from ._numbertypemeta import _NumberTypeMeta
from ._sequencetypemeta import _SequenceTypeMeta
from .numerictype import NumericType
from .numbertype import NumberType
from .sequencetype import SequenceType

__docformat__ = 'reStructuredText'

