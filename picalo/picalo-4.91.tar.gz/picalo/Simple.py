#!/usr/bin/python


####################################################################################
#                                                                                  #
# Copyright (c) 2003 Dr. Conan C. Albrecht <conan_albrechtATbyuDOTedu>             #
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
#
# Version 1.00
# Jun 22, 2005: Added the select_records and select_by_value functions
#               Moved the index() method to 
# May 31, 2005: Added the join method
# May 26, 2005: Changed all the lambda stuff over to expressions that go through eval
# Jun 23, 2004: Added the soundex algorithm.
# Jan 14, 2004: Added information about how to sort using Python's built-in sort function
# Dec 12, 2003: Version 1.00.  Refactored the code.  Significant changes, new functions
#                              Moved the previous Sequences.py routines in to Simple.py
#                              Wrote unit testing for refactored code.
# Dec 08, 2003: Version 0.30.  Started this log.
#
#
#
####################################################################################

__doc__ = '''
The Simple module contains base functions that are useful throughout the Picalo package,
such as indexing, sorting, selecting, and matching of tables.
'''

# a listing of the public functions in this module (used by Manual.py)
__functions__ = (
  'col_join',
  'col_left_join',
  'col_right_join',
  'col_match',
  'col_match_same',
  'col_match_diff',
  'compare_records',  
  'custom_match',
  'custom_match_same',
  'custom_match_diff',
  'describe',
  'expression_match',
  'find_duplicates',
  'find_gaps',
  'fuzzysearch',
  'fuzzymatch',
  'fuzzycoljoin',
  'get_unordered',
  'join',
  'left_join',
  'regex_match',
  'right_join',
  'select',
  'select_by_value',
  'select_outliers',
  'select_outliers_z', 
  'select_nonoutliers',
  'select_nonoutliers_z',
  'select_records',
  'soundex',
  'soundexcol',
  'sort',
  'transpose',
  'wildcard_match',
)


import lib.stats
import math, types, re
from picalo import Table, TableList, TableArray, show_progress, clear_progress, check_valid_table
from picalo.base.Column import _ColumnLoader
from picalo.base.Global import run_tablearray, ensure_unique_colname, ensure_unique_list_value, make_unique_colnames, make_valid_variable
from picalo.base.Expression import PicaloExpression


######################################
###   Convenience statistical methods

__descriptives__ = [
    'NumRecords',
    'NumEmpty',
    'NumNone',
    'NumZero',
    'NumText',
    'NumNumeric',
    'Median',
    'Mean',
    'Max',
    'Min',
    'Variance',
    'StdDev',
    'Total',
]    
__dm__ = dict([ [__descriptives__[i], i] for i in range(len(__descriptives__))])
round_descriptives_to = 2

def describe(table, *cols):
  '''Prepares a set of statistical descriptives for the given columns in the given table.
     While these descriptives could be retrieved from the included stats module, this method
     gives quick and easy access to the main statistical measures, such as mean, median, 
     counts, totals, and so forth. The descriptives available are shown in the example below.
    
     If no columns are designated, descriptives are run for every column in the table.  Note
     that this method is not optimized yet, so it might take a while for large tables with
     many columns.
     
     For numeric descriptives like the mean or std deviation, text fields and empty fields
     are ignored.  If no numeric descriptives can be calculated, the field is set to None.
     Since this function is meant to show a descriptive view of a table (and not to provide
     hard statistical values), most fields are rounded off to 2 decimal places for readability.
     
     Example:
      >>> table = Table([
      ...   'Name',
      ...   'Pay',
      ... ],[
      ...   ['Homer',  0],
      ...   ['Marge',  20],
      ...   ['Bart',   None],
      ...   ['Lisa',   152],
      ...   ['Maggie', ''],
      ... ])
      >>> descriptives = Simple.describe(table)
      >>> descriptives.view()
      +-------------+------+---------+
      | Descriptive | Name |   Pay   |
      +-------------+------+---------+
      | NumRecords  |    5 |       5 |
      | NumEmpty    |    0 |       2 |
      | NumZero     |    0 |       1 |
      | NumText     |    5 |       0 |
      | NumNumeric  |    0 |       3 |
      | Median      |      |    20.0 |
      | Mean        |      |   57.33 |
      | Max         |      |   152.0 |
      | Min         |      |     0.0 |
      | Variance    |      | 6821.33 |
      | StdDev      |      |   82.59 |
      | Total       |      |   172.0 |
      +-------------+------+---------+      
       
     @param table:  The table to run descriptives on.
     @type  table:  Table or TableArray
     @param cols:   Zero or more columns to run descriptives on.  If none are specified, all columns are included.
     @return:       A picalo table giving descriptives for the columns.
     @rtype:        Table
  ''' 
  if isinstance(table, TableArray):
    return run_tablearray('Calculating descriptives...', describe, table, *cols)
  check_valid_table(table, *cols)
  try:
    # prepare the descriptives table
    if len(cols) == 0:  # get all columns if none were explicitly asked for
      ncols = table.get_column_names()
    else:
      ncols = []
      for col in cols:  # ensure we have names instead of indices
        ncols.append( table.column(col).name )
    descriptives = Table([('Descriptive', unicode)] + zip(list(ncols), [float for i in ncols]))
    for descriptive in __descriptives__:
      descriptives.append([descriptive])
    # calculate the descriptives for each column
    for counter, col in enumerate(ncols):
      show_progress('Calculating descriptives...', float(counter) / len(ncols))
      # note that I don't use the lib/stats.py file because I can be more efficient
      # and handle errors better here
      numempty = 0
      numnone = 0
      numzero = 0
      numtexttype = 0
      numnumbertype = 0
      maxval = None
      minval = None
      total = 0
      numerics = [] # for median and numnumbertype
      for row in table:
        val = row[col]
        try: 
          if long(val) == float(val):  # decide whether to change to a long or float
            val = long(val)
          else:
            val = float(val)
          numerics.append(val)
          isnumeric = 1
        except:
          isnumeric = 0
        if isnumeric:
          if val == 0:
            numzero += 1
          if maxval == None:
            maxval = val
          else:
            maxval = max(maxval, val)
          if minval == None:
            minval = val
          else:
            minval = min(minval, val)
          total += val
        if val == '':
          numempty += 1
        elif val == None:
          numnone += 1
        elif not isnumeric:
          numtexttype += 1
      numerics.sort()
      descriptives[__dm__['NumRecords']][col] = len(table)
      descriptives[__dm__['NumEmpty']][col] = numempty
      descriptives[__dm__['NumNone']][col] = numnone
      descriptives[__dm__['NumZero']][col] = numzero
      descriptives[__dm__['NumText']][col] = numtexttype
      descriptives[__dm__['NumNumeric']][col] = len(numerics)
      if len(numerics) == 0:  # no numerics
        descriptives[__dm__['Mean']][col] = None
        descriptives[__dm__['Max']][col] = None
        descriptives[__dm__['Min']][col] = None
        descriptives[__dm__['Total']][col] = None
        descriptives[__dm__['Variance']][col] = None
        descriptives[__dm__['StdDev']][col] = None
        descriptives[__dm__['Median']][col] = None
      else: # we have some numerics here
        mean = float(sum(numerics)) / len(numerics)
        descriptives[__dm__['Mean']][col] = round(mean, round_descriptives_to)
        descriptives[__dm__['Max']][col] = round(maxval, round_descriptives_to)
        descriptives[__dm__['Min']][col] = round(minval, round_descriptives_to)
        descriptives[__dm__['Total']][col] = round(total, round_descriptives_to)
        # median
        if len(numerics) == 1:
          descriptives[__dm__['Median']][col] = round(numerics[0], round_descriptives_to)
        elif len(numerics) % 2 == 0:
          descriptives[__dm__['Median']][col] = round((numerics[len(numerics)/2] + numerics[(len(numerics)/2)-1]) / 2.0, round_descriptives_to)
        elif len(numerics) % 2 == 1:
          descriptives[__dm__['Median']][col] = round(numerics[len(numerics)/2], round_descriptives_to)
        # variance, stdev
        if len(numerics) > 1:
          sumsquares = sum([ (val - mean) * (val - mean) for val in numerics])
          variance = sumsquares / (len(numerics) - 1)
          descriptives[__dm__['Variance']][col] = round(variance, round_descriptives_to)
          descriptives[__dm__['StdDev']][col] = round(math.sqrt(variance), round_descriptives_to)
    return descriptives
  finally:
    clear_progress()



######################################
###   Sequential record comparisons  


