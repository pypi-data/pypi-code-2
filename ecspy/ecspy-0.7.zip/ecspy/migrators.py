"""
    This module provides pre-defined migrators for evolutionary computations.

    All migrator functions have the following arguments:
    
    - *random* -- the random number generator object
    - *population* -- the population of Individuals
    - *args* -- a dictionary of keyword arguments
    
    Each migrator function returns the updated population.
    
    .. Copyright (C) 2009  Inspired Intelligence Initiative

    .. This program is free software: you can redistribute it and/or modify
       it under the terms of the GNU General Public License as published by
       the Free Software Foundation, either version 3 of the License, or
       (at your option) any later version.

    .. This program is distributed in the hope that it will be useful,
       but WITHOUT ANY WARRANTY; without even the implied warranty of
       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
       GNU General Public License for more details.

    .. You should have received a copy of the GNU General Public License
       along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def default_migration(random, population, args):
    """Do nothing.
    
    This function just returns the existing population with no changes.
    
    """
    return population