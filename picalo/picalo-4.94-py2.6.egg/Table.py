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

import os, sys, time, types, codecs, os.path, tempfile, inspect, re, codecs
import xml.dom.minidom
from picalo import check_valid_table, show_progress, clear_progress, make_unicode, useProgress, use_progress_indicators, make_unique_colnames, ensure_valid_variables
from Column import Column, _ColumnLoader
from Record import Record
from Expression import PicaloExpression
from Error import error
import ZODB.DB
import persistent
from zc.blist import BList
from persistent.dict import PersistentDict
from persistent.list import PersistentList
import picalo.lib.pyExcelerator
import picalo.lib.pyExcelerator.CompoundDoc
import picalo.lib.delimitedtext


# global functions (defined in this file)
__all__ = [
  'Table',
  'load_delimited',
  'load_csv',
  'load_tsv',
  'load_fixed',
  'load_excel',
  'save_delimited',
  'save_csv',
  'save_tsv',
  'save_xml',
  'save_fixed',
  'save_excel',  
]


#################################
###   A Picalo table

class Table(persistent.Persistent):
  '''The primary data structure used in Picalo modules.  This is the first object a user
     should learn about since it's used everywhere. Tables are the input into most
     functions and are also the return records of most functions. 
     
     See the Picalo manual for more information on tables.   
     
     Note that Tables should almost always be added to a project after creation
     so they are saved to disk and memory managed.  If a table is assigned only
     to a local variable, its data exist only in memory.  This is faster than 
     project-based tables, but it large tables use a significant amount of memory.
     Tables added to projects are cached to disk, allowing to make efficient use
     of memory, regardless of their size.  See the Project object for more information
     on adding tables to projects.
     
     The columns (field definitions) are required to be named and to have types.
     Fields are specified as a sequence of (name, type, format).  The name
     can be any string starting with a letter and then any combination
     of letters and numbers.  Column names must be unique.
     The type must be a type object, such as int, float, unicode, DateTime, etc.  
     The format is a mask using special characters; see the set_format() method
     for documentation on the different masks.
     
     When specifying field definitions, the type and format are optional.
     Therefore, a field definition can be described as any of the following:
     
     - name      - If a simple string is passed into the field, it is assumed
                   to be the column name.  The field type defaults to string
                   and no format is used.
     - ( name )  - A string passed in within a sequence is also assumed to be
                   the column name.  The field type defaults ot string and no
                   format is used.
     - ( name, type ) - The column name and type.  No format is used.
     - ( name, type, format ) - Explicitly setting the name, type and format. 
     - ( name, type, format, static_expression, active_expression) - Explicitly setting the 
         name, type, format, expression, and/or active expression.  Since it doesn't make 
         sense for a column to be both a static expression and active expression, one
         of these should be None.  See examples below.
     
     The initial data for the table can be specified as a sequence of sequences,
     or a grid of data.  See below for examples.

     Example 1:
       >>> # creates a table with two columns, defaulting to a string type and no format. 
       >>> data = Table([ 
       ...  id,
       ...  name,
       ... ])
       >>> data.structure().view()
       +--------+------------------+------------+--------+
       | Column |       Type       | Expression | Format |
       +--------+------------------+------------+--------+
       | id     | <type 'unicode'> |    <N>     |  <N>   |
       | name   | <type 'unicode'> |    <N>     |  <N>   |
       +--------+------------------+------------+--------+         

     Example 2:
       >>> # creates a table with two columns
       >>> data = Table([ 
       ...  ( 'id',   int ),
       ...  ( 'name', unicode),
       ... ])
       >>> data.structure().view()
       +--------+------------------+------------+--------+
       | Column |       Type       | Expression | Format |
       +--------+------------------+------------+--------+
       | id     | <type 'int'>     |    <N>     |  <N>   |
       | name   | <type 'unicode'> |    <N>     |  <N>   |
       +--------+------------------+------------+--------+         
       
     Example 3:
       >>> # creates a table with two columns, an initial format on the ID field, and initial data
       >>> data = Table([ 
       ...   ( 'id',    number,    '#.#0' ),
       ...   ( 'name',  unicode        ),
       ... ],[
       ...   [ 1.253, 'Danny'    ],
       ...   [ 2,     'Vijay'    ],
       ...   [ 3,     'Dongsong' ],
       ...   [ 4,     'Sally'    ],
       ... ])
       >>> data.structure().view()
       +--------+------------------+------------+--------+
       | Column |       Type       | Expression | Format |
       +--------+------------------+------------+--------+
       | id     | <type 'number'>  |    <N>     |  #.#0  |
       | name   | <type 'unicode'> |    <N>     |  <N>   |
       +--------+------------------+------------+--------+         
     
     Example 4:
       >>> # creates a table with two columns (using shortcut notation)
       >>> # since types are not specified, both columns are typed as unicode
       >>> data = Table(['id', 'name'])
       >>> data.structure().view()
       +--------+------------------+------------+--------+
       | Column |       Type       | Expression | Format |
       +--------+------------------+------------+--------+
       | id     | <type 'unicode'> |    <N>     |  <N>   |
       | name   | <type 'unicode'> |    <N>     |  <N>   |
       +--------+------------------+------------+--------+
       
     Example 5:
       >>> # creates a table with three columns (using another shortcut notation)
       >>> data = Table(3)
       >>> data.structure().view()
       +--------+------------------+------------+--------+
       | Column |       Type       | Expression | Format |
       +--------+------------------+------------+--------+
       | col000 | <type 'unicode'> |    <N>     |  <N>   |
       | col001 | <type 'unicode'> |    <N>     |  <N>   |
       | col002 | <type 'unicode'> |    <N>     |  <N>   |
       +--------+------------------+------------+--------+
       
     Example 6:
       >>> # creates a table with an active calculated column. This column will update
       >>> # automatically as other values in the table change
       >>> data = Table([
       >>>   ( 'c1', int, None),
       >>>   ( 'c4', int, None, None, 'c1*3'),
       >>> ])
       >>> data.append(1)
       >>> data.append(2)
       >>> data.view()
       +----+----+
       | c1 | c4 |
       +----+----+
       |  1 |  3 |
       |  2 |  6 |
       +----+----+
       >>> data[0].c1 = 5
       >>> data.view()
       +----+----+
       | c1 | c2 |
       +----+----+
       |  5 | 15 |
       |  2 |  6 |
       +----+----+

     Example 7:
       >>> # creates a table with a static calculated column. Picalo will assign the results
       >>> # of the given expression to the field and will never again update them.
       >>> # This is different than example 6 because the values are static.
       >>> data = Table([
       >>>   ( 'c1', int, None),
       >>>   ( 'c2', int, None, 'c1*3'),
       >>> ], [
       >>>   [ 1 ],
       >>>   [ 2 ],
       >>> ])
       >>> data.view()        
       +----+----+
       | c1 | c4 |
       +----+----+
       |  1 |  3 |
       |  2 |  6 |
       +----+----+
       >>> data.view()
       >>> data[0].c1 = 5
       +----+----+
       | c1 | c2 |
       +----+----+
       |  5 |  3 |
       |  2 |  6 |
       +----+----+
  '''
  TRANSIENT_VARIABLE_NAMES = [ '_listeners', '_indexes', 'changed', 'filterindex', 'filterexpression' ]
  
  def __init__(self, columns=3, data=[]):
    '''Creates a Picalo Table.  Users should not call this method directly.
       Instead, call Project.create_table() or Project.open_table().
    '''
    # check the parameter types
    assert isinstance(columns, (types.IntType, types.LongType, types.ListType, types.TupleType, PersistentList)), 'The columns parameter must be list of (name, type, format).'
    assert isinstance(data, (Table, types.ListType, types.TupleType)), 'The initial data of a table must be a list of lists, such as [ [1, "a"], [2, "b"] ]'
    # set up the class variables
    self._data = BList()  # a very efficient, ZODB-aware list
    self._listeners = []   # listeners to be notified when changes occur to the table (for integration into GUI)
    self._indexes = {}     # indices used by Simple.select_by_record and other functions
    self.readonly = False
    self.changed = False   # whether the data in the table has changed
    self.columns_map_names = PersistentDict()  # index that maps column names to real column numbers
    self.columns_map_virtual = PersistentDict()  # index that maps virtual column numbers to real column numbers
    self.columns = PersistentList()      # the list of Column objects that represent the columns
    self.num_columns = 0          # the number of active columns we have
    self.filterindex = None    
    self.filterexpression = None
    # set up the columns
    if isinstance(columns, (types.IntType, types.LongType)):  # switch to a list if columns is an integer
      columns = [ 'col%03i' % i for i in range(columns) ]
    for i, col in enumerate(columns):
      if isinstance(col, (Column, _ColumnLoader)): 
        self.columns.append(Column(self, i, col.name, col.column_type, col.expression, col.format))
      elif isinstance(col, (types.ListType, types.TupleType)): 
        assert isinstance(col[0], types.StringTypes), 'Column name must be a string in: ' + str(col)
        col = list(col)  # ensure we have a list 
        while len(col) < 5:
          col.append(None)
        self.columns.append(Column(self, i, col[0], col[1], col[4], col[2]))
      elif isinstance(col, types.StringTypes): 
        self.columns.append(Column(self, i, col, unicode))
      else:
        raise AssertionError, 'Invalid (name, type, format) specification: ' + str(col)
    self._calculate_columns_map()

    # add any initial data to the table
    if data:
      self.extend(data)

    # now that we have data, calculate a static expression if we've been asked to
    # the only way this would do anything is if initial data was placed in the table
    for i, col in enumerate(columns):
      if isinstance(col, (types.ListType, types.TupleType)) and not isinstance(col, (Column, _ColumnLoader)) and len(col) >= 4 and col[3]:
        self.columns[i].static_expression = col[3]
        self.replace_column_values(i, col[3])
      
      
  def __setstate__(self, state):
    '''Restores the object from ZODB and initializes transient variables'''
    persistent.Persistent.__setstate__(self, state)
    # restore the transient variables to their defaults
    self._listeners = []
    self._indexes = {}
    self.changed = False
    self.filterindex = None
    self.filterexpression = None
    # we have to access *any* method of Record so ZODB loads the record and column information from disk
    if len(self) > 0:
      len(self[0])
    
    
  def __getstate__(self):
    '''Returns the state of the object for ZODB serialization.  First removes transient variables'''
    c = persistent.Persistent.__getstate__(self)
    for varname in self.TRANSIENT_VARIABLE_NAMES: # remove any variables that are transient
      del c[varname]
    return c
        
      
  def _add_listener(self, listener):
    '''Adds a listener to the table.  Will be notified when data changes occur.
       The listener should be a callable/function of form callback(table).  For
       efficiency reasons and because we don't need it right now,
       the col and row is not reported.'''
    self._remove_listener(listener)  # just in case it's already here
    self._listeners.append(listener)
    
    
  def _remove_listener(self, listener):
    '''Removes a listener from the table.'''
    try:
      while True:  # continue until no more of this listener in our list
        self._listeners.remove(listener)
    except ValueError:  # thrown when the listener not in list
      pass


  def _notify_listeners(self, level=1):
    '''Notifies listeners that we've had a change'''
    # this gets called a lot, so the if statement is used to speed it up
    if len(self._listeners) > 0:
      for listener in self._listeners:
        listener(self, level)


  def _invalidate_indexes(self):
    '''Invalidates the indices already calculated on this table.  This occurs anytime
       data are modified in this table'''
    if len(self._indexes) > 0:
      self._indexes = {}
    if self.filterindex != None:
      self.filterindex = None
      
      
  def is_changed(self):
    '''Returns whether the table has been changed since loading'''
    return self.changed
    
    
  def set_changed(self, changed):
    '''Sets whether the class has been changed since loading.  This is not normally
       called by users.'''
    self.changed = changed

    
  def set_readonly(self, readonly_flag=False):
    '''Sets the read only status of this table.  Tables that are read only cannot
       be modified.  Normally, tables are initially not read only (i.e. can be modified).
       The only exception is tables loaded from databases, which are read only.
       
       @param readonly_flag: True or False, depending upon whether the table should be read only or not.
       @type  readonly_flag: bool
    '''
