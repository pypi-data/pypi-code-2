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

from collections import Mapping

class FunctionMap(Mapping):

    '''
    A mapping based on a mapper function
    '''

    def __init__(self, mapper_function):
        '''
        Construct a mapping from a mapper function

        The resulting dict is immutable and its keys() returns an empty set. On
        each item get it will call the mapper function with the given key and
        return its value.

        :param mapper_function: a mapper function
        :type mapper_function: function(key) -> value
        '''
        self._mapper = mapper_function

    def __getitem__(self, key):
        return self._mapper(key)

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

