# Copyright 2010 Oren Zomer <oren.zomer@gmail.com>
#
# This file is part of pypsifas.

# pypsifas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pypsifas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pypsifas.  If not, see <http://www.gnu.org/licenses/>.

import operator

class NoClass(object):
    """
    Thisclass is used when we cannot import some classes.
    """
    def __init__(self):
        raise ImportError("Original class could not be imported")

try:
    from scapy.all import Packet as ScapyPacket
    from scapy.all import NoPayload as ScapyNoPayload
    def is_sequence_type(a):
        return operator.isSequenceType(a) and not isinstance(a, ScapyPacket) and hasattr(a, '__len__')
except ImportError:
    ScapyPacket = ScapyNoPayload = NoClass
    def is_sequence_type(a):
        return operator.isSequenceType(a) and hasattr(a, '__len__')