def compare_records(table, expression):
  '''Runs through a table sequentially and compares each record with the one after it.
     In other words, if table has 4 records, this method compares 0<=>1, 1<=>2, and
     2<=>3.  It runs the given expression for each set and returns the indices of those
     sets that return True.  The expression should always evaluate to True or False.
     
     The expression should evaluate record1 against record2, as in:
     {"record1['id'] == record2['id'] - 1"}
     
     The index of the first record is stored in the results list.  So if 
     the expression compares the third and fourth records and evaluates true, 
     index 3 is stored in the table.

     Example:
     >>> table = Table([('col000', int)], ([8000], [2000], [9000], [10000], [8000]))
     >>> results = Simple.compare_records(table, "record1.col000 < record2.col000")
     >>> results.view()
     +-------------+
     | Row Indices |
     +-------------+
     |           1 |
     |           2 |
     +-------------+
     
     In the above example, the following comparisons are made:
     8000  < 2000  (false)
     2000  < 9000  (true)
     9000  < 10000 (true)
     10000 < 8000  (false0

     @param table:      The table to be analyzed
     @type  table:      Table or TableArray
     @param expression: The expression to compare each record set with
     @type  expression: str
     @return:           A single-column table of indices that the function returned true for
     @rtype:            Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Comparing records...', compare_records, table, expression)
  check_valid_table(table)
  try:
    results = Table([('Row_Indices', int)])
    pe = PicaloExpression(expression)
    for i in range(1, len(table)):
      show_progress('Comparing records...', float(i) / len(table))
      if pe.evaluate([{'record1':table[i-1], 'record1index':i-1, 'record2':table[i], 'record2index':i}, table[i-1], table[i]]):
        results.append([i-1])
    return results
  finally:
    clear_progress()
  
  


##################################
###   Basic table routines

def sort(table, ascending, *cols):
  '''Sorts a table by values in one or more columns.  
  
     Example:
       >>> table = Table([('col000', int), ('col001', int)], ([5,6], [3,2], [4,6]))
       >>> Simple.sort(table, True, 'col000', 'col001')
       >>> table.view()
       +--------+--------+
       | col000 | col001 |
       +--------+--------+
       |      3 |      2 |
       |      4 |      6 |
       |      5 |      6 |
       +--------+--------+       
       
     @param table:     The table to be sorted.
     @type  table:     Table or TableArray
     @param ascending: Sorts ascending when True, descending when False
     @type  ascending: bool
     @param cols:      One or more column names to sort the table by
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Sorting...', sort, table, ascending, *cols)
  check_valid_table(table, *cols)
  if len(cols) == 0:
    raise 'You must supply at least one column name/index'
  # sort the table by comparing two temporary lists from the sort columns
  if ascending:
    table.sort(lambda record1, record2: cmp([ record1[col] for col in cols ], [ record2[col] for col in cols ]))
  else:
    table.sort(lambda record2, record1: cmp([ record1[col] for col in cols ], [ record2[col] for col in cols ]))
  table._notify_listeners(level=1)
  
  
def transpose(table):
  '''Transposes the table, which means the columns and rows are switched.
     A transposed (inverted) table is returned.
     
     Be careful with transposing large tables -- the new table will have
     as many columns as the source table has rows.  Large tables are often
     unmanageable because of the large number of columns they produce.
     
     Since Picalo column names must conform to a specific format and must
     be unique, some changes may be made to the values in the transposition
     process.
     
     Since Picalo cannot guess the new column types, all columns are typed
     as unicode columns.  Use table.set_type to set the types after transposition.
     
     @param   table:    The table to be transposed
     @type    table:    Table
     @return: A new table containing the transposed values
     @rtype:  Table
  '''
  try:
    check_valid_table(table)
    assert len(table) > 0, 'Empty tables cannot be transposed.'
    # make the new table
    cols = make_unique_colnames([ make_valid_variable(name) for name in table.column(0) ])
    newtable = Table([ (table.columns[0].name, unicode) ] + [ (name, unicode) for name in cols])
    # append the data
    numcols = len(table.get_columns())
    for i in range(1, numcols):
      show_progress('Transposing...', float(i) / float(numcols))
      rec = newtable.append()
      rec[0] = table.columns[i].name
      for i, val in enumerate(table.column(i)):
        rec[i+1] = val
    return newtable
  finally:
    clear_progress()
  
  
def get_unordered(table, ascending, *cols):
  '''Finds all of the records that are out of order as measured by the values of the given cols.
     The point of this function is not to determine whether a table needs sorting
     (that would be more inefficient than simply sorting it to begin with).  This 
     function supports audit procedures that look for out-of-order items.
     
     Example:
       >>> table = Table([('col000', int), ('col001', int)], ([5,6], [3,2], [4,4], [4,5], [4,3]))
       >>> unordered = Simple.get_unordered(table, True, 'col000', 'col001')
       >>> unordered.view()
       +----------------+
       | Unordered Rows |
       +----------------+
       |              0 |
       |              3 |
       +----------------+     
      
     @param table:     The table to check for sorting
     @type  table:     Table or TableArray
     @param ascending: Whether to sort ascending or descending (True for ascending, False for descending)
     @type  ascending: bool
     @param cols:      One or more column names to check the sort by.
     @return:          A single-column table of the row indices that are out of order
     @rtype:           Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Finding unordered...', get_unordered, table, ascending, *cols)
  if ascending: direc = 1
  else: direc = -1
  # make a key for each rec and compare
  unordered = compare_records(table, "direc * cmp([record1[col] for col in cols], [record2[col] for col in cols]) >= 0")
  unordered.column(0).set_name("Unordered_Rows")
  return unordered
  
  
################################
###   Duplicates and Gaps

def find_duplicates(table, *cols):
  '''Finds all duplicates in the given columns.  Some audit procedures look for 
     duplicates in columns where duplicates should not exist (such as invoice numbers).
     This function supports this need.
     
     Example:
        >>> table = Table([('col000', int), ('col001', int)], ([1,6000], [2,6000], [2,4000], [3,5000], [5,5000], [6,5000]))
        >>> dups = Simple.find_duplicates(table, 'col000')
        >>> dups.view()
        +-----+--------+
        | Key |  Rows  |
        +-----+--------+
        |   2 | [1, 2] |
        +-----+--------+
        
     Another example:
       
     @param table:  The table to be analyzed
     @type  table:  Table or TableArray
     @param cols:   The columns where duplicate values are look for
     @return:       A table with one column for the key and one column for the duplicate record indices.
     @rtype:        Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Finding dupliates...', find_duplicates, table, *cols)
  check_valid_table(table, *cols)
  if len(cols) == 0:
    raise 'You must supply at least one column name/index'
  # index the given column(s)
  idx = dict(table.index(*cols))  # make a copy since we'll be modifying it
  # remove all items from the index that have only one value and return the rest
  for key in idx.keys():
    if len(idx[key]) <= 1:
      del idx[key]
  # make up a table of the keys and matching records
  dups = Table([ (table.column(col).name, table.column(col).column_type) for col in cols ])
  dups.append_column(ensure_unique_colname(dups, 'Rows'), tuple)
  for key, val in idx.items():
    if len(cols) == 1:
      dups.append([ key ] + [val])
    else:
      dups.append(list(key) + [val])
  return dups
    
  
  
def find_gaps(table, ascending, column):
  '''Finds gaps in the sequence of values in the given col.
     A gap is where the value of the column in record1 - the value of the column in
     record2 does not equal 1.  
     
     This function supports audit procedures that look for gaps in
     ordinarily-sequential column values, such as invoice numbers.
     Gaps indicate missing values that are normally the target of further research.
    
     Example to find gaps in a set of invoice numbers and amounts
        >>> table = Table([('col000', int), ('col001', int)], ([1,6000], [2,6000], [3,5000], [5,5000], [6,5000]))
        >>> gaps = Simple.find_gaps(table, True, 'col000')
        >>> gaps.view()
        +----------+
        | Gap Rows |
        +----------+
        |        2 |
        +----------+


     @param table:      The table to be analyzed for gaps in sequence
     @type  table:      Table or TableArray
     @param ascending:  The direction of the sort (True for ascending, False for descending)
     @type  ascending:  bool
     @param column:     The column name/index in the table that will be analyzed for gaps in sequence
     @type  column:     str
     @return:           A single-columned table of row indices where gaps occur
     @rtype:            Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Finding gaps...', find_gaps, table, ascending, column)
  check_valid_table(table, column)
  if ascending: direc = 1
  else: direc = -1
  gaps = compare_records(table, "record2[column] - record1[column] != direc")
  gaps.column(0).set_name("Rows")
  return gaps


################################
###   Selecting routines

def select_records(table, record_indices):
  '''Selects records from a table given a number of table record indices and
     returns a new table including only those records.
     
     This could obviously be done with a few lines of code, but this function
     provides the functionality for more readable code.
     
     This method *is* efficient and can be used often.
     
     Example:
        >>> table = Table([('col000', int), ('col001', int)], ([5,6], [3,2], [4,6]))
        >>> results = Simple.select_records(table, [0,2])
        >>> results.view()
        +--------+--------+
        | col000 | col001 |
        +--------+--------+
        |      5 |      6 |
        |      4 |      6 |
        +--------+--------+       

     @param table:           The table records will be selected from
     @type  table:           Table or TableArray
     @param record_indices:  A list of indices (of type int) of the records to be included.
     @type  record_indices:  list
     @return:                A new table containing the records included in the record_indices list.
     @rtype:                 Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Selecting records...', select_records, table, record_indices)
  check_valid_table(table)
  assert isinstance(record_indices, (types.ListType, types.TupleType)), 'The record_indices parameter must be a list: ' + str(record_indices)
  for item in record_indices:
    assert isinstance(item, (types.IntType, types.LongType)), 'The record_indices parameter must contain integers: ' + str(record_indices)
  try:
    results = Table(table.columns)
    for i, idx in enumerate(record_indices):
      show_progress('Selecting records...', float(i) / len(record_indices))
      results.append(table[idx])
    return results  
  finally:
    clear_progress()
     

