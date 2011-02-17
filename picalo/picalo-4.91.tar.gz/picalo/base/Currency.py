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
#
#  THIS CLASS IS DEPRECATED. IT IS NO LONGER NEEDED NOW THAT COLUMNS
#  CAN HAVE FORMATS.  JUST USE A number FIELD AND THE FORMAT: $#,##0.00
#
#
import types, re
from Number import number

# global functions (defined in this file)
__all__ = [
  'currency',
]

RE_IMPORT = re.compile('^.*?(\d+\.\d+|\d+).*?$')

class currency(number):
  '''A simple extension to number to deliniate a currency type.  In future versions,
     we'll make this class support the currencies from around the world.'''
  def __new__(self, value=0.0):
    if value and isinstance(value, types.StringTypes):
      match = RE_IMPORT.search(value)
      if match:
        value = match.group(1)
    return number(value)
     
     
