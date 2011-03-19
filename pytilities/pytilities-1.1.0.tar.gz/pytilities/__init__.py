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

'''\
Pytilities is a python3 utility library.

For more information, see:

- `Pytilities homepage`_
- `Documentation`_

.. _Pytilities homepage: http://pytilities.sourceforge.net/
.. _Documentation: http://pytilities.sourceforge.net/doc/1.1.0/

'''

__docformat__ = 'reStructuredText'

from .stringifiable import Stringifiable
from .functions import (
    has_attr_name, has_attr_value, get_attr_name,
    get_attr_value, mangle, get_annotations)