def select_by_value(table, **col_value_pairs):
  '''Selects record from a table given colname=value pairs and returns a new
     table including only those records.
     
     This method *is* efficient and can be used often.  It calculates 
     indices as needed and should select very fast.
  
     If you need to do more complex selection, such as where a field is greater
     than some value, use Simple.select, which allows the use of arbitrary
     (and possibly powerful) expressions.
     
     Example:
      >>> table = Table([('col000', int), ('col001', int), ('col002', unicode)], [
      ...   [5,6,'flo'], 
      ...   [3,2,'sally'], 
      ...   [4,6,'dan'], 
      ...   [4,7,'stu' ], 
      ...   [4,7,'ben']
      ... ])
      >>> results = Simple.select_by_value(table, col001=6, col002='dan')
      >>> results.view()
      +--------+--------+--------+
      | col000 | col001 | col002 |
      +--------+--------+--------+
      |      4 |      6 | dan    |
      +--------+--------+--------+     

     @param table:              The table records will be selected from
     @type  table:              Table or TableArray
     @param col_value_pairs:    One or more column=value pairings giving the key(s) to select on (see the example)
     @return:                   A new table containing the records with matching key(s).
     @rtype:                    Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Selecting records...', select_by_value, table, **col_value_pairs)
  check_valid_table(table, *col_value_pairs.keys())
  # get an index to these columns
  idx = table.index(*col_value_pairs.keys())
  if len(col_value_pairs) == 1:
    vals = col_value_pairs.values()[0]
  else:
    vals = tuple(col_value_pairs.values())
  if idx.has_key(vals):
    return select_records(table, idx[vals])
  return select_records(table, [])


def select(table, expression):
  '''Selects records from a table based upon a custom expression and returns
     a new table including only those records.

     The expression should evaluate using "record" for the current record and
     the column names for individual column values.  The expression should
     evaluate to True or False, as in (assuming recid is a column name):
       "recid < 1000"
       
     The select function is very slow compared with database SELECT statements.
     If you have the choice (e.g. if you are using a database data source), 
     use the SQL SELECT instead of this function.  This is useful when data comes 
     from sources other than SQL, such as CSV/TSV files.
       
     Example: 
        >>> table = Table([('col000', int), ('col001', int)], ([5,6], [3,2], [4,6]))
        >>> results = Simple.select(table, "col001 > 5")
        >>> results.view()
        +--------+--------+
        | col000 | col001 |
        +--------+--------+
        |      5 |      6 |
        |      4 |      6 |
        +--------+--------+

     @param table:      The table records will be selected from
     @type  table:      Table or TableArray
     @param expression: An expression that evaluates each record and returns whether each should be included in the results table.     
     @type  expression: str
     @return:           A new table containing the records for which func evaluated to true (1)
     @rtype:            Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Selecting...', select, table, expression)
  check_valid_table(table)
  try:
    results = Table(table.columns)
    pe = PicaloExpression(expression)
    for i, rec in enumerate(table):
      show_progress('Selecting...', float(i) / len(table))
      if pe.evaluate([{'record':rec, 'recordindex':i}, rec]):
        results.append(rec)
    return results
  finally:
    clear_progress()
    

def select_by_wildcard(table, **col_value_pairs):
  '''Selects record from a table given colname=pattern pairs and returns a new
     table including only those records.  

     The methods supports the same wildcard characters as Simple.wildcard_match:

        - A question mark (?) matches a single letter (A-Z and a-z).
        - A pound sign (#) matches a single number (0-9).
        - A star (*) matches zero or more letters or numbers.
        
     Values are matched in a case-sensitive way, and the entire value must
     match the given pattern (no partial matches).  To control these settings,
     use Simple.select() with Simple.wildcard_match() in the expression.

     Example:
      >>> table = Table([('col000', int), ('col001', int), ('col002', unicode)], [
      ...   [5,6,'flo'], 
      ...   [3,2,'sally'], 
      ...   [4,6,'dan'], 
      ...   [4,77,'stu' ], 
      ...   [4,78,'ben']
      ... ])
      >>> results = Simple.select_by_wildcard(table, col001='#', col002='???')
      >>> results.view()
      +--------+--------+--------+
      | col000 | col001 | col002 |
      +--------+--------+--------+
      |      5 |      6 | flo    |
      |      4 |      6 | dan    |
      +--------+--------+--------+

     @param table:              The table records will be selected from
     @type  table:              Table or TableArray
     @param col_value_pairs:    One or more column=pattern pairings giving the column(s) to select on (see the example).
     @return:                   A new table containing the records with matching values for the given column patterns.
     @rtype:                    Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Selecting records...', select_by_wildcard, table, **col_value_pairs)
  check_valid_table(table, *col_value_pairs.keys())
  return select(table, ' and '.join(['Simple.wildcard_match("%s", %s)' % (pat.replace('"', '\\"'), colname) for (colname, pat) in col_value_pairs.items()]))
  
  
def select_by_regex(table, **col_value_pairs):
  '''Selects record from a table given colname=pattern pairs and returns a new
     table including only those records.  Each pattern sould be a valid regular
     expression.  Regular expressions are a very powerful matching language that 
     are available in many computer languages and programs.  This function uses 
     the Python re module internally, and it follows the re rules.  See 
     http://docs.python.org/dev/howto/regex.html for a tutorial
     on regular expressions.

     Values are matched in a case-sensitive way.  To allow case-insensitivity,
     use Simple.select() with Simple.regex_match() in the expression.

     Example:
      >>> table = Table([('col000', int), ('col001', int), ('col002', unicode)], [
      ...   [5,6,'flo'], 
      ...   [3,2,'sally'], 
      ...   [4,6,'dan'], 
      ...   [4,77,'stu' ], 
      ...   [4,78,'ben']
      ... ])
      >>> results = Simple.select_by_regex(table, col002='^\w{3}$')
      >>> results.view()
      +--------+--------+--------+
      | col000 | col001 | col002 |
      +--------+--------+--------+
      |      5 |      6 | flo    |
      |      4 |      6 | dan    |
      |      4 |     77 | stu    |
      |      4 |     78 | ben    |
      +--------+--------+--------+

     @param table:              The table records will be selected from
     @type  table:              Table or TableArray
     @param col_value_pairs:    One or more column=pattern pairings giving the column(s) to select on (see the example).
     @return:                   A new table containing the records with matching values for the given column patterns.
     @rtype:                    Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Selecting records...', select_by_wildcard, table, **col_value_pairs)
  check_valid_table(table, *col_value_pairs.keys())
  return select(table, ' and '.join(['Simple.regex_match("%s", %s)' % (pat.replace('"', '\\"'), colname) for (colname, pat) in col_value_pairs.items()]))


