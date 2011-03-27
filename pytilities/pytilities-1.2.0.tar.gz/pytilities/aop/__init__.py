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

'''
An aspect oriented utility library

In contrast to most libraries, this library supports giving advice to
properties (decorators in general) as well.

Features:

- Giving advice to:

  - type of object:

    - all instances of a class
    - some instances
  - kind of member:

    - any descriptor (function, property, classmethod, ...)
    - a non-existent attribute

Restrictions:

- Cannot give advice to built-in/extension types, e.g. property

See the online user guide for more information.
'''

__docformat__ = 'reStructuredText'

from .aopexception import AOPException
from .advisor import advisor
from .commands import (
    proceed, return_, arguments, advised_attribute, advised_instance, suppress_aspect
)
from .aopmeta import AOPMeta
from .aspect import Aspect

