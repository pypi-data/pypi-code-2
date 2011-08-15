"""
This module defines constants of general utility in the PyWeaver library.

The interpretation of each constant is dependent on the context.  In order to determine the precise
meaning of a constant, reference the documentation for the method/function that it is being used 
with.
"""

"""
Copyright 2007 Derek Ruths

This file is part of PyWeaver.

PyWeaver is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyWeaver is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PyWeaver.  If not, see <http://www.gnu.org/licenses/>.
"""

__all__ = ['ALL','NODES','EDGES','DIRECTED','UNDIRECTED','BOTH','IN','OUT','INFINITY']

INFINITY = float('infinity')

ALL = 'ALL'
NODES = 'NODES'
EDGES = 'EDGES'

DIRECTED = 'DIRECTED'
UNDIRECTED = 'UNDIRECTED'

BOTH = 'BOTH'
IN = 'IN'
OUT = 'OUT'
