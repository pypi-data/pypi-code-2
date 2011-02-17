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
# Jun 20, 2005: Changed "Group by" to "Stratify by" throughout.
# May 26, 2005: Changed all the lambda stuff over to expressions that go through eval
# Jan 14, 2003: Fixed minor errors in the documentation for summary methods
# Dec 14, 2003: Version 1.00.  Refactored the code.  Included the functions
#               from the previous Summarize module.
# Dec 08, 2003: Version 0.30.  Started this log.
#                  
#
#
####################################################################################

__doc__ = '''
The Grouping module contains functions that stratify and summarize records in different ways.
Grouping is a basic fraud detection method that helps generate norms and compare
records against those norms.  Further, it splits data sets into individual groups
that should be analyzed separately.

The Grouping module only stratifiess a table into many tables.  It doesn't do any summarization
of values.  All detail data are still in the tables.

The summary routines not only stratifies data on key, but also summarizes the detail
tables using sum, mean, and other statistical routines.  You get only one table returned
from Summarize.  Stratifying gives the intermediate result -- the full detail in many tables. 

For those familiar with SQL, the summarize routines are similar to the GROUP BY keyword.  Groups
are collapsed into summary records and a single table is returned.  The stratifying functions are 
similar to running one query to retrieve all unique key values, followed by a query to retrieve 
the records that match each key value.  The result is many tables (one per unique key value).
'''



# a listing of the public functions in this module (used by Manual.py)
__functions__ = [
  'stratify',
  'stratify_by_value',
  'stratify_by_expression',
  'stratify_by_step',
  'stratify_by_date',
  'summarize',
  'summarize_by_expression',
  'summarize_by_value',
  'summarize_by_step',
  'summarize_by_date',
]



import Simple
import math, sys, types, datetime
from picalo import Table, TableArray, show_progress, clear_progress, check_valid_table
from picalo.base.Global import run_tablearray, ensure_valid_variables, make_unique_colnames, ensure_unique_colname
from picalo.base.Expression import PicaloExpression
from picalo.base.Calendar import DateDelta, Date, DateTime


def stratify(table, number_of_groups):
  '''Stratifies a Picalo table into a specified number of sub-tables.
     The table should be sorted appropriately before this function is called.
     This function does not modify the underlying table.
     
     The start and end record indices are recorded in table.startvalue
     and table.endvalue.  See the example for more information.
     
     Example:
       >>> table = Table([('col000', int), ('col001', int)], [[1,1],[2,2],[3,3]])
       >>> groups = Grouping.stratify(table, 2)
       >>> print groups[0].startvalue, groups[0].endvalue
       0, 1
       >>> groups[0].view()
       +--------+--------+
       | col000 | col001 |
       +--------+--------+
       |      1 |      1 |
       |      2 |      2 |
       +--------+--------+
       >>> print groups[1].startvalue, groups[1].endvalue
       3, 3
       >>> groups[1].view()
       +--------+--------+
       | col000 | col001 |
       +--------+--------+
       |      3 |      3 |
       +--------+--------+
     
     @param table:            The table to be stratified
     @type  table:            Table
     @param number_of_groups: The number of sub-tables to create
     @type  number_of_groups: int
     @return:                 A list of new tables
     @rtype:                  TableArray
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Stratifying...', stratify, table, number_of_groups)
  check_valid_table(table)
  assert isinstance(number_of_groups, types.IntType), 'The number of groups must be an integer.'
  try:
    # make the groups
    groups = TableArray()
    span = int(math.ceil( float(len(table)) / number_of_groups ))
    for i in range(0, len(table), span):
      show_progress('Stratifying...', float(i) / len(table))
      g = table[i: i+span]
      g.startvalue = i
      g.endvalue = i+span-1
      groups.append(g)
    return groups
  finally:
    clear_progress()
  

def stratify_by_value(table, *cols):
  '''Stratifies a Picalo table by composite key (combination of values in the cols columns).
     A new table is created for each unique composite key, resulting in a list of tables.
     This function does not modify the underlying table.
     
     Each key is recorded as the start and end values of each group.
     See the example for more information.
     
     Example:
        >>> table = Table([('col000', int), ('col001', int)], [['Dan',10],['Sally',10],['Dan',11]])
        >>> groups = Grouping.stratify_by_value(table, 'col000')
        >>> groups[0].view()
        +--------+--------+
        | col000 | col001 |
        +--------+--------+
        | Dan    |     10 |
        | Dan    |     11 |
        +--------+--------+
        >>> groups[1].view()
        +--------+--------+
        | col000 | col001 |
        +--------+--------+
        | Sally  |     10 |
        +--------+--------+
     
     @param table:  The table to be stratified
     @type  table:  Table
     @param cols:   The remaining parameters are the column names/indices to stratify by
     @type  cols:   str
     @return:       A list of new tables, each table containing rows with the same key values.
     @rtype:        TableArray
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Stratifying...', stratify_by_value, table, *cols)
  check_valid_table(table, *cols)
  try:
    index = table.index(*cols)
    # put the records into the groups in the index
    groups = TableArray()
    keys = index.keys()
    keys.sort()
    for i, key in enumerate(keys):
      show_progress('Stratifying...', float(i) / len(keys))
      group = Table(table.columns, [ table[i] for i in index[key] ])
      group.startvalue = group.endvalue = key
      groups.append(group)
    return groups  
  finally:
    clear_progress()
  
  
