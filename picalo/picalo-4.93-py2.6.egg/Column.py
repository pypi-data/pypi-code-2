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

from picalo import check_valid_table, is_valid_variable, RESERVED_COLUMN_NAMES, VARIABLE_TYPES_RE, parse_value_to_type, format_value_from_type
from Expression import PicaloExpression
import types
from Calendar import Date, DateTime
from Error import error
from Number import number
import ZODB.DB
import persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList


####################################################
###   Column class

# Columns have both a virtual and actual location in the parent table's _data structure.
# When columns are added to a table, they are always added to the right side, even if they
# are inserted before other columns.  For example, if we have columns a, b, and c, inserting b1 
# between a and b results in actual positions a, b, c, b1.  That way we don't have to go through
# the entire record set and insert a None value to make room for the column.  Virtually, the 
# positioning will be a, b1, b, c so it accesses in the order the user expects.  When
# columns are deleted, we don't actually delete the data -- we just remove the column
# from the virtual list so it no longer shows.  It makes adding, removing, and deleting 
# columns super fast.  To actually delete the data, copy the table and erase the old one.

class Column(persistent.Persistent):
  '''A  single column of the table.  Columns are not copies of the values in the table,
     but rather pointers to the actual table data.  Therefore, changes to the values
     in the column are reflected in the underlying table.
     
     Columns must have unique names from other columns in the table.  Columns must also
     have either a column_type or an expression.
     
     Columns extend Python lists and mimick the list interface.  They can be used anywhere
     a regular Python list can.
  '''
  def __init__(self, table, index, name, column_type=None, expression=None, format=None):
    '''Creates a Column.  Do not call this method directly.  Rather, call mytable["colname"]'''
    check_valid_table(table)
    self.virtual_col_index = index  # the virtual location in the table or -1 if inactive
    self.table = table
    self.set_name(name)
    self.column_type = None
    self.expression = None
    self.format = None
    self.static_expression = None   # not used directly here, but stored so we can repopulate the TableProperties dialog
    self.set_type(column_type, format=format, expression=expression)
    
    
  def set_name(self, name):
    '''Sets the name of this column to the given name'''
    assert not self.table.is_readonly(), 'This table is set as read-only and cannot be modified.'
    assert isinstance(name, types.StringTypes), 'Invalid column name: ' + str(name)
    assert is_valid_variable(name), 'Invalid column name: %s.  Column names must start with a letter and then contain letters and numbers only.' % (str(name), )
    for col in self.table.columns:
      assert id(col) == id(self) or col.name != name, 'Two table columns cannot have the same name: ' + str(name)
    assert not RESERVED_COLUMN_NAMES.has_key(name), 'The name "' + str(name) + '" is a Picalo reserved word.  Please choose another name.'
    self.name = name
    self.table._calculate_columns_map()
    self.table.set_changed(True)
    self.table._notify_listeners()
    
    
  def __repr__(self):
    '''For debugging'''
    return '<Column instance: ' + self.name + '>'
    
    
  def __eq__(self, other):
    '''Compares this column with another column.  Everything must match except the table the two columns are bound to'''
    if isinstance(other, Column) and \
       self.name == other.name and \
       self.expression == other.expression and  \
       self.column_type == other.column_type:
         return True 
    return False


  def __ne__(self, other):
    '''Opposite of __eq__.  Checks whether two columns are not equals.'''
    return not self.__eq__(other)
    

  def set_type(self, column_type, format=None, expression=None):
    '''Sets the type of a column.   The type must be a valid <type> object,
       such as int, float, str, unicode, DateTime, etc.  All values in this
       column will be converted to this new type.
       
       @param column_type:  The new type of this column.
       @type  column_type:  type
       @param format:       A Picalo expression that evaluates to a string, using 'value' as the value of the field.
       @type  format:       str
       @param expression:   A Picalo expression that calculates this column. 
       @type  expression:   str
    '''
    assert not self.table.is_readonly(), 'This table is set as read-only and cannot be modified.'
    assert isinstance(column_type, (types.TypeType, types.ClassType)), '"%s" is an invalid column type for column "%s"' % (str(column_type), self.name)
    self.column_type = column_type
    self.static_expression = None
    if expression == None:   # going to a regular column type
      if self.expression != None:  # if previously an expression, record the values of the expression into the cells
        for i in range(len(self)):
          self.table[i][self.virtual_col_index] = self.expression.evaluate(({'record': self.table[i]}, self.table[i]))
        self.expression = None
      else: # going from a regular column type to a different regular column type
        for i in range(len(self)): # convert the current contents of the table
          self[i] = self[i]  # the __setitem__ in Record above will perform the expression
      
    else:  # going to a calculated column type
      if isinstance(expression, PicaloExpression):
        self.expression = PicaloExpression(expression.expression)
      else:
        self.expression = PicaloExpression(expression)
          
    self.set_format(format)
    # update indices
    self.table.set_changed(True)
    self.table._invalidate_indexes()
    self.table._notify_listeners(2)
    
    
  def get_type(self):
    '''Returns the type of this column.'''
    return self.column_type   


  def set_format(self, format=None):
    '''Sets the format of this column.  The format is used for printing and converting dates and for printing numbers.
       Regardless of the format, the cell keeps the full value internally and uses it in all Picalo functions.
       
       The format is made up of a mask consisting of special characters.  The characters are used
       to interpret values being converted or printed.
       
       The special characters used for Date and DateTime fields are as follows:
       
         - %a Locale's abbreviated weekday name.  
         - %A Locale's full weekday name.
         - %b Locale's abbreviated month name.  
         - %B Locale's full month name.  
         - %c Locale's appropriate date and time representation.  
         - %d Day of the month as a decimal number [01,31].  
         - %H Hour (24-hour clock) as a decimal number [00,23].  
         - %I Hour (12-hour clock) as a decimal number [01,12].  
         - %j Day of the year as a decimal number [001,366].  
         - %m Month as a decimal number [01,12].  
         - %M Minute as a decimal number [00,59].  
         - %p Locale's equivalent of either AM or PM. (1)
         - %S Second as a decimal number [00,61]. (2)
         - %U Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0. (3)
         - %w Weekday as a decimal number [0(Sunday),6].  
         - %W Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0. (3)
         - %x Locale's appropriate date representation.  
         - %X Locale's appropriate time representation.  
         - %y Year without century as a decimal number [00,99].  
         - %Y Year with century as a decimal number.  
         - %Z Time zone name (no characters if no time zone exists).  
         - %% A literal '%' character.
         
       The following are examples of date and time formats:
       
         - %a, %d %b %Y (Thu, 28 Jun 2001)
         - %B %d, %Y (June 28, 2001)
         - %Y-%m-%d (2015-12-30)
         - %Y/%m/%d (2015/12/30)
         - %a, %d %b %Y %H:%M:%S (Thu, 28 Jun 2001 14:17:15)
         - %B %d, %Y %H:%M:%S (June 28, 2001 14:17:15)
         - %Y-%m-%d %H:%M:%S (2015-12-30 14:17:15)
         - %Y/%m/%d %H:%M:%S (2015/12/30 14:17:15)
       
       The special characters used for all number fields (int, long, float, number, etc.) are as follows:
       
         - Prefix the format with any character(s) (like $) to add to the front of the number.
         - End the format with a zero (0) to round to the nearest whole number.
         - Use a period (.) to denote decimal portions of the number.
         - Use a pound (#) to denote a regular number.
         - Use a comma (,) to denote a thousands separator (use with # signs to place it every three numbers)
         - Use a percent (%) to denote the value should be displayed as a percent (multiplied by 100 to when displayed and divide by 100 when parsing input and the number ends with a %)
         - Use the letter E+ followed by zeros to denote scientific notation. 
         
       The following are examples of number formats:
       
         - 0 (round to the nearest whole number;  10.99 is displayed as 11; 12.3 is displayed as 12)
         - 0.00 (rounds to the nearest hundredth; 10.99 is formatted as 10.99; 12.309 is formatted as 12.31; 13 is formatted as 13.00)
         - $0.00 (rounds to the nearest hundredth and adds a dollar sign to the front of the number; you can also use any other character, such as the euro glyph)
         - #,### (formats thousands with a comma;  1234.56 is formatted as 1,234.56)
         - #,##0 (formats thousands with a comma and rounds to the nearest whole number; 1234.56 is formatted as 1,235)
         - #,##0.000 (formats thousands with a comma and rounds to the nearest thousandth; 1234.56 is formatted as 1,234.560)
         - 0% (rounds to the nearest whole number, multiplies by 100 (for display only), and adds a percent sign)
         - 0.00% (rounds to the nearest hundredth, multiplies by 100 (for display only), and adds a percent sign)
         - #E+000 (shows the number in scientific notation to the given number of decimal places)
         
       As of right now, the following formatting options are not available:
         - Numbers with a comma for the decimal separator and a period as the thousands separator.
         - Parentheses for negative numbers.
       
       To set the format on a field, set the format as follows:
         table.column('colname').set_format('#,##0')
       or
         table.set_format('colname', '#%')
       
       To remove the format from a field, set the format to None, as in:
         table.column('colname').set_format(None)
       or
         table.set_format('colname', None)
       
       @param format:  A format mask using the special characters described in the documentation.
       @type  format:  str
    '''
    # add the output function to the column
    self.format = format
    self.table.set_changed(True)
    self.table._notify_listeners(2)
    
    
  def get_format(self):
    '''Returns the format of this column.  If no format has been set, 
       None is returned.'''
    return self.format
    
    
  def format_value(self, value):
    '''Format the given value according to this column's set format.  This method is used when
       showing values in Picalo cells, when exporting, and in pretty printing.  The method
       always returns a unicode string.'''
    return format_value_from_type(value, self.column_type, self.format)
       
       
  def parse_value(self, value):
    '''Parses the given value according to this column's set format.  This method is used when
       importing data into the field.  If the given field is already the correct type,
       it is not parsed but is simply returned.
       
       Picalo uses the format extensively when parsing dates.  However, it always tries to parse
       numbers regardless of the format.  In other words, if a number being placed in a cell contains
       a percent sign, Picalo will divide by 100 when setting the value in the cell.  If a number
       contains scientific notation (ex: 1.23e+45), Picalo will expand the notation, even if a format
       has not been set on a field.
       
       This method is normally called by Record.__setitem__ (whenever a value is set in a table cell).
    '''
    return parse_value_to_type(value, self.column_type, self.format)
    
    

    
  ##### DISABLED LIST METHODS ####  
  def __delitem__(self, col):  raise 'Not allowed on Columns.  Delete at the table level.'
  def append(self, *a, **k):   raise 'Not allowed on Columns.  Append at the table level.'
  def extend(self, *a, **k):   raise 'Not allowed on Columns.  Extend at the table level.'
  def insert(self, *a, **k):   raise 'Not allowed on Columns.  Insert at the table level.'
  def pop(self, *a, **k):      raise 'Not allowed on Columns.  Pop at the table level.'
  def remove(self, *a, **k):   raise 'Not allowed on Columns.  Remove at the table level.'
  def reverse(self, *a, **k):  raise 'Not allowed on Columns.  Reverse not supported.'
  def sort(self, *a, **k):     raise 'Not allowed on Columns.  Sort at the table level.'

  ##### CONTAINER METHODS ####
  
  def __len__(self):
    '''Count the number of records in the column.
    
       @return:  The number of records.  This is the same value as the number of records in the underlying table.
       @rtype:   returns
    '''
    return len(self.table)
    
  def __getitem__(self, recindex):
    '''Retrieves the value of a field in the given record index.
       
       @param    recindex: the record index where the value will be retrieved.
       @type     int
       @return:  The value of the field.
       @rtype:   object
    '''
    assert isinstance(recindex, (types.IntType, types.LongType)), 'Invalid record index: ' + str(num_records)
    return self.table[recindex][self.virtual_col_index]
    
  def __setitem__(self, recindex, value):
    '''Sets a value in the column.  The value of this cell in the underlying table
       is changed.
    
       @param recindex: The record in dex where the value will be stored.
       @type  recindex: int
       @param value: The value to set in the table.
       @type  value: object
    '''
    assert isinstance(recindex, (types.IntType, types.LongType)), 'Invalid record index: ' + str(num_records)
    self.table[recindex][self.virtual_col_index] = value
    
  def __iter__(self):
    return ColumnIterator(self)
  
  
  def __contains__(self, item):
    '''Returns true if the item is in the column'''
    for value in self:  # go through my cell values
      try:
        if item in value:
          return True
      except TypeError:  # occurs when we can't do the "in" keyword in the given value
        if item == value:
          return True
    return False
    

  def _get_columnloader(self):
    '''Returns a column loader for this column (a representation of this column without ties to any table.
       This is normally only used internally in Picalo.
    '''
    column = _ColumnLoader()
    column.name = self.name
    column.column_type = self.column_type
    column.expression = self.expression != None and self.expression.expression or None
    column.format = self.format
    return column
  
  
# _ColumnLoader is used in:
#   1. _loadVersion1 
#   2. Simple.join
#   3. Project.save and Project.load
class _ColumnLoader:
  '''Little class that helps in loading columns'''
  def __init__(self, name=None, column_type=None, expression=None, format=None):
    self.name = name
    self.column_type = column_type
    self.expression = expression
    self.format = format
  


  
##################################################################
###   An iterator for columns
      
def ColumnIterator(column, respect_filter=True):     
  '''Returns a generator object to iterate over a table'''
  index = 0
  table = column.table
  colindex = table.deref_column(column.name)
  numrows = table.record_count(respect_filter)
  while index < numrows:
    yield table.record(index, respect_filter)[colindex]
    index += 1       
      


  