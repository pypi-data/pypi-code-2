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

from Global import check_valid_table
from Error import error
import types
import ZODB.DB
import persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList


####################################################################
###   Represents a row of data



class Record(persistent.Persistent):
  '''An individual record of a Table. Individual fields in a record can be accessed 
     via column number or name.  In the table above, this is done with the following:
       >>> rec1 = mytable3[0]
       >>> print rec1[1]
       'Bart'
       >>> print rec1['Name'] 
       'Bart'
  '''
  def __init__(self, table):
    '''Called by Table's append or insert method.  Do not create Records directly.
       table         => The Picalo table that owns this record
    '''
    assert table != None, 'The table cannot be None when creating a record.'
    self.__dict__['_table'] = table  # can't use regular syntax because we override __setitem__ below
    self.__dict__['_rowdata'] = PersistentList()


  def __repr__(self):
    '''Returns a quick view of this record.  Provide mostly for debugging purposes.'''
    return '<Record: [%s]>' % ', '.join([ str(self[i]) for i in range(len(self.__dict__['_table'].columns)) ])
    
    
  def __str__(self):
    '''Returns a quick view of this record.  Provide mostly for debugging purposes.'''
    return '<Record: [%s]>' % ', '.join([ str(self[i]) for i in range(len(self.__dict__['_table'].columns)) ])
    
    
  def __iter__(self):
    '''Returns an iterator to this record (using the table's column order)'''
    return RecordIterator(self)
    
    
  def __contains__(self, item):
    '''Returns whether the given item is in the record'''
    for value in self:  # go through my cell values
      try:
        if item in value:
          return True
      except TypeError:  # occurs when we can't do the "in" keyword in the given value
        if item == value:
          return True
    return False
    
    
  def __eq__(self, other):
    '''Returns whether this record is equal to a list/tuple/record of values.
       The other parameter can be a record of this table, a record of another table,
       or any list-like object.  Only the values are compared -- the column names
       don't have to match (but the number of columns must be the same).
    '''
    if other != None and len(self) == len(other):
      for i in range(len(self)):
        if self[i] != other[i]:
          return False
      return True
    return False
    

  def __ne__(self, other):
    '''Returns whether this record is not equal to a list/tuple/record of values.
       The other parameter can be a record of this table, a record of another table,
       or any list-like object.  Only the values are compared -- the column names
       don't have to match (but the number of columns must be the same).
    '''
    return not self.__eq__(other)
  
  
    
  ##### CONTAINER METHODS ####
  
  
  def __len__(self):
    '''Returns the length of this record'''
    return self._table.column_count()
    
  
  def has_key(self, key):
    '''Returns whether the record has the given column name'''
    return self._table.columns_map_names.has_key(key)
  
  
  def __getattribute__(self, col):
    '''Retrieves the value of a field in the record.  This method allows
       record.colname type of access to values.  
       
       @param col: The column name or index
       @type  col: str
       @return:    The value in the given field
       @rtype:     returns
    '''
    # I've overridden __getattribute__ because persistent.Persistent.__getattribute__
    # incorrectly calls str(self) if the attribute is not found in the __dict__ of the
    # object.  In other words, __getattr__ never gets called as it should.
    if object.__getattribute__(self, '__dict__').has_key('_table') and object.__getattribute__(self, '_table').columns_map_names.has_key(col):
      return object.__getattribute__(self, '__get_value__')(col, [])
    try:
      return persistent.Persistent.__getattribute__(self, col)
    except AttributeError:
      raise AttributeError('This table has no column named "%s"' % col)
    
  
  def __getitem__(self, col):
    '''Retrieves the value of a field in the record.  This method allows
       record['colname'] type of access to values.
       
       @param col: The column name or index
       @type  col: str
       @return:    The value in the given field
       @rtype:     returns
    '''
    return self.__get_value__(col, [])
    
    
  def __get_value__(self, col, expression_backtrack):
    '''Internal method to retrieve the value of a cell.
       col                  => The column name or index
       expression_backtrack => A list of expression ids that have been run so far, to catch circular formulas
    '''
    # IMPORTANT: This function is called as much as any function in
    # Picalo.  It must be coded in the most efficient way possible.
    # (this entire file would be a good candidate to rewrite in C)

    # if a slice, recursively call me to get the items of the slice
    if isinstance(col, types.SliceType):
      return [ self.__getitem__(col.name) for col in self._table.columns[col] ]
    
    else:  # a regular single request
      ###   START OF NEAR DUPLICATE CODE   ###
      # There is duplicate code in Table.deref_column and Record.__set_item__.
      # If you change something here, modify both of those locations as well.
      # The duplicate code prevents extra method calls and speeds things up considerably.

      # if a name, convert to the index
      if not isinstance(col, int):
        if not col in self._table.columns_map_names:
          raise AttributeError('This table has no column named "%s"' % col)
        col = self._table.columns_map_names[col]
  
      # the column was referenced as a number
      else:
        origcol = col
        # if a negative index, convert to a positive one
        if col < 0:
          col += self._table.num_columns

        # ensure that we have enough columns to fulfill the request
        if col >= self._table.num_columns or col < 0:
          raise IndexError('Column index [%s] is out of range.  The table only has %s columns, referenced with [0] to [%s] or [-1] to [-%s].' % (origcol, self._table.num_columns, self._table.num_columns - 1, self._table.num_columns))

        # deref to the actual column location in the table
        col = self._table.columns_map_virtual[col]
    
      ###   END OF NEAR DUPLICATE CODE   ###  
    
      # get the column definition
      coldef = self._table.columns[col]
      
      # is it a calculated column?
      if coldef.expression:
        return coldef.expression.evaluate([{'record': self}, self], expression_backtrack)
        
      # if not a calculated column, just return the value (or None if the value for this column hasn't ever been set)
      # we don't actually store values in _data until something is set explicitly - None is implied and doesn't need to be stored
      if col < len(self.__dict__['_rowdata']):
        return self.__dict__['_rowdata'][col]
      else:
        return None
      
      
  def __setattr__(self, col, value):
    '''Sets the value of a field in the record.
      
       @param col:   The column name or index
       @type  col:   str/int
       @param value: The value to save in the field
       @type  value: value
    '''
    # first check to see if we have a column name
    if isinstance(col, (int, long)) or self._table.columns_map_names.has_key(col):
      self.__setitem__(col, value)
    # if not, then set as an attribute of the object
    persistent.Persistent.__setattr__(self, col, value)
    
  
  def __setitem__(self, col, value):
    '''Sets the value of a field in the record.
      
       @param col:   The column name or index
       @type  col:   str/int
       @param value: The value to save in the field
       @type  value: value
    '''
    assert not self._table.is_readonly(), 'This table is set as read-only and cannot be modified.'
    
    # if a slice, repeatedly call this method to set each member
    if isinstance(col, types.SliceType):
      for i in range(self._table.deref_column(col.start), self._table.deref_column(col.stop)):
        valueidx = i - self._table.deref_column(col.start)
        if valueidx >= 0 and valueidx < len(value):
          self.__setitem__(i, value[valueidx])
      return
    
    ###   START OF NEAR DUPLICATE CODE   ###
    # There is duplicate code in Record.__get_item__ and Table.deref_column.
    # If you change something here, modify both of those locations as well.
    # This method is called so much that the duplicate code speeds things up by several orders.

    # if a name, convert to the index
    if not isinstance(col, int):
      if not col in self._table.columns_map_names:
        raise IndexError('This table has no column named %s' % col)
      col = self._table.columns_map_names[col]
  
    # the column was referenced as a number
    else:
      origcol = col
      # if a negative index, convert to a positive one
      if col < 0:
        col += self._table.num_columns

      # ensure that we have enough columns to fulfill the request
      if col >= self._table.num_columns or col < 0:
        raise IndexError('Column index [%s] is out of range.  The table only has %s columns, referenced with [0] to [%s] or [-1] to [-%s].' % (origcol, self._table.num_columns, self._table.num_columns - 1, self._table.num_columns))

      # deref to the actual column location in the table
      col = self._table.columns_map_virtual[col]
    
    ###   END OF NEAR DUPLICATE CODE   ###  
    
    # get the column definition
    coldef = self._table.columns[col]
    
    # coerce the value into the right type for this column
    if value != None and not isinstance(value, coldef.column_type):
      try:
        value = coldef.parse_value(value)
      except Exception, e:
        value = error(e)
  
    # invalidate the indices now that we've changed data in this table
    self._table._invalidate_indexes()
  
    # grow the rowdata list to at least this value (we only do this when data are actually assigned to the row)
    while len(self.__dict__['_rowdata']) <= col:
      self.__dict__['_rowdata'].append(None)
    
    # set the value 
    self.__dict__['_rowdata'][col] = value 
    
    # notify listeners that we've had changes
    self._table._notify_listeners()
    
  
  def __setslice__(self, i, j, values):
    '''Sets the value of several items in this record.  Use slice notation:
       table[rec][0:2] = [ 1, 2 ]   # sets first two items
       
       @param i:  The starting index (inclusive)
       @type  i:  int
       @param j:  The ending index (exclusive)
       @type  j:  int
       @param values: A sequence of values to set
       @type  values: list or tuple
    '''
    # note: although setslice is deprecated, it is still in our superclass, so we have to override it
    self.__setitem__(slice(i,j), values)
   
   
###############################
###   Iterator for a record
   
def RecordIterator(record):     
  '''Returns a generator object to iterate over the columns of a record'''
  index = 0
  numcols = len(record._table.columns)
  while index < numcols:
    yield record[index]
    index += 1  