def stratify_by_expression(table, expression):
  '''Stratifies a table based upon the return value from an expression.
     For each record in the table, the expression is evaluated with the following variables:
       1. startrecord => the starting record of the current group.
       2. record => the current record being evaluated.
     If the expression evaluates to True, rec is placed in a new group and becomes startrec
     If the expression evaluates to False, rec is placed in the current group.

     The start and end record indices are recorded in table.startvalue
     and table.endvalue.  See the example for more information.
     
     Example (starts a new group on each odd value in column 1):
       >>> table1 = Table([('col000', int)], [[1],[2],[3],[4]])
       >>> groups = Grouping.stratify_by_expression(table1, "record[0] % 2.0 == 1.0")
       >>> print groups[0].startvalue, groups[0].endvalue
       0, 1
       >>> groups[0].view()
       +--------+
       | col000 |
       +--------+
       |      1 |
       |      2 |
       +--------+
       >>> print groups[1].startvalue, groups[1].endvalue
       3, 4
       >>> groups[1].view()
       +--------+
       | col000 |
       +--------+
       |      3 |
       |      4 |
       +--------+     
     
     @param table:       The table to be stratified
     @type  table:       Table
     @param expression:  An expression that evaluates the current record and returns whether a new group should be started
     @type  expression:  str
     @return:            A list of new tables, each containing rows from table that were grouped together
     @rtype:             TableArray
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Stratifying...', stratify_by_expression, table, expression)
  check_valid_table(table)
  assert isinstance(expression, (types.StringType, types.UnicodeType, PicaloExpression)), 'Invalid expression: ' + str(expression)
  try:
    groups = TableArray()
    startrec = None 
    pe = PicaloExpression(expression)
    for i in range(len(table)):
      show_progress('Stratifying...', float(i) / len(table))
      currentrec = table[i]
      if startrec == None or pe.evaluate([{'startrecord':startrec, 'record':currentrec, 'recordindex':i}, currentrec, startrec]):
        currentgroup = Table(table.columns)
        currentgroup.startvalue = i
        groups.append(currentgroup)
        startrec = currentrec
      currentgroup.endvalue = i
      currentgroup.append(currentrec)
    return groups
  finally:
    clear_progress()
  

def stratify_by_step(table, col, step):
  '''Stratifies a table based upon the value of col.  Each time
     the value of col jumps > step, a new group is started.
  
     The table should be sorted correctly *before* this method is called.
     This method simply runs through the table records sequentially.
     
     The start and end values of each group are recorded in the table object
     since they may be different than the actual start and end column values.
     See the example for more information.
     
     Records are stratified where startvalue >= record[col] < endvalue.
  
     Example:    
       >>> table1 = Table([('col000', int), ('col001', int)], [[1,1], [2,2], [5.9,3], [6,1], [8,2], [16,1]])
       >>> groups = Grouping.stratify_by_step(table1, 0, 5)
       >>> print groups[0].startvalue, groups[0].endvalue
       1, 6
       >>> groups[0].view()
       +--------+--------+
       | col000 | col001 |
       +--------+--------+
       |      1 |      1 |
       |      2 |      2 |
       |    5.9 |      3 |
       +--------+--------+
       >>> print groups[1].startvalue, groups[1].endvalue
       6, 11
       >>> groups[1].view()
       +--------+--------+
       | col000 | col001 |
       +--------+--------+
       |      6 |      1 |
       |      8 |      2 |
       +--------+--------+
       >>> print groups[2].startvalue, groups[2].endvalue
       11, 16
       >>> groups[2].view()
       +--------+--------+
       | col000 | col001 |
       +--------+--------+
       +--------+--------+
       >>> print groups[3].startvalue, groups[3].endvalue
       16, 21
       >>> groups[3].view()
       +--------+--------+
       | col000 | col001 |
       +--------+--------+
       |     16 |      1 |
       +--------+--------+   
       
     @param table:  The table to be stratified
     @type  table:  Table
     @param col:    The column to use to step by
     @type  col:    str
     @param step:   The step value that starts a new group
     @type  step:   int
     @return:       A list of new tables, each containing rows from table that were stratified together
     @rtype:        TableArray
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Stratifying...', stratify_by_step, table, col, step)
  check_valid_table(table, col)
  if len(table) == 0:
    return TableArray([table])
  if isinstance(step, datetime.timedelta):
    assert table.column(col).get_type() in (Date, DateTime), 'The column to group by must be DateTime or Date type.'
    assert isinstance(step, datetime.timedelta), 'The step must be a DateDelta or TimeDelta type.'
  else:
    assert table.column(col).get_type() in (types.IntType, types.FloatType, types.LongType), 'The column to group by must be a number type.'
    assert isinstance(step, (types.IntType, types.FloatType, types.LongType)), 'The step must be number type such as int, long, or float.'
  try:
    Simple.sort(table, True, col)
    groups = TableArray()
    endval = None
    currentgroup = None
    for i, rec in enumerate(table):
      show_progress('Stratifying...', float(i) / len(table))
      while endval == None or rec[col] >= endval:
        currentgroup = Table(table.columns)
        groups.append(currentgroup)
        if endval == None: 
          currentgroup.startvalue = rec[col]
          endval = rec[col] + step
        else: 
          currentgroup.startvalue = endval
          endval += step
        currentgroup.endvalue = endval
      currentgroup.append(rec)
    return groups  
  finally:
    clear_progress()
    
  
    