#    assert self._cursorlen < 0, 'Database relations are read-only by default.  Copy to a Picalo table to be able to modify it.'
    self.readonly = readonly_flag
    self._notify_listeners(level=1)
    

  def is_readonly(self):
    '''Returns whether this table is read only.
       @return:  Whether this table is read only.
       @rtype:   bool
    '''
    return self.readonly
    
    
  def index(self, *col_names):
    '''Returns an index on this table for the given column name(s).  This method
       allows you to find the record indices that match specific keys.  If only
       one column name is specified, the index will have as many records as there
       are unique records in the column.  If multiple columns are specified, the
       index will have as many records as there are unique combinations of the records
       in the columns.
       
       Indices are used throughout Picalo internally and are not normally accessed
       by users.  However, many analyses need to calculate indices directly, and exposing
       this method allows this behavior.
    
       This method can be called repeatedly without affecting performance. If 
       the table data have not been modified since the last time a specific index 
       was asked for, it uses the previously calculated index.
       
       @param col_names:   One or more column names (separated by commas) to calculate the unique index on.
       @type  col_names:   str
    '''
    check_valid_table(self, *col_names)
    cols = tuple(col_names)
    # make sure we have this index
    if not self._indexes.has_key(cols):
      d = {}
      for i in range(len(self)):
        if len(cols) == 1:
          key = self[i][cols[0]]
        else:
          key = tuple( [ self[i][col] for col in cols ] )
        if d.has_key(key):
          d[key].append(i)
        else:
          d[key] = [i]
      self._indexes[cols] = d
    # return it from the cache
    return self._indexes[cols]
    
  
  def find(self, **pairs):
    '''Finds the record indices with given key=record pairs.  This method
       is not normally used directly -- use Simple.select_by_record instead.
       
       This method is different than Simple.select_by_record in that it does not create 
       a new table.  Simple.select_by_record creates a new table consisting of copies of
       all matching records.  In contrast, this method simply returns the record indices 
       of the matching records.  
       
       This method *is* efficient and can be used often.  It calculates 
       indices as needed and should select very fast.
    
       Example:
        >>> table = Table([
        ...  ('col001', int),
        ...  ('col002', int),
        ...  ('col003', unicode),
        ... ],[
        ...  [5,6,'flo'], 
        ...  [3,2,'sally'], 
        ...  [4,6,'dan'], 
        ...  [4,7,'stu'], 
        ...  [4,7,'ben'],
        ...  [4,6,'benny'],
        ... ])
        >>> results = table.find(col001=6, col000=4)
        >>> results
        [2, 5]
  
       @param pairs:   column=record pairings giving the key(s) to select on.
       @type  pairs:   object
       @return:        A list of indices that match the pairs.
       @rtype:         list 
    '''       
    # no need to check type of pairs because self.index will do it
    idx = self.index(*pairs.keys())
    if len(pairs) == 1:
      vals = pairs.values()[0]
    else:
      vals = tuple(pairs.values())
    return idx.get(vals, [])
    
  
  def filter(self, expression=None):
    '''Filters the table with the given expression.  Until the filter is either
       replaced or cleared, only the records matching the filter will be available
       in the table.  All Picalo functions will see only this limited view of the
       table in their analyses.  In other words, it is as if the filtered record is
       not in the table at all until the filter is removed.
       
       Filters are transient.  They do not save with the table and they do not
       carry over if you copy a table.  They are simply temporary filters that you
       can use to restrict Picalo analyses to a few records.
       
       Only one filter can be active at any time.  Setting a new filter will replace
       the existing one.
       
       In creating your expression, use the standard record['col'] notation
       to access individual records in the table.
       
       @param expression: A valid Picalo expression that returns True or False.  If the
                          expression evaluates to Frue, the record is included in the filtered
                          view.  If False, the record is hidden from view.
       @type  expression: str
    '''
    self._invalidate_indexes()   # calls the update filter method
    if expression:
      self.filterexpression = PicaloExpression(expression)
    else:
      self.filterexpression = None
    self._update_filter_index()
      
      
  def clear_filter(self):
    '''Clears any active filter on this table, restoring the view to all
       records in the table'''
    self.filter(None)
    
    
  def is_filtered(self):
    '''Returns True if this table has an active filter'''
    return self.filterexpression != None
    
    
  def get_filter_expression(self):
    '''Returns the filter expression as a PicaloExpression object, or None if no filter is applied.'''
    return self.filterexpression
    
  
  def _update_filter_index(self):
    '''Updates the filter index.'''
    if self.filterexpression:
      newfilterindex = []
      for i in range(self.record_count(respect_filter=False)):
        rec = self.record(i, respect_filter=False)
        val = self.filterexpression.evaluate([{'record':rec, 'recordindex':i}, rec])
        if isinstance(val, error):
          self.clear_filter()
          raise AssertionError, 'Error filtering record ' + str(i) + ': ' + str(val.get_message())
        elif val == True:
          newfilterindex.append(i)
      self.filterindex = newfilterindex
    else:
      self.filterindex = None
    self._notify_listeners(level=2)
    
      
  def _get_filtered_index(self, index):
    '''Returns the filtered index of the given index, if a filter is in place.
       This method is not thread-safe.
    '''
    if self.filterexpression:
      # do we need to recreate the index?
      if self.filterindex == None:
        self._update_filter_index()
      # return the filtered index   
      return self.filterindex[index]
    return index
    
    
  def _calculate_columns_map(self):
    '''Calculates the columns map based upon the current columns.
       This method should not be called externally.
    '''
    self.columns_map_names = PersistentDict()
    self.columns_map_virtual = PersistentDict()
    self.num_columns = 0
    for i in range(len(self.columns)):
      if self.columns[i].virtual_col_index >= 0:
        self.columns_map_names[self.columns[i].name] = i
        self.columns_map_virtual[self.columns[i].virtual_col_index] = i
        self.num_columns += 1
    self._invalidate_indexes()
    
    
  def __copy__(self):
    '''Returns a copy of this table.  Use this method to make a full copy of all data.
       The normal way to copy data (and invoke this metho) is with the [:] syntax.
       
       Example:
        >>> table1 = Table([
        ...  ('col001', int),
        ...  ('col002', int),
        ...  ('col003', unicode),
        ... ],[
        ...  [5,6,'flo'], 
        ...  [3,2,'sally'], 
        ...  [4,6,'dan'], 
        ...  [4,7,'stu'], 
        ...  [4,7,'ben'],
        ...  [4,6,'benny'],
        ... ])
        >>>
        >>> table2 = table1[:]
        >>> # table2 now has the same columns and data as table1, but it is a 
        >>> # new table -- data changes to one don't affect the other.
        >>>
        >>> table3 = table1
        >>> # table3 is now a second name for table1 -- they are the same table.
        >>> # any changes to table3 will show in table1 and vice versa
    
       @return:  A new Table object with the columns and data of this Table.
       @rtype:   returns
    '''
    return Table(self.columns, self)    


  def _populate_record(self, rec, *a, **k):
    '''Populates a record with data.
       Examples:
         - Format 1:  mytable._populate_record(val1, val2)
         - Format 2:  mytable._populate_record([val1, val2])
         - Format 3:  mytable._populate_record(head1=val1, head2=val2)
         - Format 4:  mytable._populate_record({'head1':val1, 'head2':val2})
         - Format 5:  mytable._populate_record({0:val1, 1:val2})
       You cannot mix formats in the same call.
       
       This method is used internall and should not be called by user code.
    '''
    # set the parameters
    if len(k) > 0:  # Format 3
      for key, record in k.items():
        rec[key] = record

    elif len(a) > 0 and isinstance(a[0], (types.ListType, types.TupleType, Record)):  # format 2 above
      for row in a: # in case more than one list was given
        for i in range(self.column_count()):
          try:
            rec[i] = row[i]
          except IndexError:  # we didn't have enough input values for the number of columns, so just leave None
            pass
          
    elif len(a) > 0 and isinstance(a[0], types.DictType):  # formats 4 & 5 above
      for row in a: # in case more than one dict was given
        for key, record in row.items():
          rec[key] = record

    else:   # assume format 1 above
      for i in range(self.column_count()):
        try:
          rec[i] = a[i]
        except IndexError:  # we didn't have enough input values for the number of columns, so just leave None
          pass
    

  ##### COLUMN METHODS #####
    
  def deref_column(self, col):
    '''Dereferences the col name to its index (if it is a name).  For example,
       if the column name "id" is given, it returns the index of this
       column (such as 0, 1, 2, etc.).
       
       The column can be specified as the column index, the column name,
       or even a negative index (from the last column backward).
       
       @param col_name:    The name of the column
       @type  col_name:    str/int
       @return:            The index of the column
       @rtype:             int
    '''
    ###   START OF NEAR DUPLICATE CODE   ###
    # There is duplicate code in Record.__get_item__ and Record.__set_item__.
    # If you change something here, modify both of those locations as well.
    # This method is called so much that the duplicate code speeds things up by several orders.
    
    # if a name, convert to the index
    if not isinstance(col, int):
      if not col in self.columns_map_names:
        raise IndexError('This table has no column named %s' % col)
      col = self.columns_map_names[col]
  
    # the column was referenced as a number
    else:
      origcol = col
      # if a negative index, convert to a positive one
      if col < 0:
        col += self.num_columns

      # ensure that we have enough columns to fulfill the request
      if col >= self.num_columns or col < 0:
        raise IndexError('Column index [%s] is out of range.  The table only has %s columns, referenced with [0] to [%s] or [-1] to [-%s].' % (origcol, self.num_columns, self.num_columns - 1, self.num_columns))

      # deref to the actual column location in the table
      col = self.columns_map_virtual[col]
    
    # return the column number
    return col

    ###   END OF NEAR DUPLICATE CODE   ###  


  def column(self, col):
    '''Returns a single column of the table.  Column records can be read 
       and modified but not deleted.  This is a useful method when
       you want to work with a single column of a table.
       
       The returned Column object is essentially a list of records 
       and can be treated as such.  Any function that takes a list
       can take a Column object.
       
       This method is used often in analyses.
       
       @param col:   The column name to return
       @type  col:   str
       @return:      A Column object representing the specified column of the table.
       @rtype:       Column
    '''
    check_valid_table(self, col)
    return self.columns[self.deref_column(col)]
   
    
  def get_columns(self):
    '''Returns the column objects of this table.  Columns are Column objects, which
       contain the column name, calculated expression (if any), type if set, etc.
       
       Most users should call get_column_names() instead as it only returns
       the names of the columns.  Only call this method if you need to access
       the internal column objects.
    
       @return:     A list of Column objects
       @rtype:      list
    '''
    return [ self.columns[self.columns_map_virtual[i]] for i in range(self.column_count()) ]
    
    
  def get_column_names(self):
    '''Returns the column names of this table.  
       
       @return:     A list of string names of columns
       @rtype:      list
    '''
    return [ self.columns[self.columns_map_virtual[i]].name for i in range(self.column_count()) ]
    
    
  def column_count(self):
    '''Retrieves the number of columns in a table.  Note that since
       Picalo lists are zero-based, you access individual columns
       starting with 0.  
       
       So although column_count() may report 3 columns, you access
       them via table.column(0), table.column(1), and table.column(2).
       
       However, using column names rather than direct indices is easier
       and more readable.  table['colname'] returns the given column.
    
       @return:     The number columns in the table
       @rtype:      int
    '''
    return self.num_columns
    
  
  def set_name(self, col, name):
    '''Changes the name of an existing column.  The column name must be a
       valid Picalo name and must be unique to other column names in the table.'''
    self.column(col).set_name(name)
    
    
  def set_type(self, col, col_type=None, format=None, expression=None):
    '''Sets the type of a column.   The type must be a valid <type> object,
       such as int, float, str, unicode, DateTime, etc.  All records in this
       column will be converted to this new type.
       
       The format is an optional format to be used for printing the record
       and showing the record in the Pialo GUI.
       
       @param col:          The column name or index to set the type of
       @type  col:          str
       @param col_type:     The new type of this column.
       @type  col_type:     type
       @param format:       A Picalo expression that evaluates to a string
       @type  format:       str
       @param expression:   A Picalo expression that calculates this column.
    '''
    check_valid_table(self, col)
    return self.column(col).set_type(col_type, format, expression)


  def set_format(self, col, format=None):
    '''Sets the format of this column.  The format is used for printing the record 
       and showing the record in the Picalo GUI.
       
       The format should be a Picalo expression that evaluates to a string.  Use the
       'record' variable for the record of the current cell.
       
       Note that this is not an input mask.  It doesn't affect the internal record of 
       the field records.  It only affects how it is displayed on the screen.
       
       Example:
         # shows the current record in uppercase
         table.set_format('Salary', "record.upper()")
       
       @param col:     The column name or index to set the type of
       @type  col:     str
       @param format:  A Picalo expression that evaluates to a string
       @type  format:  str
    '''
    check_valid_table(self, col)
    return self.column(col).set_format(format)

  
  def _insert_column_(self, index, coldef, records=None, expression=None):
    '''Internal method to inesrt a column once the Column object is created'''
    assert not self.is_readonly(), 'This table is set as read-only and cannot be modified.'
    assert isinstance(index, (types.IntType, types.StringType, types.UnicodeType)), 'Invalid column index: ' + str(index)
    if isinstance(index, types.IntType):
      assert index <= self.column_count() and index >= 0, 'Invalid column index: ' + str(index)
    assert isinstance(records, (types.NoneType, types.ListType, types.TupleType, Record, Table)), 'Please specify the new column records as a list.'
    # if the records variable is a table, use the first column of the table
    if isinstance(records, Table):
      records = records.column(0)

    # adjust the virtual_col_index numbers and then add to the columns list
    for c in self.columns:
      if c.virtual_col_index >= index:
        c.virtual_col_index += 1
    coldef.virtual_col_index = index
    self.columns.append(coldef)
    self._calculate_columns_map()
    
    # calculate the expression if we have one
    if expression:  # this is a static expression; an active one would have been placed in coldef
      pe = PicaloExpression(expression)
      coldef.static_expression = expression
      try:
        for i, rec in enumerate(self):
          show_progress('Calculating static expression in column...', float(i) / len(self))
          rec[coldef.name] = pe.evaluate([{'record': rec, 'recordindex': i}, rec])
      finally:
        clear_progress()      

    # set the data in the table if we were given data records
    if records:
      try:
        for i, rec in enumerate(self):
          show_progress('Adding data to new column...', float(i) / len(self))
          if i < len(records):
            val = records[i]
            if coldef.column_type:
              try:
                val = coldef.column_type(val)
              except Exception, e:
                val = error(e)
            rec[coldef.name] = val
      finally:
        clear_progress()      

    # update the table maps and indices
    self._notify_listeners(level=2)
    self.set_changed(True)
    return coldef
    
    
  def replace_column_values(self, column, expression):
    '''Replaces the given column with values calculated from the given expression.
       The previous values in this column are permanently deleted.
       
       This is similar to append_calculated_static(), except it modifies an existing
       column instead of adding a new column.
       
       Example 1:
         # replaces the values in the amount column with the number 10,000
         table.replace_column_values('amount', 10000)
         
       Example 2:
         # doubles the values in the amount column
         table.replace_column_values('amount', 'amount * 2')
      
       Example 3:
         # sets the values in the initials column with the first letter of each record's name
         table.replace_column_values('initials', 'fname[:1] + mname[:1] + lname[:1]')

       @param column:  The column name or index to replace the values in
       @type  column:  str
       @param format:  A Picalo expression used to set the values of the cell
       @type  format:  str
    '''
    assert not self.is_readonly(), 'This table is set as read-only and cannot be modified.'
    assert isinstance(column, (types.IntType, types.StringType, types.UnicodeType)), 'Invalid column index: ' + str(index)
    # dereference to the actual column index
    coldef = self.column(column)
    coldef.static_expression = expression
    # go through the records one by one and change them
    pe = PicaloExpression(expression)
    try:
      for i, rec in enumerate(self):
        show_progress('Replacing values...', float(i) / len(self))
        rec[column] = pe.evaluate([{'record': rec, 'recordindex': i}, rec])
    finally:
      clear_progress()      
    
    
  def append_column(self, name, column_type, records=None):
    '''Adds a new column to the table, optionally setting records of the new cells.

       @param name:        The new column name
       @type  name:        str
       @param column_type: The new column type (int, float, DateTime, unicode, str, etc)
       @type  column_type: type
       @param records:     A list of records to place into the cells of the new column (if a full Table, the first column is used)
       @type  records:     list, Column, or Table
       @return:            The new column object.
       @rtype:             Column
    '''
    return self._insert_column_(self.column_count(), Column(self, -1, name, column_type=column_type), records)

    
  def insert_column(self, index, name, column_type, records=None):
    '''Inserts a new column in the table at the given index location.

       @param name:        The new column name
       @type  name:        str
       @param column_type: The new column type (int, float, DateTime, unicode, str, etc)
       @type  column_type: type
       @param records:     A list of records to place into the cells of the new column (if a full Table, the first column is used)
       @type  records:     list, Column, or Table
       @return:            The new column object.
       @rtype:             Column
    '''
    return self._insert_column_(index, Column(self, -1, name, column_type=column_type), records)

    
  def append_calculated(self, name, column_type, expression):
    '''Adds a new, calculated column with records given by expression.
       Calculated columns act as regular columns in all ways.
       Their records are 'active' meaning their records change when the result
       of the expression.  In other words, they are recalculated each time they
       are used rather than being stored statically.  This is similar to the way
       Excel functions always reflect the most updated data records.
       
       Example: 
         >>> table = Table([('id', int)], [[1],[2],[4]])
         >>> table.append_calculated('plusone', "col000+1")
         >>> table.view()
         +--------+---------+
         | col000 | plusone |
         +--------+---------+
         |      1 |       2 |
         |      2 |       3 |
         |      4 |       5 |
         +--------+---------+
       
       @param name:        The new column name
       @type  name:        str
       @param column_type: The new column type (int, float, DateTime, unicode, str, etc)
       @type  column_type: type
       @param expression:  An expression that returns the record of the new field.  As shown in the example, use rec to denote the current record being evaluated.
       @type  expression:  str
       @return:            The new column object.
       @rtype:             Column
    '''
    return self.insert_calculated(self.column_count(), name, column_type, expression)
    
    
  def insert_calculated(self, index, name, column_type, expression):
    '''Inserts a new, calculated column with records given by expression at the given index location.
       Calculated columns act as regular columns in all ways.
       Their records are 'active' meaning their records change when the result
       of the expression.  In other words, they are recalculated each time they
       are used rather than being stored statically.  This is similar to the way
       Excel functions always reflect the most updated data records.
       
       Example: 
         >>> table = Table([('id', int)], [[1],[2],[4]])
         >>> table.insert_calculated(0, 'plusone', "col000+1")
         >>> table.view()
         +---------+--------+
         | plusone | col000 |
         +---------+--------+
         |       2 |      1 |
         |       3 |      2 |
         |       5 |      4 |
         +---------+--------+

       @param index:       The index location of the new column.  Previous column indices are incremented one to make room for the new column.
       @type  index:       int
       @param name:        The new column name
       @type  name:        str
       @param column_type: The new column type (int, float, DateTime, unicode, str, etc)
       @type  column_type: type
       @param expression:  An expression that returns the record of the new field.  As shown in the example, use rec to denote the current record being evaluated.
       @type  expression:  str
       @return:            The new column object.
       @rtype:             Column
    '''
    return self._insert_column_(index, Column(self, -1, name, column_type, expression=expression))
  
  
  def append_calculated_static(self, name, column_type, expression):
    '''Adds a new, calculated column with records given by expression.
       The records are calculated immediately using expression, and then they are static.
       In other words, this method calculates a new, regular column.  The records
       are not 'active' in the sense that append_calculated() columns are active.
       When this method returns, the new column is the same as any other, non-calculated
       column.
       
       Example: 
         >>> table = Table([('id', int)], [[1],[2],[4]])
         >>> table.append_calculated('plusone', int, "col000+1")
         >>> table.view()
         +--------+---------+
         | col000 | plusone |
         +--------+---------+
         |      1 |       2 |
         |      2 |       3 |
         |      4 |       5 |
         +--------+---------+
       
       @param name:        The new column name
       @type  name:        str
       @param column_type: The type of the new column (str, Date, int, long, etc.)
       @type  column_type: type
       @param expression:  An expression that returns the record of the new field.  As shown in the example, use rec to denote the current record being evaluated.
       @type  expression:  str
       @return:            The new column object.
       @rtype:             Column
    '''
    return self.insert_calculated_static(self.column_count(), name, column_type, expression)
    
    
  def insert_calculated_static(self, index, name, column_type, expression):
    '''Inserts a new, calculated column with records given by expression at the given index location.
       The records are calculated immediately using expression, and then they are static.
       In other words, this method calculates a new, regular column.  The records
       are not 'active' in the sense that append_calculated() columns are active.
       When this method returns, the new column is the same as any other, non-calculated
       column.

       Example: 
         >>> table = Table([('id', int)], [[1],[2],[4]])
         >>> table.append_calculated('plusone', int, "col000 + 1")
         >>> table.view()
         +--------+---------+
         | col000 | plusone |
         +--------+---------+
         |      1 |       2 |
         |      2 |       3 |
         |      4 |       5 |
         +--------+---------+
       
       @param index:       The index location of the new column.  Previous column indices are incremented one to make room for the new column.
       @type  index:       int
       @param name:        The new column name
       @type  name:        str
       @param column_type: The type of the new column (str, Date, int, long, etc.)
       @type  column_type: type
       @param expression:  An expression that returns the record of the new field.  As shown in the example, use rec to denote the current record being evaluated.
       @type  expression:  str
       @return:            The new column object.
       @rtype:             Column
    '''
    return self._insert_column_(index, Column(self, -1, name, column_type), expression=expression)


  def move_column(self, column, new_index):
    '''Moves a column to another location in the table.  A column
       can be moved in front of other columns or behind other columns
       with this method.  
       
       The column parameter is the name of the column to be moved,
       the index of the column to be moved, or the column object itself.
       
       The new_index parameter is the new index for this column.  This
       can be seen as the insertion point, or the column the moved column
       will be placed in front of.  It can be specified as a column index,
       a column name, or a column object.
       
       @param column: The name, index, or column object to be moved.
       @type  column: int/str/Column
       @param new_index: The name, index, or column object that the column will be placed before.
       @type  new_index: int/str/Column
    '''
    # this is not the fastest algorithm, but it's simple and still doesn't take much time
    coldef = self.column(column)
    if new_index != self.column_count():  # if it equals column count, we want to go to the end of the table
      new_index = self.column(new_index).virtual_col_index
    colnames = self.get_column_names()
    del colnames[coldef.virtual_col_index]
    if new_index > coldef.virtual_col_index:
      colnames.insert(new_index-1, coldef.name)
    else:
      colnames.insert(new_index, coldef.name)

    # now that we have the names in the right order, just call reorder_columns
    self.reorder_columns(colnames)
    
    
  def reorder_columns(self, columns):
    '''Reorders the columns according to the given list.  This is an alternative
       to move_column.  If you know the exact order you want the columns in, use
       this method to explicitly set them.
       
       The columns parameter is a list giving the new order.  Its items can
       be current column indices, names, or column objects.
       
       @param columns: A list giving the new column order (use column names, not indices).
       @type  columns: list
    '''
    # check the parameters
    assert isinstance(columns, (types.ListType, types.TupleType)), 'The columns parameter must be a list describing the new column order.'
    assert len(dict([ (self.deref_column(idx), idx) for idx in columns ])) == len(columns), 'You cannot specify a column twice in the columns parameter.'
    for col in columns:
      self.column(col)  # checks for valid name and range if int

    # first deactivate all the columns
    for coldef in self.columns:  
      coldef.virtual_col_index = -1
    
    # activate them in the order the user wants
    for i, col in enumerate(columns):
      self.column(col).virtual_col_index = i

    # notify people that we've changed
    self._calculate_columns_map()
    self.set_changed(True)
    self._notify_listeners(level=2)


  def delete_column(self, *columns):
    '''Removes a column from the table and discards the records.  
       Remaining column indices are decremented to reflect the new 
       table structure.  Column names (columns) are not modified.
       
       Example: 
         >>> table.delete_column('id')          # deletes the column named 'id' from table
         >>> table.delete_column('id', 'age')   # deletes the columns named 'id' and 'age' from table
       
       @param columns:    The name or index of the column to be removed.  The parameter can be specified more than once.
       @type  columns:    str or list
    '''
    assert not self.is_readonly(), 'This table is set as read-only and cannot be modified.'
    check_valid_table(self, columns)
    
    # go through and delete each name in the list
    indices = [ self.column(col).virtual_col_index for col in columns ]
    colnames = self.get_column_names()
    for name in [ self.column(c).name for c in columns ]:
      del colnames[colnames.index(name)]

    # reorder with the new names
    self.reorder_columns(colnames)
      
    
  ##### CONTAINER METHODS ####
  
  
  def record(self, index, respect_filter=True):
    '''Retrieves the record at the given index.  This is one of the most-used
       methods in the Picalo toolkit as it gives you access to records.
       
       In keeping with most computer languages, Picalo indices are always
       zero-based.  This may require a slight adjustment for some users,
       but it makes mathematical calculations much easier and has other
       implications. This means that record 1 is table[0], record 2 is 
       table[1], and so forth.
       
       Note that the shortcut way to access this method is the simple [n]
       notation, as in table[1] to access the second record.  table.record()
       is rarely called as the shortcut is preferred instead.
    
       For advanced users: Index can also be a slice, as in table[2:5] to 
       return a new Picalo table including only records 2, 3, and 4.  See 
       the Python documentation for more information on slices.
       
       The method respects any filters on the table by default.  This can be
       overridden to ignore the filter.
        
       Example:
         >>> table = Table([('id', int)], [[1],[2],[3],[4]])
         >>> table2 = table[1]
         >>> # table2 is now a Record object pointing at [2]
       
       Example 2:
         >>> table = Table([('id', int)], [[1],[2],[3],[4]])
         >>> print table[1]['col000']
         2
       
       @param index:   The zero-based index of the record to pull.
       @type  index:   int
       @return:        A Picalo Record object, which allows access to members via column name.
       @rtype:         Record
    '''
    assert isinstance(index, (types.IntType, types.LongType, types.SliceType)), 'Please specify the index of the record as an integer.'
    # if a slice, return a new picalo table
    # list would otherwise return a new list of Record objects
    if isinstance(index, types.SliceType):
      newtable = Table(self.get_columns())
      start, step, stop = index.start, index.step, index.stop
      if start == None: start = 0
      if step == None: step = 1
      if stop == None: stop = self.record_count(respect_filter)
      stop = min(stop, self.record_count(respect_filter))
      for i in range(start, stop, step):
        newtable.append(self.record(i, respect_filter))
      return newtable
    # if a negative number, convert it to positive
    if index < 0:
      index = self.record_count(respect_filter) + index
    # otherwise, get the record
    if respect_filter:
      index = self._get_filtered_index(index)
    return self._data[index]
    
  
  def __getitem__(self, index):
    '''Retrieves a record or a full column of the table.  If the given index is a column name,
       the column object is returned.  If the given index is an integer, the given 
       row object is returned.
    
       @param index:   The zero-based index of the record to pull OR the string name of the column to pull.
       @type  index:   int or str
       @return:        A Picalo Record object or Picalo Column object from this table
       @rtype:         Record or Column
    '''
    if isinstance(index, types.StringTypes):  # a column name
      return self.column(index)
    else:  # a record index
      return self.record(index)
    
  
  def record_count(self, respect_filter=True):
    '''Returns the number of records in this table.  The method
       respects any active filters on the table by default.

       @return:  The number of records in the table.
       @rtype:   int
    '''
    # do we need to recreate the index?
    if respect_filter and self.filterexpression:
      if self.filterindex == None:
        self._update_filter_index()
    if self.filterindex != None and respect_filter:
      return len(self.filterindex)
    return len(self._data)

    
  def __len__(self):
    '''Return the number of records in the table.  The method respects
       any active filters on the table.
    
       @return:  The number of records in the table.
       @rtype:   int
    '''
    return self.record_count()
    
    
  def __setitem__(self, index, record):
    '''Replaces an existing Record with the given data.  Use = to set items.
    
       Example:
         >>> table = Table([('id', int)], [[1,2], [3,4]])
         >>> table[1] = [5,6]
         >>> table.view()
         +--------+--------+
         | col000 | col001 |
         +--------+--------+
         |      1 |      2 |
         |      5 |      6 |
         +--------+--------+
       
       @param index: The index of the record where data will be replaced.
       @type  index: int
       @param record: A Record object, a list, or a Python sequence containing data for the 
       @type  record: Record/list/tuple of columns for the record records.
    '''
    assert not self.is_readonly(), 'This table is set as read-only and cannot be modified.'
    assert isinstance(index, (types.IntType, types.LongType, types.SliceType)), 'Please specify the index of the record as an integer.'
    for i in range(min(len(record), self.column_count())):
      self[index][i] = record[i]
    self._invalidate_indexes()
    self.set_changed(True)
    self._notify_listeners(level=1)
    
    
  def __iter__(self):
    '''Returns an interator to the Records in this Table.  This is normally achieved through:
         >>> for record in mytable:
         >>>   # do something with each record object
           
       @return:    An iterator to this Table.
       @rtype:     iterator
    '''
    return TableIterator(self)
    
    
  def iterator(self, respect_filter=True):
    '''Returns an iterator to the Records in thistTable.  This is normally achieved through:
         >>> for record in mytable:
         >>>   # do something with each record object
         
       This method is provided to allow you to ignore the filter if you want.  The 
       regular iterator syntax (for record in mytable) always respects any active filters.
           
       @return:    An iterator to this Table.
       @rtype:     iterator
    '''
    return TableIterator(self, respect_filter)
    
    
  def __delitem__(self, index):
    '''Removes a record from the table.  The proper use to call this method
       is 'del table[i]' where i is the record number to remove.  You can also
       specify columns to delete with 'del table["colname"]' where colname
       is the column name you want to delete.'''
    assert not self.is_readonly(), 'This table is set as read-only and cannot be modified.'
    if isinstance(index, types.StringTypes):  # for column deletion
      return self.delete_column(index)
    assert isinstance(index, (types.IntType, types.LongType, types.SliceType)), 'Please specify the index of the record as an integer.'
    # call recursively if a slice type
    if isinstance(index, types.SliceType):
      start, stop, step = index.start, index.stop, index.step
      if stop >= 0:  # if stop is left off, it goes to maxint
        stop = min(stop, self.record_count())
      if not step:
        step = 1
      lowest = min(start, stop)
      for i in range(start, stop, step):
        del self[lowest]
      return
    # a regular deletion
    index = self._get_filtered_index(index)
    del self._data[index]
    self._invalidate_indexes()
    self.set_changed(True)
    self._notify_listeners(level=2)
    
    
    
  ######  LIST METHODS  ######
  
  def append(self, *a, **k):
    '''Inserts a new record at the end of this table.  This is the primary
       way to add new data to a table.  If you need to insert a row in the middle
       of a table, use the insert() method.
    
       Records can be added in any of the following ways:

       Format 1:
         - newrec = mytable3.append()
         - newrec['ID'] = 4
         - newrec['Name'] = 'Homer'
         - newrec['Salary'] = 15000

       Format 2:
         - mytable.append(4, 'Homer', 1500)

       Format 3:
         - mytable3.append([4, 'Homer', 1500])

       Format 4:
         - mytable3.append({'ID':5, 'Name':'Marge', 'Salary': 275000})

       Format 5:
         - mytable3.append({0:5, 1:'Marge', 2: 275000})

       Format 6:
         - mytable3.append(ID=5, Name='Krusty', Salary=50000)

       You cannot mix formats in the same call.
       
       @return:   The new record object (that was appended to the end of the table)
       @rtype:    Record
    '''
    assert not self.is_readonly(), 'This table is set as read-only and cannot be modified.'
    # append the record and adjust our ending index
    rec = Record(self)
    self._data.append(rec)
    self._populate_record(rec, *a, **k)
    # update indices
    self.set_changed(True)
    self._invalidate_indexes()
    self._notify_listeners(level=2)
    return rec
    
    
  def insert(self, *a, **k):
    '''Inserts a new record at the given index location.  The first parameter *must*
       be the index location to insert the record.  The remaining parameters are the
       same as the append() method.  Possible formats are (assuming you want to place
       the new record in the second row and push all existing records down one):

       Format 1:
         - newrec = mytable3.insert(2) # insert before row 2
         - newrec['ID'] = 4
         - newrec['Name'] = 'Homer'
         - newrec['Salary'] = 15000

       Format 2:
         - mytable.insert(2, 4, 'Homer', 1500) # insert before row 2

       Format 3:
         - mytable3.insert(2, [4, 'Homer', 1500]) # insert before row 2

       Format 4:
         - mytable3.insert(2, {'ID':5, 'Name':'Marge', 'Salary': 275000}) # insert before row 2

       Format 5:
         - mytable3.insert(2, {0:5, 1:'Marge', 2: 275000}) # insert before row 2

       Format 6:
         - mytable3.insert(2, ID=5, Name='Krusty', Salary=50000) # insert before row 2

       You cannot mix formats in the same call.
       
       @return:  The new record object (that was inserted to the end of the table)
       @rtype:   returns
    '''
    assert not self.is_readonly(), 'This table is set as read-only and cannot be modified.'
    rec = Record(self)
    index = a[0]
    if index < 0:
      index = len(self) + index
    if index < 0:
      raise IndexError, 'list index out of range'
    index = self._get_filtered_index(index)
    self._data.insert(index, rec)
    self._populate_record(rec, *a[1:], **k)
    # update indices    
    self.set_changed(True)
    self._invalidate_indexes()
    self._notify_listeners(level=2)
    return rec
    
    
  def extend(self, table):
    '''Appends the records in the given table to the end of this table.
       The two tables must have the same number of columns to be merged. 

       Example:
         >>> mytable3.extend(mytable2)  # appends mytable2 to the end of mytable3
         
       @param table:  The records of the specified table will be added to this table.
       @type  table:  Table
    '''
    assert not self.is_readonly(), 'This table is set as read-only and cannot be modified.'
    if not isinstance(table, Table):
      assert isinstance(table, (Table, types.TupleType, types.ListType)), 'Invalid table type given to extend.'
      for item in table:
        assert isinstance(item, (Record, types.TupleType, types.ListType, types.DictType)), 'Invalid table type given to extend.'
    try:
      totalrecs = float(len(table))
      for i, rec in enumerate(table):
        show_progress('Initializing records...', float(i) / totalrecs)
        self.append(rec)
    finally:
      clear_progress()
    self.set_changed(True)
    self._invalidate_indexes()
    self._notify_listeners(level=2)
    
      
  ######  NUMERIC METHODS  ########
  
  def __iadd__(self, other):
    '''This is essentially the extend method.  I included a += method directly
       to increase efficiency (so no intermediate table needs to be created)
    '''
    check_valid_table(other)
    self.extend(other)
    return self
  
  
  def __add__(self, other):
    '''Adds two tables together.
       To be added together, two tables should have the same number of columns
       and be compatible with one another.  
       The new table includes the records of the first table followed by the
       records of the second table.  The column columns (and column calculations)
       of the first table are carried to the new table.
       The two source tables are not modified.
       
       Stated differently, this method copies the first table and appends the second 
       table's records to it.
       
       Some users might expect this method to add individual cells together, similar to
       matrix addition.  This is *not* the case.  Instead, the new table includes all
       records from both tables.
       
       Example:
         >>> t1 = Table(2, [[1,1], [2,2]])
         >>> t2 = Table(2, [[3,3], [4,4]])
         >>> t3 = t1 + t2
         >>> t3.view()
         +--------+--------+
         | col000 | col001 |
         +--------+--------+
         |      1 |      1 |
         |      2 |      2 |
         |      3 |      3 |
         |      4 |      4 |
         +--------+--------+
       
       @param other:  A Table to be added to this one.
       @type  other:  Table
       @return:       A new table with records from both tables
       @rtype:        Table
    '''
    if not isinstance(other, Table):
      assert isinstance(other, (types.TupleType, types.ListType)), 'Invalid table type given to extend.'
      for item in other:
        assert isinstance(item, (types.TupleType, types.ListType)), 'Invalid table type given to extend.'
    table = Table(self.get_columns(), self) # adds the records of the first table
    table.extend(other)
    return table
    
    
  def __sub__(self, other):
    raise NotImplementedError, 'Table subtraction is not allowed.'


  def __eq__(self, other):
    '''Returns whether this table is equal to another table (or list of lists).  Only the records
       of the table are compared -- not the column names or column definitions.'''
    if isinstance(other, (Table, types.ListType, types.TupleType)):
      if len(self) == len(other):
        for i in range(len(self)):
          if self[i] != other[i]:
            return False
        return True
    return False
    
  def __ne__(self, other):
    '''Returns whether this table is not equal to another table (or list of lists). Only the records
       of the table are compared -- not the column names or column definitions.'''
    return not self.__eq__(other)
    
    
  def sort(self, cmp=None, key=None, reverse=False):
    '''Sorts this table with optional arguments.  This is the standard Python sort method that
       iterable objects have.  See the Python sorting HowTo for more information on sorting the
       Pythonic way.
       
       Most users will probably prefer the Simple.sort(table, ...) function for sorting.  See
       the Simple.sort documentation for more information on this method of sorting.
       
       Example 1:
         >>> t1 = Table(2, [[2,2], [1,1], [5,5], [0,0]])
         >>> t1.view()
         +--------+--------+
         | col000 | col001 |
         +--------+--------+
         | 2      | 2      |
         | 1      | 1      |
         | 5      | 5      |
         | 0      | 0      |
         +--------+--------+
         >>> t1.sort(key=lambda rec: rec.col000)  # to sort by the 'col000' column
         >>> t1.view()
         +--------+--------+
         | col000 | col001 |
         +--------+--------+
         | 0      | 0      |
         | 1      | 1      |
         | 2      | 2      |
         | 5      | 5      |
         +--------+--------+
         
       Example 2:
         >>> # this example uses Simple.sort to achieve the same result as Example 1
         >>> t1 = Table(2, [[2,2], [1,1], [5,5], [0,0]])
         >>> t1.view()
         +--------+--------+
         | col000 | col001 |
         +--------+--------+
         | 2      | 2      |
         | 1      | 1      |
         | 5      | 5      |
         | 0      | 0      |
         +--------+--------+
         >>> Simple.sort(t1, True, 'col001') # table name, ascending, sort col 1, sort col 2, ...
         >>> t1.view()         
         +--------+--------+
         | col000 | col001 |
         +--------+--------+
         | 0      | 0      |
         | 1      | 1      |
         | 2      | 2      |
         | 5      | 5      |
         +--------+--------+
   
       @param cmp:     An optional function that compares two items
       @type  cmp:     function
       @param key:     A function that takes a single item and returns a version of it for use in sorting.
       @type  key:     function
       @param reverse: Whether to sort in reverse
       @type  reverse: bool
    '''
    assert not self.is_readonly(), 'This table is set as read-only and cannot be modified.'
    self._data.sort(cmp, key, reverse)
    self.set_changed(True)


  def structure(self):
    '''Returns the structure of this table, including column names, input and output types,
       and general statistics.
    
       @return:   A Picalo table describing the structure of this table.
       @rtype:    Table
    '''
    struct = Table([('Column', unicode), ('Type', str), ('Expression', str), ('Format', unicode)])
    for col in self.columns:
      rec = struct.append()
      rec['Column'] = col.name
      rec['Type'] = str(col.column_type)
      rec['Expression'] = col.expression and col.expression.expression or None
      rec['Format'] = col.format
    return struct

   
  ######  PRINTING METHODS  #######
  
  def prettyprint(self, fp=None, center_columns=True, space_before=' ', space_after=' ', col_separator_char='|', row_separator_char='-', join_char='+', line_ending=os.linesep, none='<N>', encoding='utf-8', respect_filter=True):
    '''Pretty prints the table to the given fp.  Note that the preferred way to print
       a table is to call "table.view()", which opens the table in the Picalo
       GUI if possible, or uses view() if in console mode.  In other words,
       you should normally use view() rather than this method.
       
       @param fp:                  An open file pointer object.  If None, defaults to standard output stream.
       @type  fp:                  file
       @param center_columns:      Whether to center columns or not.
       @type  center_columns:      bool
       @param space_before:        An optional spacing between the leading column separator and the field record.
       @type  space_before:        str
       @param space_after:         An optional spacing between the field and the trailing column separator.
       @type  space_after:         str
       @param col_separator_char:  An optional column separator character to use in the printout.
       @type  col_separator_char:  str
       @param row_separator_char:  An optional row separator character to use in the printout.
       @type  row_separator_char:  str
       @param join_char:           An optional character to use when joining rows and columns.
       @type  join_char:           str
       @param line_ending:         An optional line ending character(s) to use.
       @type  line_ending:         str
       @param none:                The record to print when cells are set to the special None record.
       @type  none:                str
       @param encoding:     The unicode encoding to write with.  This should be a value from the codecs module.  If None, the encoding is guessed to utf_8, utf-16, utf-16-be, or utf-16-le
       @type  encoding:     str
    '''
    assert isinstance(space_before, types.StringTypes), 'The space_before parameter must be a string.'
    assert isinstance(space_after, types.StringTypes), 'The space_after parameter must be a string.'
    assert isinstance(col_separator_char, types.StringTypes), 'The col_separator_char parameter must be a string.'
    assert isinstance(row_separator_char, types.StringTypes), 'The row_separator_char parameter must be a string.'
    assert isinstance(join_char, types.StringTypes), 'The join_char parameter must be a string.'
    assert isinstance(line_ending, types.StringTypes), 'The line_ending parameter must be a string.'
    assert isinstance(none, types.StringTypes), 'The none parameter must be a string.'
    
    # Note to programmer: this method is used by save_fixed below, so be sure to maintain compatability
    # I set fp=None above because if fp=sys.stdout, it sets that at class creation time
    # and can't be redirected to the shell
    if fp == None:
      fp = sys.stdout 
      
    # encode for unicode output
    fp = codecs.EncodedFile(fp, 'utf_8', encoding)
    
    # calculate the maximum width of each column
    widths = [ 0 for i in range(self.column_count()) ]
    for record in self.iterator(respect_filter):
      for i in range(self.column_count()):
        field = record[i]
        if field == None:
          field = make_unicode(none)
        else:
          field = make_unicode(self.column(i).format_value(field))
        widths[i] = max(widths[i], len(field))
    for i in range(self.column_count()):
      widths[i] = max(widths[i], len(str(self.column(i).name)))
        
    # create the separator line
    linesep = make_unicode(join_char)
    for w in widths:
      linesep += make_unicode(row_separator_char)
      for ch in range(w):
        linesep += make_unicode(row_separator_char)
      linesep += make_unicode(row_separator_char) + make_unicode(join_char)
    linesep += make_unicode(line_ending)
        
    # print the headings
    if linesep != line_ending:
      fp.write(linesep)
    line = make_unicode(col_separator_char)
    for i in range(self.column_count()):
      if center_columns:
        line += make_unicode(space_before) + make_unicode(self.column(i).name).center(widths[i]) + make_unicode(space_after) + make_unicode(col_separator_char)
      else:
        line += make_unicode(space_before) + make_unicode(self.column(i).name).ljust(widths[i]) + make_unicode(space_after) + make_unicode(col_separator_char)
    line += make_unicode(line_ending)
    fp.write(line)
    if linesep != line_ending:
      fp.write(linesep)
        
    # print the rows
    for record in self.iterator(respect_filter):
      line = make_unicode(col_separator_char)
      for i in range(self.column_count()):
        field = record[i]
        if field == None:
          line += make_unicode(space_before) + make_unicode(none).center(widths[i]) + make_unicode(space_after) + make_unicode(col_separator_char)
        elif isinstance(field, (types.IntType, types.LongType, types.FloatType)):  # rjustification
          line += make_unicode(space_before) + make_unicode(self.column(i).format_value(field)).rjust(widths[i]) + make_unicode(space_after) + make_unicode(col_separator_char)
        else:
          line += make_unicode(space_before) + make_unicode(self.column(i).format_value(field)).ljust(widths[i]) + make_unicode(space_after) + make_unicode(col_separator_char)
      line += make_unicode(line_ending)
      fp.write(line.encode(encoding))
    
    # print the bottom table border
    if linesep != line_ending:
      fp.write(linesep)
    
    fp.flush()
    
    
  def view(self):
    '''Opens a spreadsheet-view of the table if Picalo is being run in GUI mode.
       If Picalo is being run in console mode, it redirects to prettyprint().
       This is the preferred way of viewing the data in a table.
    '''
    view(self)
    
    
  def __repr__(self):
    '''For debugging.  Use view() for a formatted printout.
       
       @return:   The number of rows and columns in the table.  
       @rtype:    str
    '''
    return '<Table: ' + str(len(self)) + ' rows x ' + str(self.column_count()) + ' cols>'
    
        
  ######  EXPORTING METHODS #######


  def save_delimited(self, filename, delimiter=',', qualifier='"', line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False):
    '''Saves this table to a delimited text file.  This method
       allows the specification of different types of delimiters
       and qualifiers.
       
       This method is for advanced users.  Most users should call
       save_tsv, save_csv, or save_fixed to save using one of the 
       accepted text formats.  See these methods for more information.
    
       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param delimiter:    A field delimiter character, defaults to a comma (,)
       @type  delimiter:    str
       @param qualifier:    A qualifier to use when delimiters exist in field records, defaults to a double quote (")
       @type  qualifier:    str
       @param line_ending:  A line ending to separate rows with, defaults to os.linesep (\n on Unix, \r\n on Windows)
       @type  line_ending:  str
       @param none:         An parameter specifying what to write for cells that have the None value, defaults to an empty string ('')
       @type  none:         str
       @param encoding:     The unicode encoding to write with.  This should be a value from the codecs module, defaults to 'utf-8'.
       @type  encoding:     str
       @param respect_filter Whether to save the entire file or only those rows available through any current filter.
       @type  respect_filter bool
    '''
    save_delimited(self, filename, delimiter=',', qualifier='"', line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False)
    
    
  def save_csv(self, filename, line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False):
    '''Saves this table to a Comma Separated Values (CSV) text file.
       CSV is an industry-standard way of transferring data between
       applications.  This is the preferred way of exporting data from
       Picalo.
       
       Note that although this is the preferred export method, it has some
       limitations.  These are limitations of the format rather than
       limitations of Picalo:
        - No type information is saved to the file.  All data is essentially turned into strings.
        - Be sure to use the correct encoding if using international languages.
        - Different standards for CSV exist (that's the nice thing about standards :).  This export uses the Microsoft version.
       
       Note that Microsoft Office seems to like CSV files better than TSV files.
    
       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param line_ending:  An optional line ending to separate rows with
       @type  line_ending:  str
       @param none:         An optional parameter specifying what to write for cells that have the None record.
       @type  none:         str
       @param encoding:     The unicode encoding to use for international or special characters.  For example, Microsoft applications like to use special characters for double quotes rather than the standard characters.  Unicode (the default) handles these nicely.
       @type  encoding:     str
       @param respect_filter Whether to save the entire file or only those rows available through any current filter.
       @type  respect_filter bool
    '''
    save_csv(self, filename, line_ending=line_ending, none=none, encoding=encoding, respect_filter=respect_filter)
    
    
  def save_tsv(self, filename, line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False):
    '''Saves this table to a Tab Separated Values (TSV) text file.
       TSV is an industry-standard way of transferring data between
       applications.
       
       Note that although this is the preferred export method, it has some
       limitations.  These are limitations of the format rather than
       limitations of Picalo:
        - No type information is saved to the file.  All data is essentially turned into strings.
        - Be sure to use the correct encoding if using international languages.
        - Different standards for TSV exist (that's the nice thing about standards :).  This export uses the Microsoft version.
       
       Note that Microsoft Office seems to like CSV files better than TSV files.
    
       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param line_ending:  An optional line ending to separate rows with
       @type  line_ending:  str
       @param none:         An optional parameter specifying what to write for cells that have the None record.
       @type  none:         str
       @param encoding:     The unicode encoding to use for international or special characters.  For example, Microsoft applications like to use special characters for double quotes rather than the standard characters.  Unicode (the default) handles these nicely.
       @type  encoding:     str
    '''
    save_tsv(self, filename, line_ending=line_ending, none=none, encoding=encoding, respect_filter=respect_filter)
   
   
  def save_fixed(self, filename, line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False):
    '''Saves this table to a fixed width text file.  Fixed width
       files pad column records with extra spaces so they are easier
       to read.
       
       You should normally prefer CSV and TSV export formats to fixed
       as they have less limitations.  Fixed format was widely used
       in the early days of computers, and some servers still use the
       format.
    
       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param line_ending:  An optional line ending to separate rows with
       @type  line_ending:  str
       @param none:         An optional parameter specifying what to write for cells that have the None record.
       @type  none:         str
       @param respect_filter Whether to save the entire file or only those rows available through any current filter.
       @type  respect_filter bool
    '''
    save_fixed(self, filename, line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False)
    
    
  def save_xml(self, filename, line_ending=os.linesep, indent='\t', compact=False, none='', encoding='utf-8', respect_filter=False):
    '''Saves this table to an XML file using a pre-defined schema.  If you need
       to save to a different schema, use the xml.dom.minidom class directly.
       
       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param line_ending:  An optional line ending to separate rows with (when compact is False)
       @type  line_ending:  str
       @param indent:       The character(s) to use for indenting (when compact is False)
       @type  indent:       str
       @param compact:      Whether to compact the XML or make it "pretty" with whitespace
       @type  compact:      bool
       @param none:         An optional parameter specifying what to write for cells that have the None record.
       @type  none:         str
       @param respect_filter Whether to save the entire file or only those rows available through any current filter.
       @type  respect_filter bool
    '''    
    save_xml(self, filename, line_ending=os.linesep, indent='\t', compact=False, none='', encoding='utf-8', respect_filter=False)
    
   
  def save_excel(self, filename, none='', respect_filter=False):
    '''Saves this table to a Microsoft Excel 97+ file.
       
       @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
       @type  filename:     str
       @param none:         An optional parameter specifying what to write for cells that have the None record.
       @type  none:         str
       @param respect_filter Whether to save the entire file or only those rows available through any current filter.
       @type  respect_filter bool
    '''    
    save_excel(self, filename, none='', respect_filter=False)



