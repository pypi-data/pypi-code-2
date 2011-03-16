####################################################################################
#                                                                                  #
# Copyright (c) 2006 Dr. Conan C. Albrecht <conan_albrechtATbyuDOTedu>             #
#                                                                                  #
# This file is part of Picalo.                                                     #
#                                                                                  #
# Picalo is free software; you can redistribute it and/or modify                   #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation; either version 2 of the License, or                # 
# (at your option) any later version.                                              #
#                                                                                  #
# Picalo is distributed in the hope that it will be useful,                        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with Foobar; if not, write to the Free Software                            #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA        #
#                                                                                  #
####################################################################################
#                                                                                  #
#  This file is globally imported into Picalo.  See picalo/__init__.py.            # 
#  When you write "from picalo import *", these functions all get imported.        #
#                                                                                  #
####################################################################################

import decimal, sys

  
# global functions (defined in this file)
__all__ = [
  'number',
]


#######################################################
###   Number class for correct floating point type

class number(decimal.Decimal):
  '''A number with a decimal point.  This number does correct math while the 
     Python float type contains rounding errors in math.'''

  def __new__(cls, value="0", context=None):
    '''Creates a new number.'''
    if isinstance(value, float):  # Decimal doesn't take a float, we want to
      return decimal.Decimal.__new__(cls, str(value), context)
    return decimal.Decimal.__new__(cls, value, context)


  def __repr__(self):
    '''Returns a string representation of this number'''
    return str(self)


  def __pg_repr__(self):
    '''Required for PygreSQL driver'''
    return self
    
    
########################################################################
###   Conversion method - used before all arithmetic in the class

def _convert_other(*args, **kargs):
  '''Converts other to a number object'''
  if len(args) == 0:
    return None
  other = args[0]
  if isinstance(other, decimal.Decimal):
    return other
  if isinstance(other, (str, unicode)) and other == '': # if an empty string
    return number()
  if isinstance(other, (int, long, str, unicode, float)):
    return number(other)
  return NotImplemented
  
# replace Decimal's _convert_other function so we can work with floats
decimal._convert_other = _convert_other