def stratify_by_date(table, col, duration):
  '''Stratifies the table rows into specific groups by date ranges.  This function
     is useful to split a table into ranges such as two-week periods (useful for 
     analyzing timecard and invoice databases).
     
     Aging can also be done by sorting the table in reverse (newest to oldest dates)
     and using a negative duration.
     
     The start and end values of each group are recorded in the table object
     since they may be different than the actual start and end column values.
     See the example for more information.

     See the base.Calendar module for more information about time durations.
     
     Example:
       >>> table = Table([('col000', DateTime)], [
       ...   [DateTime(2000,1,1)],
       ...   [DateTime(2000,1,13)],
       ...   [DateTime(2000,1,14)],
       ...   [DateTime(2000,1,15)]
       ... ])
       >>> groups = Grouping.stratify_by_date(table, 0, DateDelta(7))
       >>> print groups[0].startvalue, groups[0].endvalue
       2000-01-01 00:00:00, 2000-01-08 00:00:00
       >>> groups[0].view()
       +------------------------+
       |         col000         |
       +------------------------+
       | 2000-01-01 00:00:00.00 |
       +------------------------+
       >>> print groups[1].startvalue, groups[1].endvalue
       2000-01-08 00:00:00, 2000-01-15 00:00:00
       >>> groups[1].view()
       +------------------------+
       |         col000         |
       +------------------------+
       | 2000-01-13 00:00:00.00 |
       | 2000-01-14 00:00:00.00 |
       +------------------------+
       >>> print groups[2].startvalue, groups[2].endvalue
       2000-01-15 00:00:00, 2000-01-22 00:00:00
       >>> groups[2].view()
       +------------------------+
       |         col000         |
       +------------------------+
       | 2000-01-15 00:00:00.00 |
       +------------------------+
     
  
     @param table:     The table to be stratified
     @type  table:     Table
     @param col:       The column to stratify by.  
     @type  col:       str
     @param duration:  The number of days or seconds to put into each group.
     @type  duration:  int
     @return:          A list of new tables, each containing rows from table that were stratified together
     @rtype:            TableArray
  '''
  # this really isn't any different than stratify by step, just the data types
  if not isinstance(duration, datetime.timedelta):
    duration = DateDelta(duration)
  return stratify_by_step(table, col, duration)
  
  
  