###############################################
###   View code for tables

def view(table):
  '''Opens a spreadsheet-view of the table if Picalo is being run in GUI mode.
     If Picalo is being run in console mode, it redirects to prettyprint().
     This is the preferred way of viewing the data in a table.
  '''
  # NOTE: this method is also used by Database.Query
  from picalo import mainframe
  if mainframe != None:
    # try to figure out the variable name of this table by inspecting the call stack
    f = inspect.currentframe().f_back.f_back
    locals = f.f_locals
    for name in f.f_code.co_names:
      if locals.has_key(name) and locals[name] == table:
        mainframe.openTable(name)
        return
  # if we get here, either we're in console mode or we couldn't find the variable name
  table.prettyprint()


  
##################################################################
###   An iterator for tables that respects the filters on them.
      
def TableIterator(table, respect_filter=True):     
  '''Returns a generator object to iterate over a table'''
  index = 0
  numrows = table.record_count(respect_filter)
  while index < numrows:
    yield table.record(index, respect_filter)
    index += 1       
      


  

      
###################################################################################################
###   Eporting and importing routines
###   CSV, TSV, XML, Excel (.xls), etc.
      
def load_delimited(filename, header_row=True, delimiter=',', qualifier='"', none='', encoding=None, errors='replace'):
  '''Loads records from the given delimited text file.  This function
     allows the specification of delimiters and qualifiers.  Most users
     should use the load_csv, load_tsv, and load_fixed functions as they
     provide easier access to text files.  Use this function only if
     you have a specially-formatted text file.
  
     @param filename:     A file name or a file pointer to an open file.
     @type  filename:     str
     @param header_row:   Whether the first line of the file includes the column names.  Most delimited text files do this.
     @type  header_row:   str
     @param delimiter:    An optional field delimiter character
     @type  delimiter:    str
     @param qualifier:    An optional qualifier to use when delimiters exist in field records
     @type  qualifier:    str
     @param none:         An optional argument that specifies the record to assign Python's None type to (for blank cells).
     @type  none:         str
     @param encoding:     The unicode encoding to write with.  This should be a value from the codecs module.  If None, the encoding is guessed to utf-8, utf-16, utf-16-be, or utf-16-le
     @type  encoding:     str
     @param errors:       How to handle characters that cannot be handled.  Options are 'replace', 'strict', and 'ignore'.  See 'codecs' in the Python documentation for more information.
     @type  errors:       str
     @return:             A new Table object, or None if the file is empty.
     @rtype:              Table
  '''
  assert isinstance(delimiter, types.StringTypes), 'The delimiter parameter must be a string.'
  assert isinstance(qualifier, (types.NoneType, types.StringTypes)), 'The qualifier parameter must be a string.'
  assert isinstance(none, (types.StringTypes, types.NoneType)), 'The none parameter must be a string.'

  try:
    show_progress('Loading file...', 0.0)
    # open the file if needed
    fileopened = False
    filesize = 0
    if type(filename) in types.StringTypes:
      filesize = os.stat(filename).st_size
      filename = open(filename, 'rb')
      fileopened = True

    # create the reader
    reader = picalo.lib.delimitedtext.DelimitedReader(filename, delimiter, qualifier, encoding, errors)
  
    # create the table
    if header_row:
      try:
        headings = reader.next()
        table = Table(make_unique_colnames(ensure_valid_variables(headings)))
      except StopIteration:
        return Table()
    else:
      table = Table(1)  # start with one column
      
    # read the rows of the table
    for row in reader:
      if filesize > 0:
        show_progress('Loading file...', float(filename.tell()) / float(filesize))
      else:
        show_progress('Loading file (progress not available)...', 0.0)
      while len(row) > len(table.columns):  # do we have more fields than columns in this record?
        table.append_column(ensure_unique_colname(table, 'unnamed'), unicode)
      table.append(row)  

    # finally, return the table 
    return table
  finally:
    clear_progress()
    
  