def calc_zscore(table, col):
  '''Calculates the zscore for each value in a column.  The z-score of a value
     gives an excellent indicator of how far outside the "normal" zone for a
     dataset.  
     
     The return of this function is often sent into Table.insert_column to
     put the z-score values in a column next to the original data.
     
     @param table:  A picalo table
     @type  table:  Table or TableArray
     @param col:    The column name to calculate zscore values on
     @type  col:    str
     @return:       A new single-column Picalo table with the zscores for the given column.
     @rtype:        Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Calculating z-score...', calc_zscore, table, col)
  check_valid_table(table, col)
  try:
    c = table.column(col)
    mean = lib.stats.mean(c)
    stdev = lib.stats.samplestdev(c)
    results = Table([('ZScore', float)])
    if stdev > 0:
      for i, val in enumerate(c):
        show_progress('Calculating z-score...', float(i) / len(table))
        results.append([(val-mean)/stdev])
    return results
  finally:
    clear_progress()
    
  
def select_outliers(table, col, min=None, max=None):
  '''A convenience function to select outliers from a table.  Outliers 
     are those with column values below the min or above the max.
     The source table is not modified.
     
     This type of filtering could also be done with the Simple.select method,
     but since filtering of outliers is so common, it is given its own function.
     
     Example:
        >>> table = Table([('col000', int), ('col001', int)], ([8,6], [3,2], [0,4], [4,6]))
        >>> selected = Simple.select_outliers(table, 'col000', min=2, max=5)
        >>> selected.view()
        +--------+--------+
        | col000 | col001 |
        +--------+--------+
        |      8 |      6 |
        |      0 |      4 |
        +--------+--------+

     @param table:  The table to be filtered
     @type  table:  Table or TableArray
     @param col:    The column index to evaluate
     @type  col:    str
     @param min:    An optional value that specifies a lower bound for included records.  If omitted, no lower bound is used
     @type  min:    object
     @param max:    An optional value that specifies an upper bound for included records.  If omitted, no upper bound is used
     @type  max:    object
     @return:       A new table containing only the outliers
     @rtype:        Table
  '''
  return select(table, "(min==None or record[col]<min) or (max==None or record[col]>max)")


def select_outliers_z(table, col, zscore):
  '''A convenience function to select outliers from a table.  Outliers 
     are those with column values with zscores above +zscore or below -zscore.
     The source table is not modified.
     
     This type of filtering could also be done with the Simple.select method,
     but since filtering of outliers is so common, it is given its own function.
     
     Example:
        >>> table = Table([('col000', int), ('col001', int)], ([8,8], [3,2], [0,4], [4,3]))
        >>> selected = Simple.select_outliers_z(table, 'col001', 1)
        >>> selected.view()
        +--------+--------+
        | col000 | col001 |
        +--------+--------+
        |      8 |      8 |
        +--------+--------+

     @param table:   A Picalo table
     @type  table:   Table or TableArray
     @param col:     The column index to evaluate
     @type  col:     str
     @param zscore:  The zscore to filter above and below
     @type  zscore:  float
     @return:        A new table containing only the outliers
     @rtype:         Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Selecting outliers...', select_outliers_z, table, col, zscore)
  # calculate the pieces of the zscore routine
  c = table.column(col)
  mean = lib.stats.mean(c)
  stdev = lib.stats.samplestdev(c)
  if stdev == 0:
    return Table(table.columns)
  zpos = math.fabs(zscore)
  zneg = -math.fabs(zscore)
  return select(table, "((record[col]-mean)/stdev<zneg) or ((record[col]-mean)/stdev>zpos)")

def select_nonoutliers(table, col, min=None, max=None):
  '''A convenience function to select non-outliers from a table.  Outliers 
     are those with column values below the min or above the max.
     The source table is not modified.
     
     This type of filtering could also be done with the Simple.select method,
     but since filtering of outliers is so common, it is given its own function.
     
     Example:
        >>> table = Table([('col000', int), ('col001', int)], ([8,6], [3,2], [0,4], [4,6]))
        >>> selected = Simple.select_nonoutliers(table, 'col000', min=2, max=5)
        >>> selected.view()
        +--------+--------+
        | col000 | col001 |
        +--------+--------+
        |      3 |      2 |
        |      4 |      6 |
        +--------+--------+

     @param table:  The table to be filtered
     @type  table:  Table or TableArray
     @param col:    The column index to evaluate
     @type  col:    str
     @param min:    An optional value that specifies a lower bound for included records.  If omitted, no lower bound is used
     @type  min:    object
     @param max:    An optional value that specifies an upper bound for included records.  If omitted, no upper bound is used
     @type  max:    object
     @return:       A new table with all outliers removed
     @rtype:        Table
  '''
  return select(table, "(min==None or record[col]>=min) and (max==None or record[col]<=max)")
  
  
