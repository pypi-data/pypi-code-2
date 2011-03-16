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

import sys
  
# global functions (defined in this file)
__all__ = [
  'error',
]

####################################
###   The error type for picalo
###   When errors are thrown in calculations,
###   an error object is placed in the cell.
###   The error shows in the cell as <err>,
###   but as an object allows the user to
###   find out the specifics of the error.

class error:
  def __init__(self, exc=None, msg=None, previous=None):
    '''An error type that signifies that an error occurred when
       calculating the value for some cell.  Don't create this
       directly.  Picalo creates them when errors
       are encountered during analyses so the analysis doesn't 
       get stopped by small errors.
       
       The error object is useful in that it encodes information
       about what went wrong.  Although it only prints as <err>
       in table listings, it can be inspected as shown in the 
       set_type method example.
       
       @param exc:         The exception object.
       @type  exc:         Exception
       @param msg:         Allows you to provide a specific error message.  Defaults to str(exception).
       @type  msg:         str
       @param previous:    The previous value of the cell, so we don't lose it.
       @type  previous:    object
    '''
    self.msg = msg
    self.exc = None
    self.previous = previous
    if exc:
      if msg == None:  # default the message if not explicitly set
        self.msg = str(exc)
      if isinstance(exc, Exception):
        self.exc = exc
    if self.msg == None:  # ensure we have at least some message
       self.msg = 'Unspecified Error'
    
  def __repr__(self):
    return '<err: ' + str(self.msg) + '>'
    
  def __str__(self):
    return '<err: ' + str(self.msg) + '>'
    
  def get_message(self):
    '''Returns the actual error message.  This allows the object
       to be interrogated for what really went wrong.
     
       @return:  The error message.
       @rtype:   str
    '''
    return self.msg
    
  def get_exception(self):
    '''Returns the exception object associated with this error.
       This might be None if no object was created.
       
       @return:   The exception object that caused this error.
       @rtype:    Exception
    '''
    return self.exc
    
  def get_previous(self):
    '''Returns the previous value of the cell before the error
       was placed in the table.  This might be none if the 
       error didn't replace a cell value.
       
       @return:   The previous value of the cell where this error occurred.
       @rtype:    object
    '''
    return self.previous
    
  # the error object replaces other variables in table cells, and
  # therefore is sent into many routines.  therefore, it must be
  # able to act like the object it replaced (str, int, etc.) or
  # it will cause additional errors
  def __lt__(self, other): return id(self) < id(other)   # compare ids to get consistency for the algorithm
  def __le__(self, other): return id(self) <= id(other)
  def __eq__(self, other): return id(self) == id(other)
  def __ne__(self, other): return id(self) != id(other)
  def __gt__(self, other): return id(self) > id(other)
  def __ge__(self, other): return id(self) >= id(other)
  def __cmp__(self, *args, **kargs): return cmp(id(self, *args, **kargs), id(other))
  def __nonzero__(self, *args, **kargs): return True
  def __len__(self, *args, **kargs): return 0
  def __getitem__(self, key): return self
  def __setitem__(self, key, value): pass
  def __delitem__(self, key): pass
  def __iter__(self, *args, **kargs): return iter([])
  def __contains__(self, item): return False
  def __add__(self, *args, **kargs): return self
  def __sub__(self, *args, **kargs): return self
  def __mul__(self, *args, **kargs): return self
  def __floordiv__(self, *args, **kargs): return self
  def __mod__(self, *args, **kargs): return self
  def __divmod__(self, *args, **kargs): return self
  def __pow__(self, *args, **kargs): return self
  def __lshift__(self, *args, **kargs): return self
  def __rshift__(self, *args, **kargs): return self
  def __and__(self, *args, **kargs): return self
  def __xor__(self, *args, **kargs): return self
  def __or__(self, *args, **kargs): return self
  def __div__(self, *args, **kargs): return self
  def __truediv__(self, *args, **kargs): return self
  def __radd__(self, *args, **kargs): return self
  def __rsub__(self, *args, **kargs): return self
  def __rmul__(self, *args, **kargs): return self
  def __rdiv__(self, *args, **kargs): return self
  def __rtruediv__(self, *args, **kargs): return self
  def __rfloordiv__(self, *args, **kargs): return self
  def __rmod__(self, *args, **kargs): return self
  def __rdivmod__(self, *args, **kargs): return self
  def __rpow__(self, *args, **kargs): return self
  def __rlshift__(self, *args, **kargs): return self
  def __rrshift__(self, *args, **kargs): return self
  def __rand__(self, *args, **kargs): return self
  def __rxor__(self, *args, **kargs): return self
  def __ror__(self, *args, **kargs): return self
  def __iadd__(self, *args, **kargs): return self
  def __isub__(self, *args, **kargs): return self
  def __imul__(self, *args, **kargs): return self
  def __idiv__(self, *args, **kargs): return self
  def __itruediv__(self, *args, **kargs): return self
  def __ifloordiv__(self, *args, **kargs): return self
  def __imod__(self, *args, **kargs): return self
  def __ipow__(self, *args, **kargs): return self
  def __ilshift__(self, *args, **kargs): return self
  def __irshift__(self, *args, **kargs): return self
  def __iand__(self, *args, **kargs): return self
  def __ixor__(self, *args, **kargs): return self
  def __ior__(self, *args, **kargs): return self
  def __neg__(self, *args, **kargs): return self
  def __pos__(self, *args, **kargs): return self
  def __abs__(self, *args, **kargs): return self
  def __invert__(self, *args, **kargs): return self
  def __complex__(self, *args, **kargs): return complex(0)
  def __int__(self, *args, **kargs): return 0
  def __long__(self, *args, **kargs): return 0
  def __float__(self, *args, **kargs): return 0.0
  def __oct__(self, *args, **kargs): return str(self, *args, **kargs)
  def __hex__(self, *args, **kargs): return str(self, *args, **kargs)
  def __coerce(self, other): return (self, other)