def load_csv(filename, header_row=True, none='', encoding=None, errors='replace'):
  '''Loads records from a Comma Separated Values (CSV) file.
     Among the various CSV flavors in the world, this function
     uses the Microsoft version.
  
     @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
     @type  filename:     str
     @param header_row:   Whether the first line of the file includes the column names.  Most delimited text files do this.
     @type  header_row:   str
     @param none:         An optional argument that specifies the record to assign Python's None type to (for blank cells).
     @type  none:         str
     @param encoding:     The unicode encoding to write with.  This should be a value from the codecs module.  If None, the encoding is guessed to utf-8, utf-16, utf-16-be, or utf-16-le
     @type  encoding:     str
     @param errors:       How to handle characters that cannot be handled.  Options are 'replace', 'strict', and 'ignore'.  See 'codecs' in the Python documentation for more information.
     @type  errors:       str
     @return:             A new Table object, or None if the file is empty.
     @rtype:              Table
  '''
  return load_delimited(filename, header_row=header_row, delimiter=',', qualifier='"', none=none, encoding=encoding, errors=errors)
  

def load_tsv(filename, header_row=True, none='', encoding=None, errors='replace'):
  '''Loads records from a Excel Tab Separated Values (TSV) file.
     Among the various TSV flavors in the world, this function
     uses the Microsoft version.
  
     @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
     @type  filename:     str
     @param header_row:   Whether the first line of the file includes the column names.  Most delimited text files do this.
     @type  header_row:   str
     @param none:         An optional argument that specifies the record to assign Python's None type to (for blank cells).
     @type  none:         str
     @param encoding:     The unicode encoding to write with.  This should be a value from the codecs module.  If None, the encoding is guessed to utf-8, utf-16, utf-16-be, or utf-16-le
     @type  encoding:     str
     @param errors:       How to handle characters that cannot be handled.  Options are 'replace', 'strict', and 'ignore'.  See 'codecs' in the Python documentation for more information.
     @type  errors:       str
     @return:             A new Table object, or None if the file is empty.
     @rtype:              Table
  '''
  return load_delimited(filename, header_row=header_row, delimiter='\t', qualifier='"', none=none, encoding=encoding, errors=errors)
 
 