def select_nonoutliers_z(table, col, zscore):
  '''A convenience function to select non-outliers from a table.  Outliers 
     are those with column values with zscores above +zscore or below -zscore.
     The source table is not modified.
     
     This type of filtering could also be done with the Simple.select method,
     but since filtering of outliers is so common, it is given its own function.

     Example:
        >>> table = Table([('col000', int), ('col001', int)], ([8,8], [3,2], [0,4], [4,3]))
        >>> selected = Simple.select_nonoutliers_z(table, 'col001', 1)
        >>> selected.view()
        +--------+--------+
        | col000 | col001 |
        +--------+--------+
        |      3 |      2 |
        |      0 |      4 |
        |      4 |      3 |
        +--------+--------+

     @param table:   The table to be filtered
     @type  table:   Table
     @param col:     The column index to evaluate
     @type  col:     str
     @param zscore:  The zscore to filter above and below
     @type  zscore:  float
     @return:        A new table containing only the outliers
     @rtype:         Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Selecting nonoutliers...', select_nonoutliers_z, table, col, zscore)
  check_valid_table(table, col)
  assert isinstance(zscore, (types.IntType, types.LongType, types.FloatType)), 'The zscore parameter must be a number: ' + str(zscore)
  # calculate the pieces of the zscore routine
  c = table.column(col)
  mean = lib.stats.mean(c)
  stdev = lib.stats.samplestdev(c)
  if stdev == 0:
    return Table(table.columns)
  zpos = math.fabs(zscore)
  zneg = -math.fabs(zscore)
  return select(table, "((record[col]-mean)/stdev>=zneg) and ((record[col]-mean)/stdev<=zpos)")
  

################################
###   Matching routines  
    
def expression_match(table1, table2, expression):
  '''Finds records in the two tables where the expression evalutes True.
     This method is usually used only internally, but it is available for 
     general use for those who want it.  (in other words, most users generally
     use other methods like join, col_match_same, etc.)
     
     The resulting table shows the matching records indices in table 1 and table 2.

     The variable "record1" is set to a record in table1, and "record2" is set to a record
     in table2.  The expression is evaluated for each record in table 1 and table 2.

     This function is *much* slower than a Database join.  If you are getting data
     from a database, use the SQL join instead.  This method is provided when you
     need to join tables that were loaded from CSV, etc.
     
     However, although it is slower, this function can evalute any expression (including
     the use of Picalo functions) in the join.
     
     Example: 
        >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
        >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
        >>> matches = Simple.expression_match(table1, table2, "record1[0] == record2[0]")
        >>> matches.view()
        +--------------+--------------+
        | table1record | table2record |
        +--------------+--------------+
        |            0 |            0 |
        |            0 |            2 |
        +--------------+--------------+
       
     @param table1:      The first source table
     @type  table1:      Table
     @param table2:      The second source table
     @type  table2:      Table
     @param expression:  The expression to be evaluated, using variables record1 and record2
     @type  expression:  str
     @return:            A picalo Table containing the table1 match, the table2 match, and the key
     @rtype:             Table
  '''
  check_valid_table(table1)
  check_valid_table(table2)
  try:
    # create a picalo table of the matches
    results = Table([('Table1_Record', int), ('Table2_Record', int)])
    pe = PicaloExpression(expression)
    for t1index in range(len(table1)):
      show_progress('Matching...', t1index / len(table1))
      for t2index in range(len(table2)):
        if pe.evaluate([{'record1':table1[t1index], 'record1index':t1index, 'record2':table2[t2index], 'record2index':t2index}, table1[t1index], table2[t2index]]):
          results.append([t1index, t2index])
    return results
  finally:
    clear_progress()
  


def col_join(table1, table2, *match_cols):
  '''Joins two tables together (similar to a regular SQL inner join) that have
     matching values in the given columns.

     This function is much faster than Simple.join() because it uses table indices.     
     However, it is much slower than a Database join.  If you are getting data
     from a database, use the SQL join instead.  This method is provided when you
     need to join tables that were loaded from CSV, etc.
     
     Example:
        >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
        >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
        >>> matches = Simple.col_join(table1, table2, ['col000','col000'], ['col001','col002'])
        >>> matches.view()
        +--------+--------+----------+----------+--------+
        | col000 | col001 | col000_2 | col001_2 | col002 |
        +--------+--------+----------+----------+--------+
        |      3 |      2 |        3 | Bailey   |      2 |
        |      3 |      2 |        3 | Sally    |      2 |
        +--------+--------+----------+----------+--------+     
     
     @param table1:       The first source table
     @type  table1:       Table
     @param table2:       The second source table
     @type  table2:       Table
     @param match_cols:   One or more 2-tuples specifying columns to be matched for the join (see the example)
     @return:             A picalo Table containing matching records from the two source tables
     @rtype:              Table
  '''     
  assert len(match_cols) > 0, 'You must specify at least one column to join the tables on'
  for match in match_cols:
    assert isinstance(match, (types.ListType, types.TupleType)), 'The match column must be a list of two column names/indices: ' + str(match)
    assert len(match) == 2, 'The match column must be a list of two column names/indices: ' + str(match)
    check_valid_table(table1, match[0])
    check_valid_table(table2, match[1])
  matches = col_match(table1, table2, *match_cols)
  return _join(table1, table2, matches, False)


def col_left_join(table1, table2, *match_cols):
  '''Joins two tables together (similar to a regular SQL LEFT join) that have
     matching values in the given columns.  All records in table1 are returned,
     and only matching records in table2 are joined with them.

     This function is much faster than Simple.join() because it uses table indices.     
     However, it is much slower than a Database join.  If you are getting data
     from a database, use the SQL join instead.  This method is provided when you
     need to join tables that were loaded from CSV, etc.
     
     Example:
        >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
        >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
        >>> matches = Simple.col_left_join(table1, table2, ['col000','col000'], ['col001','col002'])
        >>> matches.view()
        +--------+--------+----------+----------+--------+
        | col000 | col001 | col000_1 | col001_1 | col002 |
        +--------+--------+----------+----------+--------+
        |      3 |      2 |        3 | Bailey   |      2 |
        |      3 |      2 |        3 | Sally    |      2 |
        |      4 |      5 |   <N>    |   <N>    |  <N>   |
        +--------+--------+----------+----------+--------+
     
     @param table1:       The first source table
     @type  table1:       Table
     @param table2:       The second source table
     @type  table2:       Table
     @param match_cols:   One or more 2-tuples specifying columns to be matched for the join (see the example)
     @return:             A picalo Table containing matching records from the two source tables
     @rtype:              Table
  '''     
  assert len(match_cols) > 0, 'You must specify at least one column to join the tables on'
  for match in match_cols:
    assert isinstance(match, (types.ListType, types.TupleType)), 'The match column must be a list of two column names/indices: ' + str(match)
    assert len(match) == 2, 'The match column must be a list of two column names/indices: ' + str(match)
    check_valid_table(table1, match[0])
    check_valid_table(table2, match[1])
  matches = col_match(table1, table2, *match_cols)
  return _join(table1, table2, matches, True)


def col_right_join(table1, table2, *match_cols):
  '''Joins two tables together (similar to a regular SQL RIGHT join) that have
     matching values in the given columns.  All records in the table2 are returned,
     and only matching records in table1 are joined with them.

     This function is much faster than Simple.join() because it uses table indices.     
     However, it is much slower than a Database join.  If you are getting data
     from a database, use the SQL join instead.  This method is provided when you
     need to join tables that were loaded from CSV, etc.
     
     Example:
        >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
        >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
        >>> matches = Simple.col_right_join(table1, table2, ['col000','col000'], ['col001','col002'])
        >>> matches.view()
        +--------+--------+--------+----------+----------+
        | col000 | col001 | col002 | col000_1 | col001_1 |
        +--------+--------+--------+----------+----------+
        |      3 | Bailey |      2 |        3 |        2 |
        |      1 | Dan    |      2 |   <N>    |   <N>    |
        |      3 | Sally  |      2 |        3 |        2 |
        +--------+--------+--------+----------+----------+     
        
     @param table1:       The first source table
     @type  table1:       Table
     @param table2:       The second source table
     @type  table2:       Table
     @param match_cols:   One or more 2-tuples specifying columns to be matched for the join (see the example)
     @return:             A picalo Table containing matching records from the two source tables
     @rtype:              Table
  '''     
  # reverse the match_cols, since we're reversing the tables
  return col_left_join(table2, table1, *[ cols[::-1] for cols in match_cols])


def join(table1, table2, expression):
  '''Joins two tables together (similar to a regular SQL inner join) where
     the expression evalutes True.
     
     This function is *much* slower than a Database join.  If you are getting data
     from a database, use the SQL join instead.  This method is provided when you
     need to join tables that were loaded from CSV, etc.
     
     Example:
        >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
        >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
        >>> matches = Simple.join(table1, table2, "record1[0] == record2[0]")
        >>> matches.view()
        +--------+--------+----------+----------+--------+
        | col000 | col001 | col000_2 | col001_2 | col002 |
        +--------+--------+----------+----------+--------+
        |      3 |      2 |        3 | Bailey   |      2 |
        |      3 |      2 |        3 | Sally    |      2 |
        +--------+--------+----------+----------+--------+


     @param table1:      The first source table
     @type  table1:      Table
     @param table2:      The second source table
     @type  table2:      Table
     @param expression:  The expression to be evaluated, using variables record1 and record2
     @type  expression:  str
     @return:            A picalo Table containing matching records from the two source tables
     @rtype:             Table
  '''
  check_valid_table(table1)
  check_valid_table(table2)
  matches = expression_match(table1, table2, expression)
  return _join(table1, table2, matches, False)
  
  
def left_join(table1, table2, expression):
  '''Joins two tables together (similar to a regular SQL LEFT join) where
     the expression evalutes True.  All records in the first table are returned,
     and only matching records in the second table are returned.
     
     This function is *much* slower than a Database join.  If you are getting data
     from a database, use the SQL join instead.  This method is provided when you
     need to join tables that were loaded from CSV, etc.
     
     Example:
        >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
        >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
        >>> matches = Simple.left_join(table1, table2, "record1[0] == record2[0]")
        >>> matches.view()
        +--------+--------+----------+----------+--------+
        | col000 | col001 | col000_1 | col001_1 | col002 |
        +--------+--------+----------+----------+--------+
        |      3 |      2 |        3 | Bailey   |      2 |
        |      3 |      2 |        3 | Sally    |      2 |
        |      4 |      5 |   <N>    |   <N>    |  <N>   |
        +--------+--------+----------+----------+--------+

     @param table1:      The first source table
     @type  table1:      Table
     @param table2:      The second source table
     @type  table2:      Table
     @param expression:  The expression to be evaluated, using variables record1 and record2
     @type  expression:  str
     @return:            A picalo Table containing matching records from the two source tables
     @rtype:             Table
  '''
  check_valid_table(table1)
  check_valid_table(table2)
  matches = expression_match(table1, table2, expression)
  return _join(table1, table2, matches, True)


def right_join(table1, table2, expression):
  '''Joins two tables together (similar to a regular SQL RIGHT join) where
     the expression evalutes True.  All records in the second table are returned,
     and only matching records in the first table are returned.
     
     This function is *much* slower than a Database join.  If you are getting data
     from a database, use the SQL join instead.  This method is provided when you
     need to join tables that were loaded from CSV, etc.
     
     Example:
        >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
        >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
        >>> matches = Simple.right_join(table1, table2, "record1[0] == record2[0]")
        >>> matches.view()
        +--------+--------+--------+----------+----------+
        | col000 | col001 | col002 | col000_1 | col001_1 |
        +--------+--------+--------+----------+----------+
        |      3 | Bailey |      2 |        3 |        2 |
        |      1 | Dan    |      2 |   <N>    |   <N>    |
        |      3 | Sally  |      2 |        3 |        2 |
        +--------+--------+--------+----------+----------+

     @param table1:      The first source table
     @type  table1:      Table
     @param table2:      The second source table
     @type  table2:      Table
     @param expression:  The expression to be evaluated, using variables record1 and record2
     @type  expression:  str
     @return:            A picalo Table containing matching records from the two source tables
     @rtype:             Table
  '''
  return left_join(table2, table1, expression)
  
    
def _join(table1, table2, matches, left_join=False):
  '''Internal method to perform joining.  If left_join is True, 
     all records in table1 are returned (i.e. SQL LEFT JOIN) with
     any matching records from the right table.  If
     left_join is False, only the matching records are returned.
     To perform a right_join, simply reverse table1 and table2.'''
  try:
    # create the new table
    newcols = []
    for heading in table1.get_columns() + table2.get_columns():
      column = heading._get_columnloader()
      column.name = ensure_unique_list_value([col.name for col in newcols], column.name)
      newcols.append(column)
    joined = Table(newcols)
    table1cols = len(table1.get_columns())
    table2cols = len(table2.get_columns())
    # populate the new table with matching records
    if left_join:  # left join -- all records from table1
      matches_map = {} # first make a map of the matches (for fast access)
      for match in matches:
        matches_map.setdefault(match[0], []).append(match[1])
      for table1index in range(len(table1)):
        show_progress('Joining...', float(table1index) / len(table1))
        if table1index in matches_map:  # if we have matches for this record number
          for table2index in matches_map[table1index]:
            rec = joined.append()
            for i in range(table1cols):
              rec[i] = table1[table1index][i]
            for i in range(table2cols):
              rec[table1cols+i] = table2[table2index][i]
        
        else:  # no matches, so simply add the record
          rec = joined.append()
          for i in range(table1cols):
            rec[i] = table1[table1index][i]
      
    else:  # regular join -- only do the matches
      for counter, match in enumerate(matches):
        show_progress('Joining...', float(counter) / len(matches))
        rec = joined.append()
        for i in range(table1cols):
          rec[i] = table1[match[0]][i]
        for i in range(table2cols):  
          rec[table1cols+i] = table2[match[1]][i]
    return joined
  finally:
    clear_progress()
  

def col_match(table1, table2, *match_cols):
  '''Finds rows in the two tables with values that match in specific columns.
     This method is usually used only internally, but it is available for 
     general use for those who want it.  (in other words, most users generally
     use other methods like join, col_match_same, etc.)
     
     Example: 
        >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
        >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
        >>> matches = Simple.col_match(table1, table2, ['col000','col000'], ['col001','col002'])
        >>> matches.view()
        +--------------+--------------+--------+
        | table1record | table2record |  key   |
        +--------------+--------------+--------+
        |            0 |            0 | (3, 2) |
        |            0 |            2 | (3, 2) |
        +--------------+--------------+--------+ 
       
     @param table1:       The first source table
     @type  table1:       Table
     @param table2:       The second source table
     @type  table2:       Table
     @param match_cols:   One or more 2-tuples specifying columns to be matched (see the example)
     @return:             A picalo Table containing the table1 match, the table2 match, and the key
     @rtype:              Table
  '''
  assert len(match_cols) > 0, 'You must specify at least one column to match the tables on'
  for match in match_cols:
    assert isinstance(match, (types.ListType, types.TupleType)), 'The match column must be a list of two column names/indices: ' + str(match)
    assert len(match) == 2, 'The match column must be a list of two column names/indices: ' + str(match)
    check_valid_table(table1, match[0])
    check_valid_table(table2, match[1])
  try:
    # I'm not sure if we can trust that keys() and values() always come in a consistent order, so
    # I rolled my own code to split the dictionary into two lists
    columns = match_cols
    # index the two tables
    index1 = table1.index(*[item[0] for item in columns])
    index2 = table2.index(*[item[1] for item in columns])
    # find the matching keys in the two indices using the builtin filter function
    matches = filter(lambda x: x in index1.keys(), index2.keys())
    # create a picalo table of the matches
    results = Table([('Table1_Record', int), ('Table2_Record', int), ('Key', tuple)])
    for counter, key in enumerate(matches):
      show_progress('Matching...', float(counter) / len(matches))
      for i1 in index1[key]: # separate result row for each matching record
        for i2 in index2[key]:
          results.append(i1, i2, key)
    return results
  finally:
    clear_progress()
  
  
def col_match_same(table1, table2, *match_cols):
  '''Finds records in the two tables with values that match in specific columns and
     returns two new tables that contain only those records.  Stated differently,
     this method filters all non-matching rows out of the two tables and returns
     the filtered tables (the original tables are not modified).  All records
     that have matching keys in the other table are included.

     This function is the opposite of col_match_diff.
     
     Example: 
       >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
       >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
       >>> match1, match2 = Simple.col_match_same(table1, table2, ['col000','col000'], ['col001','col002'])
       >>> match1.view()
       +--------+--------+
       | col000 | col001 |
       +--------+--------+
       |      3 |      2 |
       +--------+--------+    
       >>> match2.view()
       +--------+--------+--------+
       | col000 | col001 | col002 |
       +--------+--------+--------+
       |      3 | Bailey |      2 |
       |      3 | Sally  |      2 |
       +--------+--------+--------+     
     
     @param table1:       The first source table
     @type  table1:       Table
     @param table2:       The second source table
     @type  table2:       Table
     @param match_cols:   One or more 2-tuples specifying columns to be matched (see the example)
     @return:             A list of two Tables containing only matching records
     @rtype:              list
  '''
  # parameter type assertion is performed by col_match
  # perform the match
  matches = col_match(table1, table2, *match_cols)
  # round up the results
  results = TableList([Table(table1.columns), Table(table2.columns)])
  tables = ( table1, table2 )
  for i in [0,1]:
    for recno in dict(zip(matches.column(i), matches.column(i))).keys(): # convert to dict to remove duplicate record numbers
      results[i].append(tables[i][recno])
  return results
  
  
  
def col_match_diff(table1, table2, *match_cols):
  '''Finds records in the two tables with values that match in specific columns and
     returns two new tables that contain everything but those records.  Stated differently,
     this method filters all matching rows out of the two tables and returns
     the filtered tables (the original tables are not modified).  All records
     that do not have matching keys in the other table are included.

     This function is the opposite of col_match_same.
     
     Example: 
        >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
        >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
        >>> match1, match2 = Simple.col_match_diff(table1, table2, ['col000','col000'])
        >>> match1.view()
        +--------+--------+
        | col000 | col001 |
        +--------+--------+
        |      4 |      5 |
        +--------+--------+
        >>> match2.view()
        +--------+--------+--------+
        | col000 | col001 | col002 |
        +--------+--------+--------+
        |      1 | Dan    |      2 |
        +--------+--------+--------+

     @param table1:       The first source table
     @type  table1:       Table
     @param table2:       The second source table
     @type  table2:       Table
     @param match_cols:   One or more 2-tuples specifying columns to be matched (see the example)
     @return:             A list of two Tables containing only non-matching records
     @rtype:              list
  '''
  # parameter type assertion is performed by col_match
  # perform the match
  matches = col_match(table1, table2, *match_cols)
  # round up the results
  results = TableList([ Table(table1.get_columns()), Table(table2.get_columns()) ])
  tables = ( table1, table2 )
  for i in [0,1]:
    # convert the matching rec nums to maps (removes duplicates)
    matchrecnums = dict(zip(matches.column(i), matches.column(i)))
    # create a table of the opposite
    for recnum in range(len(tables[i])):
      if not matchrecnums.has_key(recnum):
        results[i].append(tables[i][recnum])
  return results


def custom_match(table1, table2, expression):
  '''Finds rows in the two tables with values that match as returned by the specified expression.
     This is a more general version of col_match.  It is significantly slower than col_match
     because it can't uses indices.  It is O^2.
     
     The expression should use "record1" for the current record in table 1 and "record2" for
     the current record in the table 2, and it should evaluate to True or False.  
     
     Example: 
       >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
       >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
       >>> # match if the first column matches (granted, a very simple comparison in this example)P
       >>> matches = Simple.custom_match(table1, table2, "record1[0] == record2[0]")
       >>> matches.view()
       +--------------+--------------+
       | table1record | table2record |
       +--------------+--------------+
       |            0 |            0 |
       |            0 |            2 |
       +--------------+--------------+
          
     @param table1:       The first source table
     @type  table1:       Table
     @param table2:       The second source table
     @type  table2:       Table
     @param expression:   An expression to use for the match
     @type  expression:   str
     @return:             A picalo Table containing the table1 match and the table2 match
     @rtype:              Table
  '''
  check_valid_table(table1)
  check_valid_table(table2)
  try:
    results = Table([('Table1_Record', int), ('Table2_Record', int)])
    pe = PicaloExpression(expression)
    for recnum1 in range(len(table1)):
      show_progress('Matching...', float(recnum1) / len(table1))
      for recnum2 in range(len(table2)):
        if pe.evaluate([{'record1':table1[recnum1], 'record1index':recnum1, 'record2':table2[recnum2], 'record2index':recnum2}, table1[recnum1], table2[recnum2]]):
          results.append(recnum1, recnum2)
    return results
  finally:
    clear_progress()

  
def custom_match_same(table1, table2, expression):
  '''Finds records in the two tables with values that match based upon the give expression and
     returns two new tables that contain only those records.  Stated differently,
     this method filters all non-matching rows out of the two tables and returns
     the filtered tables (the original tables are not modified).  All records
     that have matching keys in the other table are included.

     The expression should use "record1" for the current record in table 1 and "record2" for
     the current record in the table 2, and it should evaluate to True or False.  

     This function is the opposite of custom_match_diff.

     Example: 
        >>> employees = Table([('col000', unicode), ('col001', unicode)], (['Bailey', '123 North Way'], ['Sally', '456 Dety']))
        >>> vendors = Table([('col000', unicode), ('col001', unicode)], (['ABC Comp', '789 Maple'], ['DEF Enterprises', '123 Nth Way']))
        >>> t1, t2 = Simple.custom_match_same(vendors, employees, "Simple.fuzzymatch(record1[1], record2[1]) > .5")
        >>> t1.view()
        +-----------------+-------------+
        |      col000     |    col001   |
        +-----------------+-------------+
        | DEF Enterprises | 123 Nth Way |
        +-----------------+-------------+
        >>> t2.view()
        +--------+---------------+
        | col000 |     col001    |
        +--------+---------------+
        | Bailey | 123 North Way |
        +--------+---------------+

     @param table1:       The first source table
     @type  table1:       Table
     @param table2:       The second source table
     @type  table2:       Table
     @param expression:   An expression to use for the match
     @type  expression:   str
     @return:             list of two Tables containing only matching records
     @rtype:              list
  '''
  # parameter type checking is performed by custom_match
  ### THIS METHOD IS AN ALMOST DIRECT COPY OF col_match_same ABOVE
  # perform the match       
  matches = custom_match(table1, table2, expression)
  # round up the results
  results = TableList([ Table(table1.get_columns()), Table(table2.get_columns()) ])
  tables = ( table1, table2 )
  for i in [0,1]:
    for recno in dict(zip(matches.column(i), matches.column(i))).keys(): # convert to dict to remove duplicate record numbers
      results[i].append(tables[i][recno])
  return results
    
  
def custom_match_diff(table1, table2, expression):
  '''Finds records in the two tables with values that do not match based upn the give expression and
     returns two new tables that contain only those records.  Stated differently,
     this method filters all matching rows out of the two tables and returns
     the filtered tables (the original tables are not modified).  All records
     that do not have matching keys in the other table are included.

     The expression should use "record1" for the current record in table 1 and "record2" for
     the current record in the table 2, and it should evaluate to True or False.  

     This function is the opposite of custom_match_same.
     
     Example: 
       >>> table1 = Table([('col000', int), ('col001', int)], ([3,2], [4,5]))
       >>> table2 = Table([('col000', int), ('col001', unicode), ('col002', int)], ([3,'Bailey',2], [1,'Dan',2], [3,'Sally',2]))
       >>> # match if the first column matches (granted, a very simple comparison in this example)
       >>> match1, match2 = Simple.custom_match_diff(table1, table2, "record1[0] == record2[0]")
       >>> match1.view()
       +--------+--------+
       | col000 | col001 |
       +--------+--------+
       |      3 |      2 |
       +--------+--------+     
       >>> match2.view()
       +--------+--------+--------+
       | col000 | col001 | col002 |
       +--------+--------+--------+
       |      3 | Bailey |      2 |
       |      3 | Sally  |      2 |
       +--------+--------+--------+
   
     @param table1:       The first source table
     @type  table1:       Table
     @param table2:       The second source table
     @type  table2:       Table
     @param expression:   An expression to use for the match
     @type  expression:   str
     @return:             A list of two Tables containing only non-matching records
     @rtype:              list
  '''
  # parameter type checking is performed by custom_match
  ### THIS METHOD IS AN ALMOST DIRECT COPY OF col_match_diff ABOVE
  # perform the match
  matches = custom_match(table1, table2, expression)
  # round up the results
  results = TableList([ Table(table1.get_columns()), Table(table2.get_columns()) ])
  tables = ( table1, table2 )
  for i in [0,1]:
    # convert the matching rec nums to maps (removes duplicates)
    matchrecnums = dict(zip(matches.column(i), matches.column(i)))
    # create a table of the opposite
    for recnum in range(len(tables[i])):
      if not matchrecnums.has_key(recnum):
        results[i].append(tables[i][recnum])
  return results  


#################################################
###   Fuzzy text matching


def soundex(text, len=4, digits='01230120022455012623010202'):
  '''Calculates a soundex computation for the given text.
     Soundex is a standard algorithm for comparing text in a fuzzy way.  For example,
     it sees 'Smith', 'Smoth', and 'Smiith' as the same thing.  From a fraud detection
     perspective, it is extremely useful to match addresses, employee names, vendor names,
     and other text that may have variations in it.
     
     Soundex creates a number out of text.  To compare two text values, compute a soundex
     hash of both values and compare the soundex results.
     
     Note that soundex is optimized for English names.  If you need to optimize for other
     languages, search the Internet for an appropriate set of digits.
     
     Also note that this method calculates the raw soundex score.  It may be more
     useful to use Simple.soundexcol, which runs the soundex algorithm on
     an entire column.

     Credits: Taken from ASPN: implementation 2000-12-24 by Gregory Jorgensen
     License: Public domain by G.J.
     
     Example:
       >>> Simple.soundex('Smith') 
       'S530'
       >>> Simple.soundex('Smoth') 
       'S530'
       >>> Simple.soundex('Smithinson', len=6)
       'S53525'
       >>> Simple.soundex('Smithinall', len=6)
       'S53540'
       
     @param text:    The text to compute soundex on
     @type  text:    str
     @param len:     The length of the resulting soundex hash.  Longer lengths are more precise.  Shorter lengths are more fuzzy.
     @type  len:     int
     @param digits:  The digits to use in the soundex algorithm.  The default digits are optimized for English names.
     @type  digits:  str
     @return:        The soundex hash for the given text.
     @rtype:         str
  '''
  assert isinstance(text, types.StringTypes), 'The text parameter must be a string: ' + str(text)
  assert isinstance(len, types.IntType), 'The len parameter must be an integer: ' + str(len)
  assert isinstance(digits, types.StringTypes), 'The digits parameter must be a string: ' + str(digits)
  sndx = ''
  fc = ''

  # translate alpha chars in text to soundex digits
  for c in text.upper():
    if c.isalpha():
      if not fc: 
        fc = c   # remember first letter
      d = digits[ord(c)-ord('A')]
      # duplicate consecutive soundex digits are skipped
      if not sndx or (d != sndx[-1]):
        sndx += d

  # replace first digit with first alpha character
  sndx = fc + sndx[1:]

  # remove all 0s from the soundex code
  sndx = sndx.replace('0','')

  # return soundex code padded to len characters
  return (sndx + (len * '0'))[:len]
  
  
def soundexcol(table, col):
  '''Calculates the soundex score for each value in a column and 
     appends the scores as a new column in the table.  The new column
     is named 'column_soundex' (where column is the name of the column).
     
     See the Simple.soundex method for information on the soundex algorithm.

     Example:
       >>> t = Table([('name', unicode)], [['Samuel'], ['Sally'], ['Max'], ['Maxx']])
       >>> Simple.soundexcol(t, 'name')
       >>> t.view()
       +--------+------+
       |  name  | hash |
       +--------+------+
       | Samuel | S540 |
       | Sally  | S400 |
       | Max    | M200 |
       | Maxx   | M200 |
       +--------+------+
       >>> # Grouping by the new 'hash' column will quickly place duplicates together in groups.     
     
     @param table:  A Picalo table 
     @type  table:  Table
     @param col:    The column name/index to calculate the soundex score on.
     @type  col:    str
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Appending soundex column...', soundexcol, table, col)
  check_valid_table(table, col)
  colname = table.column(col).name     # if the index is given, get the name
  hashname = ensure_unique_colname(table, colname + '_soundex')
  table.append_calculated_static(hashname, unicode, "Simple.soundex(record[" + str(table.deref_column(col)) + "])")
  
  
  
