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


import os, sys, time, types, codecs, gzip
import re, inspect, linecache, csv, xml.dom.minidom
from Table import Table
from Global import check_valid_table, show_progress, clear_progress, ensure_valid_variables, make_unique_colnames
import ZODB.DB
import persistent
from persistent.list import PersistentList


# global functions (defined in this file)
__all__ = [
  'TableArray',
]
  

##########################################################
###   TableArray type
###   A simple extension to list to allow lists of tables
###   to be identified without having to look through all
###   the elements to ensure they are Tables.
###
###   All of the elements of a TableArray must be 
###   compatible with the same columns, etc.  

class TableArray(persistent.Persistent):
  def __init__(self, *args):
    '''A list of picalo tables.  Some functions in Picalo return a set
       of tables.  Sets of tables are returned as TableArray objects.  These
       objects have the exact same methods and behavior as typical Python
       lists.
       
       For example, the Grouping.stratify_by_value() method stratifies
       a table into a number of smaller tables.  These tables are
       returned in TableArray objects.  You can access individual tables
       in a TableArray using the [n] notation.
       
       Users do not normally create TableArrays.  They are created automatically
       by Picalo functions.
       
       TableArrays must hold the exact same type of table.  For example, two
       tables in a given TableArray may not have different column names.
       If you need to hold a list of noncompatible tables (i.e. tables with
       different columns or types), use a TableList object.
       
       Example:
        >>> data = Table([
        ...   ('id', int),
        ...   ('name', unicode),
        ... ],[
        ...   [ 1, 'Benny' ],
        ...   [ 2, 'Vijay' ],
        ... ])
        >>> tables = Grouping.stratify_by_value(data, 'id')
        >>> tables[0].view()
        +----+-------+
        | id |  name |
        +----+-------+
        |  1 | Benny |
        +----+-------+
        >>> tables[1].view()
        +----+-------+
        | id |  name |
        +----+-------+
        |  2 | Vijay |
        +----+-------+
        >>> for table in tables:
        ...   print len(table)        
        ...
        1
        1
    '''
    self.changed = False
    if len(args) == 0:
      self._tables = PersistentList() 
    else:
      self._tables = PersistentList(args[0]) 
    for value in self:
      self._check_valid_table(value)
      
  
  def view(self):
    '''Opens the table list for viewing in the Picalo user interface.
       The resulting view allows you to page through the tables in the
       list.  See the first example.
       
       You can view individual tables in the list by using the [n]
       notation.  See the second example for this notation.
       
       Example:
        >>> data = Table([
        ...   ('id', int),
        ...   ('name', unicode),
        ... ],[
        ...   [ 1, 'Benny' ],
        ...   [ 2, 'Vijay' ],
        ... ])
        >>> tables = Grouping.stratify_by_value(data, 'id')
        >>> tables.view()
         
       Example:
        >>> data = Table([
        ...   ('id', int),
        ...   ('name', unicode),
        ... ],[
        ...   [ 1, 'Benny' ],
        ...   [ 2, 'Vijay' ],
        ... ])
        >>> tables = Grouping.stratify_by_value(data, 'id')
        >>> tables[0].view()
         
    '''
    from Global import mainframe
    if mainframe != None:
      # try to figure out the variable name of this table by inspecting the call stack
      f = inspect.currentframe().f_back
      locals = f.f_locals
      for name in f.f_code.co_names:
        if locals.has_key(name) and locals[name] == self:
          mainframe.openTable(name)
          return
    # if we get here, either we're in console mode or we couldn't find the variable name
    print self
    

  def _check_valid_table(self, table):
    '''Ensures that a given table is valid'''
    try:
      assert isinstance(table, (Table, TableArray)), 'This type of list can only hold Picalo Tables or TableArrays.  You sent %s.' % (table.__class__, )
      if len(self) > 0:
        assert table.get_columns() == self[0].get_columns(), 'Incompatible table.  All tables in a TableArray must have the same columns, types, etc.'
    except AssertionError, e:
      raise TypeError, str(e)
    
  
  def __repr__(self):
    '''For debugging.
       @return:   The number of tables in this TableArray.
       @rtype:    str
    '''
    return '<TableArray of %s: %s>' % (len(self), ', '.join([ repr(t) for t in self._tables]))
  
  def __str__(self):
    '''For debugging.
       @return:   The number of tables in this TableArray.
       @rtype:    str
    '''
    return '<TableArray of %s: %s>' % (len(self), ', '.join([ str(t) for t in self._tables]))
  
  
  ##### CONTAINER METHODS ####
  
  def __iter__(self):
    '''Returns an iterator to this TableArray'''
    return TableArrayIterator(self)
    
    
  def __contains__(self, table):
    '''Returns whether the given table is in this TableArray'''
    if isinstance(table, (Table, TableArray)):
      for item in self:
        if item.get_columns() == table.get_columns() and item == table: # item == table checks the values of the tables
          return true
    return False
    
    
  def __eq__(self, other):
    '''Returns whether this TableArray is equal to a list/tuple/TableArray of tables.'''
    if other != None and len(self) == len(other):
      for i in range(len(self)):
        if self[i] != other[i]:
          return False
      return True
    return False
    

  def __ne__(self, other):
    '''Returns whether this TableArray is not equal to a list/tuple/TableArray of tables.'''
    return not self.__eq__(other)  
  
  
  def __len__(self):
    return len(self._tables)
    
  
  def __getitem__(self, index):
    return self._tables[index]


  def __setitem__(self, index, table):
    self._check_valid_table(table)
    self.changed = True
    self._tables[index] = table

  
  def __setslice__(self, i, j, sequence):
    for value in sequence:
      self._check_valid_table(value)
    self.changed = True
    self._table.__setslice__(i, j, sequence)


  def __getslice__(self, i, j):  
    return self._table.__getslice__(i, j)
    
    
  def append(self, table):
    self._check_valid_table(table)
    self.changed = True
    self._tables.append(table)

    

  ###################################################################
  ###   Table functions that are applied to each table in the list

  def _add_listener(self, listener):
    '''Adds a listener to the table.  Will be notified when data changes occur.
       The listener should be a callable/function of form callback(table).  For
       efficiency reasons and because we don't need it right now,
       the col and row is not reported.'''
    for table in self:
      table._add_listener(listener)
    
    
  def _remove_listener(self, listener):
    '''Removes a listener from the table.'''
    for table in self:
      table._remove_listener(listener)


  def _notify_listeners(self, level=1):
    '''Notifies listeners that we've had a change'''
    for table in self:
      table._notify_listeners(level)


  def _invalidate_indexes(self):
    '''Invalidates the indices already calculated on this table.  This occurs anytime
       data are modified in this table'''
    for table in self:
      table._invalidate_indexes()


  def is_changed(self):
    '''Returns whether the table has been changed since loading'''
    if self.changed:
      return True
    for table in self:
      if table.is_changed():
        return True
    return False
    
    
  def set_changed(self, changed):
    '''Sets whether the class has been changed since loading.  This is not normally
       called by users.'''
    self.changed = True


  def set_readonly(self, readonly_flag=False):
    '''Sets the read only status of this table.  Tables that are read only cannot
       be modified.  Normally, tables are initially not read only (i.e. can be modified).
       The only exception is tables loaded from databases, which are read only.
       
       @param readonly_flag: True or False, depending upon whether the table should be read only or not.
       @type  readonly_flag: bool
    '''
    for table in self:
      table.set_readonly(readonly_flag)
  

  def is_readonly(self):
    '''Returns whether this table is read only.
       @return:  Whether this table is read only.
       @rtype:   bool
    '''
    if len(self) > 0:
      return self[0].is_readonly()
    return False


  def filter(self, expression=None):
    '''Applies the given filter to all tables in the list.  
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.filter(expression)
      
      
  def clear_filter(self):
    '''Clears any active filter to all tables in the list.  
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.clear_filter()
       

  def is_filtered(self):
    '''Returns whether the first table in this list is filtered.'''
    if len(self) > 0:
      return self[0].is_filtered()
    return False


  def get_filter_expression(self):
    '''Returns the filter expression as a PicaloExpression object, or None if no filter is applied.'''
    if len(self) > 0:
      return self[0].get_filter_expression()
    return None


  def column(self, col):
    '''Returns the given column from the first table in this list.  Since all
       tables have the same column definitions, it is comparable across all
       tables in the list.'''
    if len(self) > 0:
      return self[0].column(col)
    return None
    

  def get_columns(self):
    '''Returns the columns from the first table in this list.  Since all
       tables have the same column definitions, it is comparable across all
       tables in the list.'''
    if len(self) > 0:
      return self[0].get_columns()
    return None
    
    
  def get_column_names(self):
    '''Returns the column names from the first table in this list.  Since all
       tables have the same column definitions, it is comparable across all
       tables in the list.'''
    if len(self) > 0:
      return self[0].get_column_names()
    return []
    
    
  def column_count(self):
    '''Returns the column count from the first table in this list.  Since all
       tables have the same column definitions, it is comparable across all
       tables in the list.'''
    if len(self) > 0:
      return self[0].column_count()
    return 0


  def set_name(self, column, name):
    '''Sets the column name for all tables in the list.  
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.set_name(column, name)


  def set_type(self, column, column_type=None, format=None, expression=None):
    '''Sets the column type for all tables in the list.  
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.set_type(column, column_type, format, expression)


  def set_format(self, column, format=None):
    '''Sets the format for a column in all tables in the list.
       See the definition of this method in Table for more information.'''
    for table in self:
      table.set_format(column, format)       
    
    
  def guess_types(self, num_records=-1):
    '''Guesses the column types for all tables in the list.  
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.guess_types(num_records)


  def append_column(self, name, column_type, values=None):
    '''Adds a new column to each table in the list.
       See the definition of this method in Table for more 
       information.'''
    assert isinstance(values, (types.NoneType, TableArray)), 'If the values parameter is provided, it must be a TableArray of values to add'
    for i, table in enumerate(self):
      if values == None or i >= len(values):
        table.append_column(name, column_type)
      else:
        table.append_column(name, column_type, values[i])
      
      
  def insert_column(self, index, name, column_type, values=None):
    '''Inserts a new column to each table in the list.
       See the definition of this method in Table for more 
       information.'''
    assert isinstance(values, (types.NoneType, TableArray)), 'If the values parameter is provided, it must be a TableArray of values to add'
    for i, table in enumerate(self):
      if values == None or i >= len(values):
        table.insert_column(name, column_type)
      else:
        table.insert_column(index, name, column_type, values[i])
      

  def append_calculated(self, name, expression):
    '''Appends a calculated column to each table in the list.
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.append_calculated(name, expression)
  
  
  def insert_calculated(self, index, name, expression):
    '''Inserts a calculated column to each table in the list.
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.insert_calculated(index, name, expression)
  
  
  def append_calculated_static(self, name, column_type, expression):
    '''Appends a calculated column to each table in the list.
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.append_calculated_static(name, column_type, expression)
  

  def insert_calculated_static(self, index, name, column_type, expression):
    '''Inserts a calculated column to each table in the list.
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.insert_calculated_static(index, name, column_type, expression)
  

  def move_column(self, column, new_index):
    '''Moves a column to another location for each table in the list.
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.move_column(column, new_index)


  def delete_column(self, column):
    '''Deletes a column from each table in the list.
       See the definition of this method in Table for more 
       information.'''
    for table in self:
      table.delete_column(column)
  

  def structure(self):
    '''Returns the structure of the first table in this list.  Since all
       tables have the same column definitions, it is comparable across all
       tables in the list.'''
    if len(self) > 0:
      return self[0].structure()
    return None
    

  def combine(self):
    '''Combines this table array into a single table.  This is a kind of 'anti-stratification'.
       The new table has all the records of the tables in the TableArray.
    '''
    # create the new table
    results = Table(self.get_columns())
    # append the results from each table in the array
    try:
      for i, table in enumerate(self):
        show_progress('Combining into table...', float(i) / len(self))
        results.extend(table)
    finally:
      clear_progress()
    return results
    
          
  def save(self, filename, respect_filter=False):
    '''Saves this TableList in native Picalo format.  This is the preferred
       format to save TableLists in because all column types, formulas, and so
       forth are saved.
    
       @param filename: The filename to save to.  This can also be an open stream.
       @type  filename: str
       @param respect_filter Whether to save the entire file or only those rows available through any current filters.
       @type  respect_filter bool
    '''
    # I can't import save until now because TableArray class must be declared first
    from Table import save as table_save
    table_save(self, filename, respect_filter)


  def save_delimited(self, filename, delimiter=',', qualifier='"', line_ending='\n', none='', encoding='utf-8', respect_filter=False):
    '''Saves this TableList in delimited format.  Since the table list probably has multiple tables
       in it, one delimited file per table is created by prepending 1, 2, 3 to the filename.

       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param delimiter:    An optional field delimiter character
       @type  delimiter:    str
       @param qualifier:    An optional qualifier to use when delimiters exist in field values
       @type  qualifier:    str
       @param line_ending:  An optional line ending to separate rows with
       @type  line_ending:  str
       @param none:         An optional parameter specifying what to write for cells that have the None value.
       @type  none:         str
       @param encoding:     The unicode encoding to use for international or special characters.  For example, Microsoft applications like to use special characters for double quotes rather than the standard characters.  Unicode (the default) handles these nicely.
       @type  encoding:     str
       @param respect_filter Whether to save the entire file or only those rows available through any current filter.
       @type  respect_filter bool
    '''    
    for i, table in enumerate(self):
      table.save_delimited('%05i-' % i + filename, delimiter, qualifier, line_ending, none, encoding, respect_filter)
      

  def save_csv(self, filename, line_ending='\n', none='', encoding='utf-8', respect_filter=False):
    '''Saves this TableList in CSV format.  Since the table list probably has multiple tables
       in it, one CSV per table is created by prepending 1, 2, 3 to the filename.

       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param line_ending:  An optional line ending to separate rows with
       @type  line_ending:  str
       @param none:         An optional parameter specifying what to write for cells that have the None value.
       @type  none:         str
       @param encoding:     The unicode encoding to use for international or special characters.  For example, Microsoft applications like to use special characters for double quotes rather than the standard characters.  Unicode (the default) handles these nicely.
       @type  encoding:     str
       @param respect_filter Whether to save the entire file or only those rows available through any current filter.
       @type  respect_filter bool
    '''
    for i, table in enumerate(self):
      table.save_csv('%05i-' % i + filename, line_ending, none, encoding, respect_filter)
    

  def save_tsv(self, filename, line_ending='\n', none='', encoding='utf-8', respect_filter=False):
    '''Saves this TableList in tsv format.  Since the table list probably has multiple tables
       in it, one tsv file per table is created by prepending 1, 2, 3 to the filename.

       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param line_ending:  An optional line ending to separate rows with
       @type  line_ending:  str
       @param none:         An optional parameter specifying what to write for cells that have the None value.
       @type  none:         str
       @param encoding:     The unicode encoding to use for international or special characters.  For example, Microsoft applications like to use special characters for double quotes rather than the standard characters.  Unicode (the default) handles these nicely.
       @type  encoding:     str
    '''
    for i, table in enumerate(self):
      table.save_tsv('%05i-' % i + filename, line_ending, none, encoding, respect_filter)
    
    
  def save_fixed(self, filename, line_ending='\n', none='', respect_filter=False):
    '''Saves this TableList in fixed format.  Since the table list probably has multiple tables
       in it, one fixed file per table is created by prepending 1, 2, 3 to the filename.

       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param line_ending:  An optional line ending to separate rows with
       @type  line_ending:  str
       @param none:         An optional parameter specifying what to write for cells that have the None value.
       @type  none:         str
       @param respect_filter Whether to save the entire file or only those rows available through any current filter.
       @type  respect_filter bool
    '''
    for i, table in enumerate(self):
      table.save_fixed('%05i-' % i + filename, line_ending, none, respect_filter)
    
    
  def save_xml(self, filename, line_ending='\n', indent='\t', compact=False, none='', respect_filter=False):
    '''Saves this TableList in xml format.  Since the table list probably has multiple tables
       in it, one xml file per table is created by prepending 1, 2, 3 to the filename.

       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param line_ending:  An optional line ending to separate rows with (when compact is False)
       @type  line_ending:  str
       @param indent:       The character(s) to use for indenting (when compact is False)
       @type  indent:       str
       @param compact:      Whether to compact the XML or make it "pretty" with whitespace
       @type  compact:      bool
       @param none:         An optional parameter specifying what to write for cells that have the None value.
       @type  none:         str
       @param respect_filter Whether to save the entire file or only those rows available through any current filter.
       @type  respect_filter bool
    '''
    for i, table in enumerate(self):
      table.save_xml('%05i-' % i + filename, line_ending, indent, compact, none, respect_filter)
    
    
    
###############################
###   Iterator for a TableArray
   
def TableArrayIterator(ta):     
  '''Returns a generator object to iterate over the tables in a TableArray'''
  index = 0
  numcols = len(ta)
  while index < numcols:
    yield ta[index]
    index += 1  


    