def save_delimited(table, filename, delimiter=',', qualifier='"', line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False):
  '''Saves this table to a delimited text file.  This method
     allows the specification of different types of delimiters
     and qualifiers.
     
     This method is for advanced users.  Most users should call
     save_tsv, save_csv, or save_fixed to save using one of the 
     accepted text formats.  See these methods for more information.
  
     @param table:        The table to save
     @type  table:        Table
     @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
     @type  filename:     str
     @param delimiter:    A field delimiter character, defaults to a comma (,)
     @type  delimiter:    str
     @param qualifier:    A qualifier to use when delimiters exist in field records, defaults to a double quote (")
     @type  qualifier:    str
     @param line_ending:  A line ending to separate rows with, defaults to os.linesep (\n on Unix, \r\n on Windows)
     @type  line_ending:  str
     @param none:         An parameter specifying what to write for cells that have the None value, defaults to an empty string ('')
     @type  none:         str
     @param encoding:     The unicode encoding to write with.  This should be a value from the codecs module, defaults to 'utf-8'.
     @type  encoding:     str
     @param respect_filter Whether to save the entire file or only those rows available through any current filter.
     @type  respect_filter bool
  '''
  assert isinstance(table, Table), 'The table must be a Picalo table.'
  assert isinstance(delimiter, types.StringTypes), 'The delimiter parameter must be a string.'
  assert isinstance(qualifier, types.StringTypes), 'The qualifier parameter must be a string.'
  assert isinstance(line_ending, types.StringTypes), 'The line_ending parameter must be a string.'
  assert isinstance(none, types.StringTypes), 'The none parameter must be a string.'
  assert isinstance(encoding, types.StringTypes), 'The encoding parameter must be a string.'
  
  try:
    # open the file if we need to
    fileopened = False
    if type(filename) in types.StringTypes:
      filename = open(filename, 'wb')
      fileopened = True
      
    # set up a delimited writer
    writer = picalo.lib.delimitedtext.DelimitedWriter(filename, delimiter, qualifier, line_ending, none, encoding)
    
    # write the headers
    writer.writerow(table.get_column_names())
    
    # write the rows of the table
    numrecs = table.record_count(respect_filter)
    for rowindex, row in enumerate(table.iterator(respect_filter)):
      show_progress('Saving file...', float(rowindex) / float(table.record_count(respect_filter=respect_filter)))
      row2 = list(row) # convert to a list
      # change None to whatever was asked for and encode for unicode since csv doesn't support it
      for i in range(len(row2)):
        if row2[i] == None:
          row2[i] = none
        else:
          row2[i] = table.columns[i].format_value(row2[i])
      # write the row
      writer.writerow(row2, lastrow=(rowindex == numrecs-1))
    
    # flush everything through
    filename.flush()
    
    # close the filename if we opened it
    if fileopened:
      filename.close()
  finally:
    clear_progress()