def fuzzysearch(fulltext, searchtext, ngramlen=3, ignorecase=True):
  '''Calculates a fuzzy search to see if searchtext is found in fulltext.
     This is an adaptation of the Trigram method found at http://www.heise.de/ct/english/97/04/386/
     by Reinhard Rapp.  The score will always be a decimal between 0.0 and 1.0:
      - 0.0 means the letters in (and sequence of) searchtext is not found at in any form in fulltext.
      - 1.0 means the letters in searchtext is perfectly found in fulltext.
     
     This algorithm is not as effective as more advanced neural-net-based algorithms, but it
     is simple and works fairly well. 
     
     This method is different than fuzzymatch because it expects a long string for the fulltext
     variable.  For example, searching for a phrase within a large document.  
       
     @param fulltext:    The text to find within.
     @type  fulltext:    str
     @param searchtext:  The text to search for.
     @type  searchtext:  str
     @param ngramlen:    The length of the ngrams to test.  Smaller ngrams provide greater tolerance and higher scores.  Larger ngrams provide smaller tolerance and lower scores.  An ngram of the length of searchtext provides an exact match only.  Default is 3.
     @type  ngramlen:    int
     @param ignorecase:  Whether to ignore letter case when searching.  Default is to ignore case.
     @type  ignorecase:  bool
     @return:            A float between 0.0 and 1.0 giving a score for the amount of match.
     @rtype:             float
  '''
  assert isinstance(fulltext, types.StringTypes), 'The fulltext parameter must be a string.'
  assert isinstance(searchtext, types.StringTypes), 'The fulltext parameter must be a string.'
  assert isinstance(ngramlen, types.IntType), 'The ngramlen parameter must be an integer.'
  if ignorecase:
    fulltext = fulltext.lower()
    searchtext = searchtext.lower()
  ngramlen = min(ngramlen, len(searchtext))
  nummatches = 0
  numngrams = len(searchtext) - ngramlen + 1
  for i in range(0, numngrams):
    ngram = searchtext[i: i + ngramlen]
    if fulltext.find(ngram) >= 0:
      nummatches += 1
  # the main difference between fuzzymatch and fuzzysearch is this calculation
  # this calculation is an adaptation made for large lengths of fulltext
  # when fulltext is long, the regular calculation doesn't work well
  return float(nummatches) / float(numngrams)
    
    