###############################################
###   Summarize functions

def summarize(groups, **expressions):
  '''Summarizes a sequence of groups by evaluating a series of expressions on each group.
     The result is a single table with one row representing each group in groups.
     This is analogous to the SQL GROUP BY command.

     Each item in expressions should be an expression that summarizes a group.
     It must evaluate to a single value summarizing the entire table.
     Most expressions will probably only summarize a single column as is done in the
     example.  Use the Table['colname'] method do get the desired column.
     
     Example:
       >>> from picalo.lib import stats
       >>> table = Table([('col000', int), ('col001', int), ('col002', int')], [[1,1,1],[1,1,2],[2,1,2],[2,1,3]])
       >>> groups = Grouping.stratify_by_value(table, 0, 1)
       >>> summary = Grouping.summarize(groups, sum="sum(group['col002'])", avg="stats.mean(group['col002'])")
       >>> summary.view()
       +------------+----------+-----+-----+
       | StartValue | EndValue | sum | avg |
       +------------+----------+-----+-----+
       |     (1, 1) |   (1, 1) |   3 | 1.5 |
       |     (2, 1) |   (2, 1) |   5 | 2.5 |
       +------------+----------+-----+-----+
     
     @param groups:         A TableArray of groups, probably created by one of the stratify_by_... routines.
     @type  groups:         TableArray
     @param expressions:    One or more colname=expression pairs to summarize by.
     @return:               A single table containing the summaries of the groups.
     @rtype:                Table
  '''
  assert isinstance(groups, TableArray), 'The groups variable must be a TableArray.'
  # if all members are TableArrays, we need to recurse
  for sub in groups:
    if not isinstance(sub, TableArray):
      break
  else:
    return run_tablearray('Summarizing...', summarize, groups, **expressions)
  # check the column names and expressions
  for colname, expression in expressions.items():
    assert isinstance(colname, types.StringTypes), 'Invalid column name given to an expression: ' + str(colname)
    assert isinstance(expression, (types.StringType, types.UnicodeType, PicaloExpression)), 'Invalid expression: ' + str(expression)
  # run the summary
  try:
    headings = make_unique_colnames(ensure_valid_variables([ 'StartValue', 'EndValue' ] + expressions.keys()))
    coltypes = [ unicode, unicode ] + [ float for i in headings ]
    results = Table(zip(headings, coltypes))
    for expname, exp in expressions.items():  # convert to picalo expressions for speed
      expressions[expname] = PicaloExpression(exp)
    for i in range(len(groups)):
      show_progress('Summarizing...', float(i) / len(groups))
      group = groups[i]
      rec = results.append()
      if hasattr(group, 'startvalue'):
        rec['StartValue'] = group.startvalue
      if hasattr(group, 'endvalue'):
        rec['EndValue'] = group.endvalue
      for expname, exp in expressions.items():
        rec[expname] = exp.evaluate([{'group':group}])
    return results
  finally:
    clear_progress()
  
  
  
