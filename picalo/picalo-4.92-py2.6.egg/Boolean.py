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

import types


  
# global functions (defined in this file)
__all__ = [
  'boolean',
]


class boolean:  # btw, can't extend bool as it's a special singleton class
  '''A flag type, such as on/off, true/false, etc.  The following
     values are considered true (case is always ignored):
       - t (T)
       - true (True, TRUE, TrUe)
       - yes (Yes, YES, YeS)
       - on (ON, On, oN)
       - any integer other than 0
  '''
  def __init__(self, *args, **kargs):
    '''Creates a new boolean object'''
    if len(args) >= 1 and isinstance(args[0], types.StringTypes) and args[0].lower() in [ 't', 'true', 'yes', 'on' ]:
      self._value = True
    elif len(args) >= 1 and isinstance(args[0], types.BooleanType):
      self._value = args[0]
    elif len(args) >= 1 and isinstance(args[0], (types.IntType, types.LongType, types.FloatType)):
      self._value = (args[0] != 0)
    elif len(args) >= 1 and isinstance(args[0], boolean):
      self._value = args[0]._value
    else:
      self._value = False
    
  
  def __eq__(self, other):
    '''Returns whether this boolean value matches the other one'''
    if isinstance(other, boolean):
      return self._value == other._value
    elif isinstance(other, types.BooleanType):
      return self._value == other
    else:
      return self._value == boolean(other)._value
      
      
  def __repr__(self):
    return self._value and 'True' or 'False'
    
    