def save_csv(table, filename, line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False):
  '''Saves this table to a Comma Separated Values (CSV) text file.
     CSV is an industry-standard way of transferring data between
     applications.  This is the preferred way of exporting data from
     Picalo.

     Note that although this is the preferred export method, it has some
     limitations.  These are limitations of the format rather than
     limitations of Picalo:
      - No type information is saved to the file.  All data is essentially turned into strings.
      - Be sure to use the correct encoding if using international languages.
      - Different standards for CSV exist (that's the nice thing about standards :).  This export uses the Microsoft version.

     Note that Microsoft Office seems to like CSV files better than TSV files.

     @param table:        The table to save
     @type  table:        Table
     @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
     @type  filename:     str
     @param line_ending:  An optional line ending to separate rows with
     @type  line_ending:  str
     @param none:         An optional parameter specifying what to write for cells that have the None record.
     @type  none:         str
     @param encoding:     The unicode encoding to use for international or special characters.  For example, Microsoft applications like to use special characters for double quotes rather than the standard characters.  Unicode (the default) handles these nicely.
     @type  encoding:     str
     @param respect_filter Whether to save the entire file or only those rows available through any current filter.
     @type  respect_filter bool
  '''
  save_delimited(table, filename, delimiter=',', qualifier='"', line_ending=line_ending, none=none, encoding=encoding, respect_filter=respect_filter)