def fuzzymatch(text1, text2, ngramlen=3, ignorecase=True):  
  '''Calculates a fuzzy match of text1 and text2.
     This is an adaptation of the Trigram method found at http://www.heise.de/ct/english/97/04/386/
     by Reinhard Rapp.  The score will always be a decimal between 0.0 and 1.0:
      - 0.0 means the letters in (and sequence of) searchtext is not found at in any form in fulltext.
      - 1.0 means the letters in searchtext is perfectly found in fulltext.
     
     This algorithm is not as effective as more advanced neural-net-based algorithms, but it
     is simple and fast.  It requires very little processing power compared with more advanced
     algorithms.
     
     This method is different than fuzzysearch because it expects text1 and text2 to
     be about the same length.  For example, two last names, two addresses, etc.
       
     Example:
       >>> Simple.fuzzymatch("500 West Street", "500 West St.")
       0.69230769230769229
       
     @param text1:       The first text string.
     @type  text1:       str
     @param text2:       The second text string.
     @type  text2:       str
     @param ngramlen:    The length of the ngrams to test.  Smaller ngrams provide greater tolerance and higher scores.  Larger ngrams provide smaller tolerance and lower scores.  An ngram of the length of searchtext provides an exact match only.  Default is 3.
     @type  ngramlen:    int
     @param ignorecase:  Whether to ignore letter case when searching.  Default is to ignore case.
     @type  ignorecase:  bool
     @return:            A float between 0.0 and 1.0 giving a score for the amount of match.
     @rtype:             float
  '''
  # parameter type checking is done by fuzzysearch
  # the fuzzysearch algorithm works well as long as the longest word is used as the search
  # text.  If the shortest one is used, a perfect match can be achieved when text1 is a subset
  # of text2.  Going longest stops this from happening.
  if len(text1) > len(text2):
    return fuzzysearch(text2, text1, ngramlen, ignorecase)
  else:
    return fuzzysearch(text1, text2, ngramlen, ignorecase)

      