########################################################################
###  The remaining summarize_by_* are just convenience functions that 
###  first call the stratify_by_... function and then summarize the groups.
###  These functions are provided mostly to included summarization in
###  the standard documentation and to ease summarization for users.
  
def summarize_by_value(table, *cols, **expressions):
  '''Stratifies a Picalo table by composite key (combination of values in the col_list columns).
     A new table is created for each unique composite key, resulting in a list of tables.
     The function then summarizes the list of groups by running a series of expressions on
     each group.  The result is single table with one row representing each group.
     This is analogous to the SQL GROUP BY command.  This function does not modify the 
     underlying table.
     
     Each item in expressions should be an expression that summarizes a group.
     It must evaluate to a single value summarizing the entire table.
     Most expressions will probably only summarize a single column as is done in the
     example.  Use the Table['colname'] method do get the desired column.
     
     Example:
      >>> from picalo import *
      >>> from picalo.lib import stats
      >>> table = Table([('col000', unicode), ('col001', int), ('col002', int)], [
      ...      ['Dan',10,8],
      ...      ['Sally',12,12],
      ...      ['Dan',11,15], 
      ...      ['Sally',12,14], 
      ...      ['Dan',11,16], 
      ...      ['Sally',15,15], 
      ...      ['Dan',16,15], 
      ...      ['Sally',13,14]])
      >>> results = Grouping.summarize_by_value(table, 'col000', 
      ...      sum="sum(group['col001'])", 
      ...      correlation="stats.spearmanr(list(group['col001']), list(['col002']))")
      >>> results.view()
      +-------+-----+--------------------------------------------+
      | Value | sum |                correlation                 |
      +-------+-----+--------------------------------------------+
      | Dan   |  48 | (0.55000000000000004, 0.45000000000651308) |
      | Sally |  52 |  (0.84999999999999998, 0.1499999999962324) |
      +-------+-----+--------------------------------------------+
      >>> # the first number in the correlation is the statistic, second number is the p-value

     
     @param table:          The table to be summarized
     @type  table:          Table
     @param cols:           One or more columns to summarize with the given expressions.
     @param expressions:    One or more colname=expression pairs to summarize by.
     @return:               A single table containing the summaries of the groups.
     @rtype:                Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Summarizing...', summarize_by_value, table, *cols, **expressions)
  check_valid_table(table, *cols)
  summary = summarize(stratify_by_value(table, *cols), **expressions)
  try:
    show_progress('Formatting...', 0 / 2)
    summary.delete_column('EndValue')
    show_progress('Formatting...', 1 / 2)
    summary.column('StartValue').set_name(ensure_unique_colname(summary, '_'.join([ table.column(col).name for col in cols ])))
  finally:
    clear_progress()
  return summary

  
def summarize_by_expression(table, stratifying_expression, **expressions):
  '''Summarizess a table based upon the return value from expressions.
     The function then summarizes the list of groups by running a series of functions on
     each group.  The result is single table with one row representing each group.
     This is analogous to the SQL GROUP BY command.  This function does not modify the 
     underlying table.
     
     Each item in expressions should be an expression that summarizes a group.
     It must evaluate to a single value summarizing the entire table.
     Most expressions will probably only summarize a single column as is done in the
     example.  Use the Table['colname'] method do get the desired column.

     @param table:                   The table to be summarized
     @type  table:                   Table
     @param stratifying_expression:  An expression that evaluates the current record and returns whether a new group should be started
     @type  stratifying_expression:  str
     @param expressions:             One or more colname=expression pairs to summarize by.
     @return:                        A single table containing the summaries of the groups.
     @rtype:                         Table
  '''
  return summarize(stratify_by_expression(table, stratifying_expression), **expressions)

def summarize_by_step(table, col, step, **expressions):
  '''Summarizes a table based upon the value of col.  Each time
     the value of col jumps > step, a new group is started.
     The function then summarizes the list of groups by running a series of functions on
     each group.  The result is single table with one row representing each group.
     This is analogous to the SQL GROUP BY command.  This function does not modify the 
     underlying table.
  
     Each item in expressions should be an expression that summarizes a group.
     It must evaluate to a single value summarizing the entire table.
     Most expressions will probably only summarize a single column as is done in the
     example.  Use the Table['colname'] method do get the desired column.
     
     Example:    
       >>> from picalo.lib import stats
       >>> table1 = Table([('col000', int), ('col001', int)], [[1,1], [2,2], [5.9,3], [6,1], [8,2], [16,1]])
       >>> summary = Grouping.summarize_by_step(table1, 0, 5, count="len(group)")
       >>> summary.view()
       +------------+----------+-------+
       | StartValue | EndValue | count |
       +------------+----------+-------+
       |          1 |        6 |     3 |
       |          6 |       11 |     2 |
       |         11 |       16 |     0 |
       |         16 |       21 |     1 |
       +------------+----------+-------+

     @param table:          The table to be summarized
     @type  table:          Table
     @param col:            The column to stratify by.
     @type  col:            str
     @param step:           The step value that starts a new group
     @type  step:           float
     @param expressions:    One or more colname=expression pairs to summarize by.
     @return:               A single table containing the summaries of the groups.
     @rtype:                Table
  '''
  return summarize(stratify_by_step(table, col, step), **expressions)
  
def summarize_by_date(table, col, num_days_in_groups, **expressions):
  '''Summarizes the table rows into specific groups by date ranges.  
     The function then summarizes the list of groups by running a series of functions on
     each group.  The result is single table with one row representing each group.
     This is analogous to the SQL GROUP BY command.  This function does not modify the 
     underlying table.
     
     Aging can also be done by sorting the table in reverse (newest to oldest dates)
     and using a negative num_days_in_groups.
     
     Each item in expressions should be an expression that summarizes a group.
     It must evaluate to a single value summarizing the entire table.
     Most expressions will probably only summarize a single column as is done in the
     example.  Use the Table['colname'] method do get the desired column.
     
     Example:
       >>> table = Table([('col000', DateTime), ('col001', int), ('col002', int)], [
       ...   [DateTime(2000,1,1)],
       ...   [DateTime(2000,1,13)],
       ...   [DateTime(2000,1,14)],
       ...   [DateTime(2000,1,15)]
       ... ])
       >>> summary = Grouping.summarize_by_date(table, 0, TimeDelta(7), first="group[0][0]", last="group[-1][0]")
       >>> summary.view()
       +---------------------+---------------------+---------------------+---------------------+
       |      StartValue     |       EndValue      |         last        |        first        |
       +---------------------+---------------------+---------------------+---------------------+
       | 2000-01-01 00:00:00 | 2000-01-08 00:00:00 | 2000-01-01 00:00:00 | 2000-01-01 00:00:00 |
       | 2000-01-08 00:00:00 | 2000-01-15 00:00:00 | 2000-01-14 00:00:00 | 2000-01-13 00:00:00 |
       | 2000-01-15 00:00:00 | 2000-01-22 00:00:00 | 2000-01-15 00:00:00 | 2000-01-15 00:00:00 |
       +---------------------+---------------------+---------------------+---------------------+

     @param table:              The table to be summarized
     @type  table:              Table
     @param col:                The column to stratify by.
     @type  col:                str
     @param num_days_in_groups: The number of days or seconds to put into each group.
     @type  num_days_in_groups: int
     @param expressions:        One or more colname=expression pairs to summarize by.
     @return:                   A single table containing the summaries of the groups.
     @rtype:                    Table
  '''
  return summarize(stratify_by_date(table, col, num_days_in_groups), **expressions)  