def save_tsv(table, filename, line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False):
  '''Saves this table to a Tab Separated Values (TSV) text file.
     TSV is an industry-standard way of transferring data between
     applications.

     Note that although this is the preferred export method, it has some
     limitations.  These are limitations of the format rather than
     limitations of Picalo:
      - No type information is saved to the file.  All data is essentially turned into strings.
      - Be sure to use the correct encoding if using international languages.
      - Different standards for TSV exist (that's the nice thing about standards :).  This export uses the Microsoft version.

     Note that Microsoft Office seems to like CSV files better than TSV files.

     @param table:        The table to save
     @type  table:        Table
     @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
     @type  filename:     str
     @param line_ending:  An optional line ending to separate rows with
     @type  line_ending:  str
     @param none:         An optional parameter specifying what to write for cells that have the None record.
     @type  none:         str
     @param encoding:     The unicode encoding to use for international or special characters.  For example, Microsoft applications like to use special characters for double quotes rather than the standard characters.  Unicode (the default) handles these nicely.
     @type  encoding:     str
  '''
  save_delimited(table, filename, delimiter='\t', qualifier='"', line_ending=line_ending, none=none, encoding=encoding, respect_filter=respect_filter)



 
 
###################################################
###   Fixed format loading and saving 
 
  

# patterned after Lars Tiede python code for bom detection
bommap={ 
  (0x00, 0x00, 0xFE, 0xFF): "utf_32_be",        
  (0xFF, 0xFE, 0x00, 0x00): "utf_32_le",
  (0xEF, 0xBB, 0xBF):       "utf_8"    ,
  (0xFE, 0xFF):             "utf_16_be", 
  (0xFF, 0xFE):             "utf_16_le", 
}

def load_fixed(filename, column_positions=[], header_row=True, none='', encoding=None, errors='replace', line_separators=True): 
  '''Loads records from a fixed width file.  Fixed width files
     pad columns with extra spaces so they are easy to read with
     a text editor.
     
     Example 1:

     Suppose test-fixed.txt contains the following data:
      id name  salary 
       1 Marge 50000  
       2 Dan    4500

     >>> # load the data into a new table, specifying column positions as 0-2, 2-8, and 8-15
     >>> data2 = load_fixed('test-fixed.txt', [0,2,8,15])
     >>> data2.view()     
     +----+-------+--------+
     | id |  name | salary |
     +----+-------+--------+
     | 1  | Marge | 50000  |
     | 2  | Dan   | 4500   |
     +----+-------+--------+
     The next step is to convert column types as approriate.
     
     
     Example 2:
     
     Suppose test-fixed.txt contains the following data:
      idname salary01Marge05000002Dan  004500
     Note that in this file, the lines are not separated by hard returns.  This is common in mainframe
     data files like EBCDIC-encoded files.
     
     >>> # load the data into a new table, specifying column positions as 0-2, 2-7, and 7-13
     >>> data2 = load_fixed('test-fixed.txt', [0,2,7,13], line_separators=False)
     >>> data2.view()
     +----+-------+--------+
     | id |  name | salary |
     +----+-------+--------+
     | 01 | Marge | 050000 |
     | 02 | Dan   | 004500 |
     +----+-------+--------+
     The next step is to convert column types as approriate.
     
     
     @param filename:          A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
     @type  filename:          str
     @param column_positions:  A list of integers specifying where to split columns.  The first item should always be 0 (the first character in each line).  The last item should be the ending column position.
     @type  column_positions:  list
     @param header_row:        An optional parameter to specify whether the first row of the file contains field headers.  Defaults to True.
     @type  header_row:        bool
     @param none:              An optional argument that specifies the record to assign Python's None type to (for blank cells).
     @type  none:              str
     @param encoding:          The unicode encoding to read with.  This should be a value from the codecs module.  If None, the encoding is guessed to utf_8, utf-16, utf-16-be, or utf-16-le
     @type  encoding:          str
     @param errors:            How to handle characters that cannot be handled.  Options are 'replace', 'strict', and 'ignore'.  See 'codecs' in the Python documentation for more information.
     @type  errors:            str
     @param line_separators:   Whether the lines in the file are separated by hard returns.  See the examples above for more information.
     @type  line_separators:   bool
     @return:                  A new Table object, or None if the file is empty.
     @rtype:                   Table
  '''
  assert isinstance(column_positions, (types.ListType, types.TupleType)), 'The column_positions must be a list of positions.'
  for item in column_positions:
    assert isinstance(item, (types.IntType, types.LongType)), 'Invalid column position: ' + str(item)
  assert isinstance(none, (types.StringTypes, types.NoneType)), 'The none parameter must be a string.'
  try:
    # ensure we have an open file
    fileopened = 0
    filesize = 0
    filepath = filename  
    if type(filename) in types.StringTypes:
      filesize = os.stat(filename).st_size
      filename = open(filename, 'rb')
      fileopened = 1
    
    # read the first few bytes of the file, then reset to start of file
    startpos = filename.tell()
    byte1, byte2, byte3, byte4 = tuple(map(ord, filename.read(4)))
    filename.seek(startpos) 
    # see if we need to skip over the BOM (Byte Order Mark) characters
    if bommap.get((byte1, byte2, byte3, byte4)):
      filename.read(4)
    elif bommap.get((byte1, byte2, byte3)):
      filename.read(3)
    elif bommap.get((byte1, byte2)):
      filename.read(2)
    # set up the encoding correctly
    if encoding != None:  
      filename = codecs.EncodedFile(filename, 'utf_8', encoding, errors)
    else:
      bomDetection = bommap.get((byte1, byte2, byte3, byte4)) or bommap.get((byte1, byte2, byte3)) or bommap.get((byte1, byte2))
      if bomDetection == None:
        encoding = 'utf_8'
        filename = codecs.EncodedFile(filename, 'utf_8', 'utf_8', errors) # default to utf_8
      else:
        encoding = bomDetection
        filename = codecs.EncodedFile(filename, 'utf_8', bomDetection, errors)
    
    # read the file
    positions = [ (column_positions[i], column_positions[i+1]) for i in range(len(column_positions)-1) ]
    recsize = column_positions[-1]
    table = None
    if line_separators:
      line = unicode(filename.readline(), encoding)
    else:
      line = unicode(filename.read(recsize), encoding)
    while line:
      if filesize > 0:
        show_progress('Loading file...', float(filename.tell()) / float(filesize))
  
      # do this twice since windows uses \r\n
      if line[-1:] in (u'\n', u'\r'):
        line = line[:-1]
      if line[-1:] in (u'\n', u'\r'):
        line = line[:-1]
      
      # split the line into its records
      if len(positions) == 0:
        rec = [ line ]
      else:
        rec = [ line[pos1: pos2].strip() for pos1, pos2 in positions ]
      
      # add to the table in the appropriate place
      if table == None:
        if header_row: 
          uniqueheaders = make_unique_colnames(ensure_valid_variables([ name.strip() for name in rec ]))
          table = Table([ (header, unicode) for header in uniqueheaders ])
        else:
          table = Table([ ('col%03d' % i, unicode) for i in range(len(rec)) ])
          table.append(rec)
      else:
        # replace the none values
        for i in range(len(rec)):
          if rec[i] == none:
            rec[i] = None
        table.append(rec)

      # read the next line
      if line_separators:
        line = unicode(filename.readline(), encoding)
      else:
        line = unicode(filename.read(recsize), encoding)
  
    if fileopened:
      filename.close()
  
    return table

  finally:
    clear_progress()
    
    