def fuzzycoljoin(table1, col1, table2, col2, matchpercent, ngramlen=3, ignorecase=True):
  '''Joins two tables based upon a fuzzy match of two column values.
     The resulting table has rows of both tables that match.  This method
     uses the Simple.join method to join where the fuzzymatch percentage
     is greater than or equal to the given matchpercent.
     
     Example:
       >>> table1 = Table([('Name', unicode), ('Address', unicode)], [['Daniel', '500 West Street'], ['Marge', '200 North Maple']])
       >>> table2 = Table([('Name', unicode), ('Address', unicode)], [['Steven', '500 West St.'], ['Denny', '600 Times Avenue']])
       >>> results = Simple.fuzzycolmatch(table1, 'Address', table2, 'Address', 0.30)
       >>> results.view()
       +--------+-----------------+--------+--------------+
       |  Name  |     Address     | Name_2 |     Add      |
       +--------+-----------------+--------+--------------+
       | Daniel | 500 West Street | Steven | 500 West St. |
       +--------+-----------------+--------+--------------+
     
     @param table1:        The first table
     @type  table1:        Table
     @param col1:          The column in the first table to join on
     @type  col1:          str
     @param table2:        The second table
     @type  table2:        Table
     @param col2:          The column in the second table to join on
     @type  col2:          str
     @param matchpercent:  To be joined, col1 and col2 must match by at least this percent
     @type  matchpercent:  float
     @param ngramlen:      The length of the ngrams to test.  Smaller ngrams provide greater tolerance and higher scores.  Larger ngrams provide smaller tolerance and lower scores.  An ngram of the length of searchtext provides an exact match only.  Default is 3.
     @type  ngramlen:      int
     @param ignorecase:    Whether to ignore letter case when searching.  Default is to ignore case.
     @type  ignorecase:    bool
     @return:              The joined table.
     @rtype:               Table
  '''
  check_valid_table(table1, col1)
  check_valid_table(table2, col2)
  assert isinstance(matchpercent, (types.IntType, types.FloatType)), 'Invalid match percent.  Please specify a value between 0.0 and 1.0.'
  assert matchpercent >= 0 and matchpercent <= 1, 'Invalid match percent.  Please specify a value between 0.0 and 1.0.'
  col1index = table1.deref_column(col1)
  col2index = table2.deref_column(col2)
  return join(table1, table2, "Simple.fuzzymatch(str(record1[" + str(col1index) + "]), str(record2[" + str(col2index) + "]), " + str(ngramlen) + ", " + str(ignorecase) + ") >= " + str(matchpercent))




def regex_match(pattern, value, ignorecase=False):
  '''Returns whether the given value matches the given regular
     expression pattern.  Regular expressions are a very powerful
     matching language that are available in many computer languages
     and programs.  This function uses the Python re module
     internally, and it follows the re rules.  See 
     http://docs.python.org/dev/howto/regex.html for a tutorial
     on regular expressions.
     
     The function only returns True or False.  To discover the actual
     matched text or groups within text, use the Python re module
     directly.
     
     Example 1: A simple email pattern to check validity
     >>> Simple.regex_match('^.+@.+\.\w{2,4}$', 'someone@myemail.info')
     True
     
     Example 2: Match a US phone number in format 1-###-###-####.
     >>> Simple.regex_match('1-\d{3}-\d{3}-\d{4}', '1-800-555-1234')
     True
     
     Example 3: Match various renditions of "P.O. Box"
     >>> pat = '^P(ost){0,1}\.{0,1} *O(ffice){0,1}\.{0,1} *Box$'
     >>> Simple.regex_match(pat, 'PO box', True)
     True
     >>> Simple.regex_match(pat, 'P.O. Box', True)
     True
     >>> Simple.regex_match(pat, 'Post Office Box', True)
     True
     >>> Simple.regex_match(pat, 'po box road', True)
     False

     @param pattern:    A regular expression pattern.
     @type  pattern:    str
     @param value:      The value to match against the pattern.  If not a string, it is converted automatically so matching is possible.
     @type  value:      str
     @param ignorecase: Whether to make the match case sensitive (the default) or not.
     @type  ignorecase: bool
     @return:           True if the value matches the pattern, False otherwise.
     @rtype:            bool
  '''
  assert isinstance(pattern, types.StringTypes), lang('The pattern must be a string type.')
  if not isinstance(value, types.StringTypes):
    value = unicode(value)
  if ignorecase:
    return re.search(pattern, value, re.IGNORECASE) != None
  else:
    return re.search(pattern, value) != None



def wildcard_match(pattern, value, ignorecase=False, fullmatch=True):
  '''Returns whether the given value matches the given wildcard pattern.
     This is the simplest way to match values to patterns in Picalo.  It
     supports only three special characters:
     
       - A question mark (?) matches a single letter (A-Z and a-z).
       - A pound sign (#) matches a single number (0-9).
       - A star (*) matches zero or more letters or numbers.
     
     Internally, the function turns the wildcard characters into the 
     appropriate regular expression and uses the Python re module
     to perform the match.
     
     This function only returns True or False.  To discover the actual
     matched text or groups within text, use the Python re module
     directly.
     
     For a more advanced and powerful method of pattern matching, see the
     Simple.regex_match function, which allows matching via the full
     regular expression language.

     Example 1: A simple email pattern to check validity
     >>> Simple.wildcard_match('?*@?*.??*', 'someone@myemail.info')
     True
     
     Example 2: Match a US or Canada phone number in format 1-###-###-####.
     >>> Simple.wildcard_match('1-###-###-####', '1-800-555-1234')
     True
     
     Example 3: A specific timestamp format:
     >>> Simple.wildcard_match('####-##-## ##:##:##.###', '2009-12-25 15:33:01.155')
     True
     
     @param pattern:    A regular expression pattern.
     @type  pattern:    str
     @param value:      The value to match against the pattern.  If not a string, it is converted automatically so matching is possible.
     @type  value:      str
     @param ignorecase: Whether to make the match case sensitive (the default) or not.
     @type  ignorecase: bool
     @param fullmatch:  Whether to force matchin of the entire value (the default) or to allow partial matching within the value string.
     @type  fullmatch:  bool
     @return:           True if the value matches the pattern, False otherwise.
     @rtype:            bool
  '''
  assert isinstance(pattern, types.StringTypes), lang('The pattern must be a string type.')
  if not isinstance(value, types.StringTypes):
    value = unicode(value)

  # convert to a regular expression
  regex = []
  for ch in pattern:
    if not ch in '01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-*?# ':
      regex.append('\\')
    regex.append(ch)
  pattern = ''.join(regex)
  for orig, repl in (
    ( '*', '\\w*' ),
    ( '?', '[A-Za-z]'  ),
    ( '#', '\\d'  ),
  ):
    pattern = pattern.replace(orig, repl)
   
  # ensure full match if asked for it
  if fullmatch and pattern[:1] != '^':
    pattern = '^' + pattern
  if fullmatch and pattern[-1:] != '$':
    pattern += '$'
    
  # use the regular expression function to do the match
  return regex_match(pattern, value, ignorecase)
  
  
  
  
  
  



  
  
  

