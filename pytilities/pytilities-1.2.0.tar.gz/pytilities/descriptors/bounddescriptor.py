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

from .dereferencedbounddescriptor import DereferencedBoundDescriptor

def BoundDescriptor(descriptor, instance):
    '''
    Constructs a descriptor with an object bound to it.

    It's like bound methods, but more general (supports all descriptors rather
    than just functions).

    :param descriptor: The descriptor to bind to
    :type descriptor: descriptor
    :param instance: The instance to be bound
    :type instance: any
    '''
    return DereferencedBoundDescriptor(
        property(lambda o: descriptor),
        property(lambda o: instance)
    )