def save_fixed(table, filename, line_ending=os.linesep, none='', encoding='utf-8', respect_filter=False):
  '''Saves this table to a fixed width text file.  Fixed width
     files pad column records with extra spaces so they are easier
     to read.

     You should normally prefer CSV and TSV export formats to fixed
     as they have less limitations.  Fixed format was widely used
     in the early days of computers, and some servers still use the
     format.

     >>> # create a table and save it     
     >>> data = Table([
     >>>   ( 'id',     int     ),
     >>>   ( 'name',   unicode ),
     >>>   ( 'salary', number  ),
     >>> ])
     >>> data.append(1, 'Marge', 50000)
     >>> data.append(2, 'Danny', 45000)
     >>> data.save_fixed('test-fixed.txt')
     
     Test-fixed.txt now contains the following data:
      id name  salary 
       1 Marge 50000  
       2 Danny 45000

     @param table:        The table to save
     @type  table:        Table
     @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
     @type  filename:     str
     @param line_ending:  An optional line ending to separate rows with
     @type  line_ending:  str
     @param none:         An optional parameter specifying what to write for cells that have the None record.
     @type  none:         str
     @param respect_filter Whether to save the entire file or only those rows available through any current filter.
     @type  respect_filter bool
  '''
  assert isinstance(table, Table), 'The table must be a Picalo table.'
  try:
    show_progress('Saving (ongoing progress not available)...', 0)
    fileopened = 0
    if type(filename) in types.StringTypes:
      filename = open(filename, 'w')
      fileopened = 1
    table.prettyprint(filename, space_before='', space_after=' ',center_columns=0, col_separator_char='', row_separator_char='', join_char='', line_ending=line_ending, none=none, encoding=encoding, respect_filter=respect_filter)
    if fileopened:
      filename.close()
  finally:
    clear_progress()




###################################################
###   Classic Excel loading and saving
    
def load_excel(filename, worksheet_name=None, topleft_cell=None, bottomright_cell=None, header_row=True, none=''): 
  '''Loads the given Excel file.  Values are taken from the first sheet in the workbook.

     @param filename:         The file name.  It must be the string name and not a file pointer (the library doesn't support it).
     @type  filename:         str
     @param worksheet_name:   The name of the worksheet that contains the data (only one worksheet can be imported).  Defaults to the first sheet in the workbook.
     @type  worksheet_name:   str
     @param topleft_cell:     The top-left cell of the block to import.  It should be in spreadsheet format, such as "A2" or "C5".  Defaults to the first cell with data.
     @type  topleft_cell:     str
     @param bottomright_cell: The bottom-right cell of the block to import.  It should be in spreadsheet format, such as "A2" or "C5".  Defaults to the last cell with data.
     @type  bottomright_cell: str
     @param header_row:       Whether the first line of the file includes the column names.  Defaults to True.
     @type  header_row:       str
     @param none:             An optional argument that specifies the record to assign Python's None type to (for blank cells).
     @type  none:             str
     @return:                 A new Table object, or None if the file is empty.
     @rtype:                  Table
  '''
  assert isinstance(filename, types.StringTypes), 'Invalid filename: ' + str(filename)
  assert os.path.exists(filename), 'The given filename does not exist.'
  assert isinstance(worksheet_name, (types.StringTypes, types.NoneType)), 'You must specify a valid worksheet name.'
  assert isinstance(topleft_cell, (types.StringTypes, types.NoneType)), 'The top-left cell must be a spreadsheet location like A2 or C5.'
  assert isinstance(bottomright_cell, (types.StringTypes, types.NoneType)), 'The bottom-right cell must be a spreadsheet location like A2 or C5.'
  assert isinstance(none, (types.StringTypes, types.NoneType)), 'The none parameter must be a string.'
  assert not (topleft_cell == None and bottomright_cell != None), 'You must specify a topleft_cell record if you specify a bottomright_cell record.'
  try:
    workbook = picalo.lib.pyExcelerator.parse_xls(filename)  # returns a list of (sheetname, sheet) objects
    assert len(workbook) > 0, 'No worksheets were found in this Excel file.'

    # find the right sheet
    sheet = None
    for name, sht in workbook:
      if name == worksheet_name or not worksheet_name:
        sheet = sht
        break
    assert sheet != None, 'The sheet name, %s, does not appear to be in the file.' % (worksheet_name, )
    assert len(sheet) > 0, 'This sheet name you want to import appears to be empty.'

    # parse the top left and bottom right cell locations
    rows = {}
    keys = sheet.keys()
    if topleft_cell:
      topleft_cell = topleft_cell.upper()
      topleft_match = re.search('^([A-Z]+)([0-9]+)$', topleft_cell)
      assert topleft_match, 'The top-left cell must be a spreadsheet location like A2 or C5.'
      firstrow = int(topleft_match.group(2)) - 1
      firstcol = 0
      multiplier = 0
      for ch in topleft_match.group(1)[::-1]:
        firstcol += (pow(26, multiplier) * (ord(ch) - ord('A') + 1))
        multiplier += 1
      firstcol -= 1  # since the importer is zero based
    else:
      firstrow, firstcol = keys[0]
      for r, c in keys:
        firstrow = min(firstrow, r)
        firstcol = min(firstcol, c)
    
    if bottomright_cell:
      bottomright_cell = bottomright_cell.upper()
      bottomright_match = re.search('^([A-Z]+)([0-9]+)$', bottomright_cell)
      assert bottomright_match, 'The bottomright cell must be a spreadsheet location like A2 or C5.'
      lastrow = int(bottomright_match.group(2)) - 1
      lastcol = 0
      multiplier = 0
      for ch in bottomright_match.group(1)[::-1]:
        lastcol += (pow(26, multiplier) * (ord(ch) - ord('A') + 1))
        multiplier += 1
      lastcol -= 1  # since the importer is zero based
      assert firstcol < lastcol, 'The first column must be less than the last column in the block'
      assert firstrow < lastrow, 'The first row must be less than the last row in the block'
    else:
      lastcol = firstcol
      lastrow = firstrow
      maxcol = firstcol
      for r, c in keys:
        firstrow = min(firstrow, r)
        firstcol = min(firstcol, c)
        maxcol = max(maxcol, c)
      while True:
        rowhasdata = False
        for c in range(firstcol, maxcol+1):
          if sheet.has_key((lastrow+1, c,)):
            lastcol = max(lastcol, c)
            rowhasdata = True
        if not rowhasdata:
          break
        lastrow += 1

    # load the data from the dictionary
    table = None
    for r in range(firstrow, lastrow+1):
      # load the data for this row
      row = []
      for c in range(firstcol, lastcol+1):
        if sheet.has_key((r, c,)):
          row.append(sheet[(r,c,)])
        else:
          row.append(None)
      if table == None and header_row:
        table = Table([ header for header in make_unique_colnames(ensure_valid_variables(row)) ])
      elif table == None:
        table = Table([ 'col%03d' % i for i in range(lastcol-firstcol+1)])
        table.append(row)
      else:
        table.append(row)
    return table
  finally:
    clear_progress()
  



def save_excel(table, filename, none='', respect_filter=False):
  '''Saves this table to a Microsoft Excel 97+ file.

     @param table:        The table to save
     @type  table:        Table
     @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
     @type  filename:     str
     @param none:         An optional parameter specifying what to write for cells that have the None record.
     @type  none:         str
     @param respect_filter Whether to save the entire file or only those rows available through any current filter.
     @type  respect_filter bool
  '''    
  assert isinstance(table, Table), 'The table must be a Picalo table.'
  assert isinstance(none, types.StringTypes), 'The none parameter must be a string.'
  try:
    # open the file if we need to
    fileopened = 0
    if type(filename) in types.StringTypes:
      filename = open(filename, 'wb')
      fileopened = 1

    # set up the workbook
    workbook = picalo.lib.pyExcelerator.Workbook()
    sheet1 = workbook.add_sheet('Sheet1')

    # add the column headings (with a little style :)
    alignment = picalo.lib.pyExcelerator.Alignment()
    alignment.horz = alignment.HORZ_CENTER
    font = picalo.lib.pyExcelerator.Font()
    font.bold = True
    style = picalo.lib.pyExcelerator.XFStyle()
    style.font = font
    style.alignment = alignment
    for c in range(len(table.columns)):
      sheet1.write(0, c, table.columns[c].name, style)

    # add the rows of the table
    style = picalo.lib.pyExcelerator.XFStyle()
    style.alignment = alignment
    for r, rec in enumerate(table):
      for c in range(len(table.columns)):
        if rec[c] == None:
          sheet1.write(r+1, c, none, style)
        else:
          sheet1.write(r+1, c, table.columns[c].format_value(rec[c]))

    # save it - the default implmeentation doesn't allow me to save to a stream, so I override one of its methods
    class XlsDoc(picalo.lib.pyExcelerator.CompoundDoc.XlsDoc):
      def save(table, f, stream):
        # 1. Align stream on 0x1000 boundary (and therefore on sector boundary)
        padding = '\x00' * (0x1000 - (len(stream) % 0x1000))
        table.book_stream_len = len(stream) + len(padding)
        table.__build_directory()
        table.__build_sat()
        table.__build_header()
        f.write(table.header)
        f.write(table.packed_MSAT_1st)
        f.write(stream)
        f.write(padding)
        f.write(table.packed_MSAT_2nd)
        f.write(table.packed_SAT)
        f.write(table.dir_stream)
    xlsdoc = XlsDoc()
    xlsdoc.save(filename, workbook.get_biff_data())

    # close the filename if we opened it
    if fileopened:
      filename.close()
  finally:
    clear_progress()



#############################################
###   XML Saving

def save_xml(table, filename, line_ending=os.linesep, indent='\t', compact=False, none='', encoding='utf-8', respect_filter=False):
  '''Saves this table to an XML file using a pre-defined schema.  If you need
     to save to a different schema, use the xml.dom.minidom class directly.
     
     @param table:        The table to save
     @type  table:        Table
     @param filename:     A file name or a file pointer to an open file.  Using the file name string directly is suggested since it ensures the file is opened correctly for reading in CSV.
     @type  filename:     str
     @param line_ending:  An optional line ending to separate rows with (when compact is False)
     @type  line_ending:  str
     @param indent:       The character(s) to use for indenting (when compact is False)
     @type  indent:       str
     @param compact:      Whether to compact the XML or make it "pretty" with whitespace
     @type  compact:      bool
     @param none:         An optional parameter specifying what to write for cells that have the None record.
     @type  none:         str
     @param respect_filter Whether to save the entire file or only those rows available through any current filter.
     @type  respect_filter bool
  '''    
  assert isinstance(table, Table), 'The table must be a Picalo table.'
  assert isinstance(line_ending, types.StringTypes), 'The line_ending parameter must be a string.'
  assert isinstance(indent, types.StringTypes), 'The indent parameter must be a string.'
  assert isinstance(none, types.StringTypes), 'The none parameter must be a string.'
  try:
    # open the file if we need to
    fileopened = 0
    if type(filename) in types.StringTypes:
      filename = open(filename, 'w')
      fileopened = 1
    
      # output to xml
      cols = table.get_columns()
      doc = xml.dom.minidom.Document()
      root = doc.appendChild(doc.createElement('table'))
      for i, rec in enumerate(table.iterator(respect_filter)):
        show_progress('Saving...', float(i) / table.record_count(respect_filter=respect_filter))
        row = root.appendChild(doc.createElement('record'))
        for c, col in enumerate(cols):
          cell = row.appendChild(doc.createElement('field'))
          cell.setAttribute('name', col.name)
          cell.setAttribute('type', col.column_type.__name__)
          cell.setAttribute('format', col.format != None and col.format or '')
          field = rec[c]
          if rec[c] == None:
            field = none
          cell.appendChild(doc.createTextNode(str(table.columns[c].format_value(field))))

      if compact:
        filename.write(doc.toxml())
      else:
        filename.write(doc.toprettyxml(indent=indent, newl=line_ending))
  
    # close the filename if we opened it
    if fileopened:
      filename.close()
  finally:
    clear_progress()
  
  
  
  
  
  
  
  
  
  
  
