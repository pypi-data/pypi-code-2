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

import inspect, types
from Error import error
from Record import Record

#################################################
###   Helper functions for Picalo

def get_current_vars(*locals):
  '''Returns the locals and globals from ALL frames top to bottom. Variables
     in inner-most frames override the outermost frames.
     
     The locals is a list of local dictionaries, with the first ones listed
     overriding any variables in the latter ones listed.  These take precendence
     over any variables found in the frames.
  '''
  # get the globals and locals from previous frames
  # this is required because functions and variables in outer frames
  # can be used in evaluate expressions
  # this is different than regular python, but it makes sense
  # in the context of cell expressions
  g = {}
  l = {}
  stack = inspect.stack()
  stack.reverse()  # so the vars from inner-most frames override the outermost frames
  for frame in stack:
    f = frame[0]
    l.update(f.f_locals)
    g.update(f.f_globals)
  # update with any locals sent in.
  for local in locals:
    l.update(local)
  return l, g
  
  
class PicaloExpression:
  '''A class that compiles an expression.  This is done so the expression
     and locals/globals are only compiled and determined one time rather
     than for each time the expression is run.  It's for efficiency.'''
  def __init__(self, expression, *locals):
    '''Constructor.  The initial_locals and initial_globals dicts override
       any local or global variables'''
    # ensure that we have a string for the expression
    if not isinstance(expression, (types.StringType, types.UnicodeType, PicaloExpression)):
      expression = unicode(expression)
    
    # save the globals, locals, and compile the code
    # we save the locals and globals dicts at creation time rather than at execution time
    self.locals, self.globals = get_current_vars(*locals)
    if isinstance(expression, PicaloExpression):
      self.expression = expression.expression  # don't wrap a PicaloExpression within a PicaloExpression
    else:
      self.expression = expression
    try:
      self.code = compile(self.expression, '<string>', 'eval')
    except Exception, e:
      self.code = compile("error('Expression is invalid: " + str(e).replace("'", "\'") + "')", '<string>', 'eval')
  
  
  def evaluate(self, locals, expression_backtrack=[]):
    '''Runs the expression given any additional locals and globals
    
       locals => A list of dictionaries containing mappings that override the values in locals
       expression_backtrack => A list of all the expression id's we've run so far, to catch circular logic.
    '''
    try:
      # ensure we haven't already done this expression in this chain
      assert not id(self) in expression_backtrack, 'Circular logic detected'
      new_expression_backtrack = [id(self)] + expression_backtrack
      # set up the locals
      l = self.locals
      if len(locals) > 0:
        l = dict(self.locals)  # make a copy so we don't modify the core dictionary
        for d in locals:
          if isinstance(d, Record):  # convenience since records almost always get passed to evaluate 
            l.update([ ( d._table.columns[j].name, d.__get_value__(j, new_expression_backtrack)) for j in range(len(d))])
          else:
            l.update(d)
      # eval the expression
      return eval(self.code, self.globals, l)
    except Exception, e:
      return error(e)
  
  
  def __repr__(self):
    return self.__str__()
    
  
  def __str__(self):
    '''Returns a string representation of this expression'''
    return '<Expression: ' + self.expression + '>'
    
    
  def __eq__(self, other):
    if isinstance(other, PicaloExpression):
      return self.expression == other.expression
    return self.expression == other
  
       
  def __ne__(self, other):
    return not self.__eq__(other)
    
