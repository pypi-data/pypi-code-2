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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOS E.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with Foobar; if not, write to the Free Software                            #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA        #
#                                                                                  #
####################################################################################
#
# Version 1.0
# Oct 11, 2003: Now uses expressions everywhere (to match Picalo's interface elsewhere)
#               Much better documentation
# Mar 09, 2003: pivot() was compiling results backwards.  Fixed this.
# Dec 08, 2003: Version 1.0.  Started this log.
#               Updated to work with Tables
#
#
####################################################################################

from picalo import Table, TableArray, Simple, show_progress, clear_progress, check_valid_table
from picalo.base.Global import run_tablearray, ensure_valid_variables, ensure_unique_list_value, make_unique_colnames, make_valid_variable
from picalo.base.Expression import PicaloExpression
import types


__doc__ = '''
The Crosstable module creates crosstables of data.  It is similiar to Excel's
powerful PivotTable function.  Crosstabling takes data that is in database format
and converts it to spreadsheet format, usually with summarization functions like
sum, average, etc.

The primary function of this module is pivot().  The other functions are more
advanced functions that show different levels of detail from the crosstabling
process.

Pivoting extremely large tables can take some time, depending upon your processor
speed and amount of memory.  Assuming you are running Picalo in GUI mode,
the functions will show a progress bar.
'''



# a listing of the public functions in this module (used by Manual.py)
__functions__ = (
  'pivot',
  'pivot_table',
  'pivot_map',
  'pivot_map_detail',
)




def pivot(table, col_fields, row_fields, expressions, delimiter='_'):
  '''Crosstables a Picalo table into a new table.  This routine is similar to
     Excel's PivotTable feature, but it is quite a bit more powerful (although
     not as easy to use).  
     
     The pivot function flattens the results into a two-dimensional table, with a 
     column for each expression of each data field.  Of all the pivot functions
     in the Crosstable module, this is the most like Excel's pivot table feature.
     
     There are no arbitrary limits on table size in Picalo, so you can pivot tables
     with many values (resulting in a significant number of rows and columns).
     The only limit on the number of resulting rows and columns is your memory.
     
     The first example shows a simple pivot on a single col_field, row_field,
     and single expression.  The second example shows a more complex pivot
     with multiple fields and expressions.  Note that the second example
     has some errors because the average function is being run on cells
     that have no values (divide by zero).
     
     Example 1:
        >>> # create a test table
        >>> data = Table([
        ...  ('Region', unicode),
        ...  ('Product', unicode),
        ...  ('Salesperson', unicode), 
        ...  ('Customer', unicode),
        ...  ('Amount', int),
        ... ],[
        ...  [ 'Rural','Computers',  'Mollie', 'Faiz',  500 ],
        ...  [ 'City',  'Monitors',  'Danny',  'Sheng', 700 ],
        ...  [ 'Rural', 'Mice',      'Mollie', 'Brian', 900 ],
        ...  [ 'City',  'Computers', 'Danny',  'Faiz',  300 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
        ...  [ 'City',  'Mice',      'Danny',  'Brian', 100 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Faiz',  200 ],
        ...  [ 'City',  'Computers', 'Danny',  'Sheng', 400 ],
        ... ])
        >>> # perform the pivot
        >>> ret = Crosstable.pivot(data, 'Salesperson', 'Product', 'sum(group["Amount"])')
        >>> ret.view()     
        +-----------+-------+--------+--------+
        |   Pivot   | Danny | Mollie | Totals |
        +-----------+-------+--------+--------+
        | Computers |   700 |    500 |   1200 |
        | Mice      |   100 |    900 |   1000 |
        | Monitors  |   700 |   1200 |   1900 |
        | Totals    |  1500 |   2600 |   4100 |
        +-----------+-------+--------+--------+     

     Example 2:
        >>> # create a test table
        >>> data = Table([
        ...  ('Region', unicode),
        ...  ('Product', unicode),
        ...  ('Salesperson', unicode), 
        ...  ('Customer', unicode),
        ...  ('Amount', int),
        ... ],[
        ...  [ 'Rural','Computers',  'Mollie', 'Faiz',  500 ],
        ...  [ 'City',  'Monitors',  'Danny',  'Sheng', 700 ],
        ...  [ 'Rural', 'Mice',      'Mollie', 'Brian', 900 ],
        ...  [ 'City',  'Computers', 'Danny',  'Faiz',  300 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
        ...  [ 'City',  'Mice',      'Danny',  'Brian', 100 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Faiz',  200 ],
        ...  [ 'City',  'Computers', 'Danny',  'Sheng', 400 ],
        ... ])
        >>> # perform the pivot
        >>> ret = Crosstable.pivot(data, ['Salesperson','Customer'], ['Product', 'Region'], ['sum(group["Amount"])','mean(group["Amount"])'])
        >>> ret.view()
        +-----------------+-------------------+-------------------+------------------+------------------+-------------------+-------------------+--------------------+--------------------+-------------------+-------------------+--------------------+--------------------+--------------+---------------+
        |      Pivot      | Danny_Brian_expr1 | Danny_Brian_expr2 | Danny_Faiz_expr1 | Danny_Faiz_expr2 | Danny_Sheng_expr1 | Danny_Sheng_expr2 | Mollie_Brian_expr1 | Mollie_Brian_expr2 | Mollie_Faiz_expr1 | Mollie_Faiz_expr2 | Mollie_Sheng_expr1 | Mollie_Sheng_expr2 | Totals_expr1 |  Totals_expr2 |
        +-----------------+-------------------+-------------------+------------------+------------------+-------------------+-------------------+--------------------+--------------------+-------------------+-------------------+--------------------+--------------------+--------------+---------------+
        | Computers_City  |                 0 |                 0 |              300 |              300 |               400 |               400 |                  0 |                  0 |                 0 |                 0 |                  0 |                  0 |          700 |         350.0 |
        | Computers_Rural |                 0 |                 0 |                0 |                0 |                 0 |                 0 |                  0 |                  0 |               500 |               500 |                  0 |                  0 |          500 |           500 |
        | Mice_City       |               100 |               100 |                0 |                0 |                 0 |                 0 |                  0 |                  0 |                 0 |                 0 |                  0 |                  0 |          100 |           100 |
        | Mice_Rural      |                 0 |                 0 |                0 |                0 |                 0 |                 0 |                900 |                900 |                 0 |                 0 |                  0 |                  0 |          900 |           900 |
        | Monitors_City   |                 0 |                 0 |                0 |                0 |               700 |               700 |                  0 |                  0 |                 0 |                 0 |                  0 |                  0 |          700 |           700 |
        | Monitors_Rural  |                 0 |                 0 |                0 |                0 |                 0 |                 0 |                  0 |                  0 |               200 |               200 |               1000 |              500.0 |         1200 |         400.0 |
        | Totals          |               100 |               100 |              300 |              300 |              1100 |             550.0 |                900 |                900 |               700 |             350.0 |               1000 |              500.0 |         4100 | 455.555555556 |
        +-----------------+-------------------+-------------------+------------------+------------------+-------------------+-------------------+--------------------+--------------------+-------------------+-------------------+--------------------+--------------------+--------------+---------------+

     @param table:         The Picalo table that will be crosstabled
     @type  table:         Table or TableArray
     @param col_fields:    A single field name or a list containing the field names of the fields used to group columns.
     @type  col_fields:    str/list
     @param row_fields:    A single field name or a list containing the field names of the fields used to group rows
     @type  row_fields:    str/list
     @param expressions:   A single expression or a list containing expressions used to do calculations on groupings; when the expression is evaluated, the keyword 'group' denotes the matching records for each cell
     @type  expressions:   str/list
     @param delimiter:     The character(s) to use to combine field values and expressions (for row and column headers)
     @type  delimiter:     str
     @return:              A new table containing the crosstabled results.  The last column and last row of the table contain the row and column totals
     @rtype:               Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Running pivot...', pivot, table, col_fields, row_fields, expressions, delimiter=delimiter)
  # table and field type checking is performed in Crosstable.__init__
  assert isinstance(delimiter, types.StringType), 'Invalid delimiter: ' + str(delimiter)
  try:
    ct = Crosstabler(table, row_fields, col_fields, expressions)
    rowlabels = ct.get_row_labels()
    rowlabels.sort()
    collabels = ct.get_col_labels()
    collabels.sort()
    
    # header (the columns)
    show_progress('Running pivot...', 0.0/len(rowlabels))
    columns = [ make_valid_variable('_'.join(_ensure_tuple(row_fields))) ] # first column is for the row keys
    for collabel in collabels:
      colname = delimiter.join([ unicode(name) for name in _ensure_tuple(collabel)])
      for i in range(len(ct.expressions)):       
        columns.append(ensure_unique_list_value(columns, make_valid_variable(colname + (len(ct.expressions) != 1 and (delimiter + 'expr' + str(i+1)) or ''))))
    for i in range(len(ct.expressions)):
      columns.append(ensure_unique_list_value(columns, make_valid_variable('Totals' + (len(ct.expressions) != 1 and (delimiter + 'expr' + str(i+1)) or ''))))
    table = Table(zip(make_unique_colnames(columns), [ unicode for i in columns ]))
  
    # add the data by row 
    for k, rowlabel in enumerate(rowlabels):
      show_progress('Running pivot...', float(k)/len(rowlabels))
      columns = []
      columns.append(delimiter.join([ str(name) for name in _ensure_tuple(rowlabel)]))
      for collabel in collabels:
        values = ct.get_cell_calculations(rowlabel, collabel)
        for i in range(len(ct.expressions)):
          columns.append(values[i])
      # row totals
      for total in ct.get_row_calculations(rowlabel):
        columns.append(total)
      table.append(columns)
      
    # add rows for totals
    columns = [ 'Totals' ]
    for collabel in collabels:
      values = ct.get_col_calculations(collabel)
      for i in range(len(ct.expressions)):
        columns.append(values[i])
    # grand totals
    for calc in ct.get_table_calculations():
      columns.append(calc)
    table.append(columns)
    
    return table  
  finally:
    clear_progress()
    

  
  
   
def pivot_table(table, col_fields, row_fields, expressions):
  '''Crosstables a Picalo table into a new table.  This routine is similar to
     Excel's PivotTable feature, but it is quite a bit more powerful (although
     not as easy to use).  
     
     This version creates does not flatten results to a two-dimensional table
     like the pivot function.  It is a more advanced way of pivoting than
     the pivot function because it creates a list of expressions results for 
     each cell.  In other words, the results table is not normalized, but
     contains lists within each cell that contain the results.  When a single
     col_field, row_field, and expression is given, this function produces the
     exact same results as pivot().
     
     This way of pivoting is useful if you want a single column for each col
     field value and a single row for each row field value.  Even if you provide
     multiple expressions and/or multiple data fields, you'll still only get one
     col/row match for a given value set.  The multiple expressions on the multiple
     data fields will be contained in a list in the cell for each row/col match.
     
     There are no arbitrary limits on table size in Picalo, so you can pivot tables
     with many values (resulting in a significant number of rows and columns).
     The only limit on the number of resulting rows and columns is your memory.
     
     The first example shows a simple pivot on a single col_field, row_field,
     and single expression.  The second example shows a more complex pivot
     with multiple fields and expressions.  Note that the second example
     has some errors because the average function is being run on cells
     that have no values (divide by zero).
     
     Example 1:
        >>> # create a test table
        >>> data = Table([
        ...  ('Region', unicode),
        ...  ('Product', unicode),
        ...  ('Salesperson', unicode), 
        ...  ('Customer', unicode),
        ...  ('Amount', int),
        ... ],[
        ...  [ 'Rural','Computers',  'Mollie', 'Faiz',  500 ],
        ...  [ 'City',  'Monitors',  'Danny',  'Sheng', 700 ],
        ...  [ 'Rural', 'Mice',      'Mollie', 'Brian', 900 ],
        ...  [ 'City',  'Computers', 'Danny',  'Faiz',  300 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
        ...  [ 'City',  'Mice',      'Danny',  'Brian', 100 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Faiz',  200 ],
        ...  [ 'City',  'Computers', 'Danny',  'Sheng', 400 ],
        ... ])
        >>> # perform the pivot
        >>> ret = Crosstable.pivot_table(data, 'Salesperson', 'Product', 'sum(group["Amount"])')
        >>> ret.view()
        +-----------+-------+--------+--------+
        |   Pivot   | Danny | Mollie | Totals |
        +-----------+-------+--------+--------+
        | Computers |   700 |    500 |   1200 |
        | Mice      |   100 |    900 |   1000 |
        | Monitors  |   700 |   1200 |   1900 |
        | Totals    |  1500 |   2600 |   4100 |
        +-----------+-------+--------+--------+        

     Example 2:
        >>> # create a test table
        >>> data = Table([
        ...  ('Region', unicode),
        ...  ('Product', unicode),
        ...  ('Salesperson', unicode), 
        ...  ('Customer', unicode),
        ...  ('Amount', int),
        ... ],[
        ...  [ 'Rural','Computers',  'Mollie', 'Faiz',  500 ],
        ...  [ 'City',  'Monitors',  'Danny',  'Sheng', 700 ],
        ...  [ 'Rural', 'Mice',      'Mollie', 'Brian', 900 ],
        ...  [ 'City',  'Computers', 'Danny',  'Faiz',  300 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
        ...  [ 'City',  'Mice',      'Danny',  'Brian', 100 ],
        ...  [ 'Rural', 'Monitors',  'Mollie', 'Faiz',  200 ],
        ...  [ 'City',  'Computers', 'Danny',  'Sheng', 400 ],
        ... ])
        >>> # perform the pivot
        >>> ret = Crosstable.pivot_table(data, ['Salesperson','Customer'], ['Product', 'Region'], ['sum(group["Amount"])','mean(group["Amount"])'])
        >>> ret.view()
        +------------------------+--------------------+-------------------+--------------------+---------------------+--------------------+---------------------+----------------------------+
        |         Pivot          | ('Danny', 'Brian') | ('Danny', 'Faiz') | ('Danny', 'Sheng') | ('Mollie', 'Brian') | ('Mollie', 'Faiz') | ('Mollie', 'Sheng') |           Totals           |
        +------------------------+--------------------+-------------------+--------------------+---------------------+--------------------+---------------------+----------------------------+
        |  ('Computers', 'City') |             (0, 0) |        (300, 300) |         (400, 400) |              (0, 0) |             (0, 0) |              (0, 0) |               (700, 350.0) |
        | ('Computers', 'Rural') |             (0, 0) |            (0, 0) |             (0, 0) |              (0, 0) |         (500, 500) |              (0, 0) |                 (500, 500) |
        |       ('Mice', 'City') |         (100, 100) |            (0, 0) |             (0, 0) |              (0, 0) |             (0, 0) |              (0, 0) |                 (100, 100) |
        |      ('Mice', 'Rural') |             (0, 0) |            (0, 0) |             (0, 0) |          (900, 900) |             (0, 0) |              (0, 0) |                 (900, 900) |
        |   ('Monitors', 'City') |             (0, 0) |            (0, 0) |         (700, 700) |              (0, 0) |             (0, 0) |              (0, 0) |                 (700, 700) |
        |  ('Monitors', 'Rural') |             (0, 0) |            (0, 0) |             (0, 0) |              (0, 0) |         (200, 200) |       (1000, 500.0) |              (1200, 400.0) |
        | Totals                 |         (100, 100) |        (300, 300) |      (1100, 550.0) |          (900, 900) |       (700, 350.0) |       (1000, 500.0) | (4100, 455.55555555555554) |
        +------------------------+--------------------+-------------------+--------------------+---------------------+--------------------+---------------------+----------------------------+     
     
     @param table:         The Picalo table that will be crosstabled
     @type  table:         Table or TableArray
     @param col_fields:    A single field name or a list containing the field names of the fields used to group columns.
     @type  col_fields:    str/list
     @param row_fields:    A single field name or a list containing the field names of the fields used to group rows
     @type  row_fields:    str/list
     @param expressions:   A single expression or a list containing expressions used to do calculations on groupings; when the expression is evaluated, the keyword 'group' denotes the matching records for each cell
     @type  expressions:   str/list
     @return:              A new table containing the crosstabled results.  The last column and last row of the table contain the row and column totals
     @rtype:               Table
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Running pivot...', pivot_table, table, col_fields, row_fields, expressions)
  # table and field type checking is performed in Crosstable.__init__
  try:
    ct = Crosstabler(table, row_fields, col_fields, expressions)
    rowlabels = ct.get_row_labels()
    rowlabels.sort()
    collabels = ct.get_col_labels()
    collabels.sort()
    
    # header (the columns)
    show_progress('Running pivot...', 0.0/len(rowlabels))
    columns = [ make_valid_variable('_'.join(_ensure_tuple(row_fields))) ] # first column is for the row keys
    for collabel in collabels:
      colname = make_valid_variable('_'.join([ unicode(name) for name in _ensure_tuple(collabel)]))
      columns.append(ensure_unique_list_value(columns, colname))
    totalsname = ensure_unique_list_value(columns, 'Totals')
    columns.append(totalsname)
    table = Table(zip(make_unique_colnames(columns), [ unicode for i in columns ]))
  
    # add the data by row
    for k, rowlabel in enumerate(rowlabels):
      show_progress('Running pivot...', float(k)/len(rowlabels))
      # add the row key (first column)
      columns = [ '_'.join([ unicode(name) for name in _ensure_tuple(rowlabel)]) ]
      # add the data cells
      for collabel in collabels:
        if len(ct.expressions) == 1: columns.append(ct.get_cell_calculations(rowlabel, collabel)[0])
        else: columns.append(ct.get_cell_calculations(rowlabel, collabel))
      # add the row subtotal
      if len(ct.expressions) == 1: columns.append(ct.get_row_calculations(rowlabel)[0])
      else: columns.append(ct.get_row_calculations(rowlabel))
      # append the columns to the rows list
      table.append(columns)
      
    # add a row for the column totals
    columns = [ totalsname ]
    for collabel in collabels:
      if len(ct.expressions) == 1: columns.append(ct.get_col_calculations(collabel)[0])
      else: columns.append(ct.get_col_calculations(collabel))
    # add the grand total
    if len(ct.expressions) == 1: columns.append(ct.get_table_calculations()[0])
    else: columns.append(ct.get_table_calculations())
    table.append(columns)
    
    # return the table
    return table
    
  finally:
    clear_progress()

  

def pivot_map(table, col_fields, row_fields, expressions):
  '''Matches all unique combinations of values in col_fields and row_fields with
     expressions run on the records that containing those unique values.
  
     This function is very similar to Grouping.summarize_by_value, only it is formatted
     in a way to make crossstabling possible.

     This is an advanced function that is used internally during the pivot technique.
     It is provided for advanced users who want to access the detail records during
     the crosstabling process.  It is one step in the process beyond pivot_map_detail.

     Most users should use Crosstable.pivot instead as it is more like Excel's pivot function.
     
     Example:
       >>> # create a test table
       >>> data = Table([
       ...  ('Region', unicode),
       ...  ('Product', unicode),
       ...  ('Salesperson', unicode), 
       ...  ('Customer', unicode),
       ...  ('Amount', int),
       ... ],[
       ...   [ 'Rural','Computers',  'Mollie', 'Faiz',  500 ],
       ...   [ 'City',  'Monitors',  'Danny',  'Sheng', 700 ],
       ...   [ 'Rural', 'Mice',      'Mollie', 'Brian', 900 ],
       ...   [ 'City',  'Computers', 'Danny',  'Faiz',  300 ],
       ...   [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
       ...   [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
       ...   [ 'City',  'Mice',      'Danny',  'Brian', 100 ],
       ...   [ 'Rural', 'Monitors',  'Mollie', 'Faiz',  200 ],
       ...   [ 'City',  'Computers', 'Danny',  'Sheng', 400 ],
       ... ])
       >>> # perform the pivot
       >>> ret = Crosstable.pivot_map(data, 'Salesperson', 'Product', 'sum(group["Amount"])')
       >>> ret
       {
         ('Monitors', 'Mollie'): (1200,), 
         ('Computers', 'Mollie'): (500,), 
         ('Mice', 'Danny'): (100,), 
         ('Computers', 'Danny'): (700,), 
         ('Mice', 'Mollie'): (900,), 
         ('Monitors', 'Danny'): (700,),
       }     
     
     @param table:         The Picalo table that will be crosstabled
     @type  table:         Table
     @param col_fields:    A single field name or a list containing the field names of the fields used to group columns.
     @type  col_fields:    str/list
     @param row_fields:    A single field name or a list containing the field names of the fields used to group rows
     @type  row_fields:    str/list
     @param expressions:   A single expression or a list containing expressions used to do calculations on groupings; when the expression is evaluated, the keyword 'group' denotes the matching records for each cell
     @type  expressions:   str/list
     @return:              A dictionary of each unique key (made up of row and column combinations) mapped to their matching records.
     @rtype:               dict
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Running pivot...', pivot_map, table, col_fields, row_fields, expressions)
  # table and field type checking is performed in Crosstable.__init__
  try:
    # note that this is almost exactly the same code as pivot_map_detail, except it runs get_cell_calculations
    ct = Crosstabler(table, row_fields, col_fields, expressions)
    dict = {}
    rowlabels = ct.get_row_labels()
    for k, rowlabel in enumerate(rowlabels):
      show_progress('Running pivot...', float(k)/len(rowlabels))
      for collabel in ct.get_col_labels():
        dict[(rowlabel, collabel)] = ct.get_cell_calculations(rowlabel, collabel)
    return dict
  finally:
    clear_progress()
    
 
def pivot_map_detail(table, col_fields, row_fields):
  '''Matches all unique combinations of values in col_fields and row_fields with
     Tables that contain only the records with those values.  This function is a
     "mega-select" function that is the basis of the crosstabling technique.
  
     Use this function if you just want to separate a Table in a number of 
     subtables -- one for each unique combination of col_fields and row_fields.
     
     This function is very similar to Grouping.stratify_by_value, only it is formatted
     in a way to make crossstabling possible.

     This is an advanced function that is used internally during the pivot technique.
     It is provided for advanced users who want to access the detail records during
     the crosstabling process.  It is the first step performed in a crosstable.

     Most users should use Crosstable.pivot instead as it is more like Excel's pivot function.
     
     Example:
       >>> # create a test table
       >>> data = Table([
       ...  ('Region', unicode),
       ...  ('Product', unicode),
       ...  ('Salesperson', unicode), 
       ...  ('Customer', unicode),
       ...  ('Amount', int),
       ... ],[
       ...   [ 'Rural','Computers',  'Mollie', 'Faiz',  500 ],
       ...   [ 'City',  'Monitors',  'Danny',  'Sheng', 700 ],
       ...   [ 'Rural', 'Mice',      'Mollie', 'Brian', 900 ],
       ...   [ 'City',  'Computers', 'Danny',  'Faiz',  300 ],
       ...   [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
       ...   [ 'Rural', 'Monitors',  'Mollie', 'Sheng', 500 ],
       ...   [ 'City',  'Mice',      'Danny',  'Brian', 100 ],
       ...   [ 'Rural', 'Monitors',  'Mollie', 'Faiz',  200 ],
       ...   [ 'City',  'Computers', 'Danny',  'Sheng', 400 ],
       ... ])
       >>> # perform the pivot
       >>> ret = Crosstable.pivot_map_detail(data, 'Salesperson', 'Product')
       >>> ret
       {
         ('Mollie', 'Computers'): <Table: 1 rows x 5 cols>, 
         ('Danny', 'Computers'):  <Table: 2 rows x 5 cols>, 
         ('Mollie', 'Monitors'):  <Table: 3 rows x 5 cols>, 
         ('Danny', 'Monitors'):   <Table: 1 rows x 5 cols>, 
         ('Danny', 'Mice'):       <Table: 1 rows x 5 cols>, 
         ('Mollie', 'Mice'):      <Table: 1 rows x 5 cols>
       }

     
     @param table:         The Picalo table that will be crosstabled
     @type  table:         Table
     @param col_fields:    A single field name or a list containing the field names of the fields used to group columns.
     @type  col_fields:    str/list
     @param row_fields:    A single field name or a list containing the field names of the fields used to group rows
     @type  row_fields:    str/list
     @return:              A dictionary of each unique key (made up of row and column combinations) mapped to Tables containing their matching records.
     @rtype:               dict
  '''
  if isinstance(table, TableArray):
    return run_tablearray('Running pivot...', pivot_map_detail, table, col_fields, row_fields)
  # table and field type checking is performed in Crosstable.__init__
  try:
    # note that this is almost exactly the same code as pivot_map, except it runs get_cell_records
    ct = Crosstabler(table, row_fields, col_fields, [])
    dict = {}
    rowlabels = ct.get_row_labels()
    for k, rowlabel in enumerate(rowlabels):
      show_progress('Running pivot...', float(k)/len(rowlabels))
      for collabel in ct.get_col_labels():
        dict[(rowlabel, collabel)] = ct.get_cell_records(rowlabel, collabel)
    return dict
  finally:
    clear_progress()
  
  
  
  
############################################################
###   Crosstabler class -- used internally in the functions

class Crosstabler:
  '''Crosstables data sets.  This is similar to Excel's PivotTable feature, although
     somewhat more powerful (although admittedly harder to use).
     
     The Crosstable object is not normally used directly.  The pivot, pivot_source,
     and pivot_map functions should be used instead.
     
     The Crosstable object is live, meaning that it calculates results just in time.
     Any changes to the table are reflected immediately.
  '''
  def __init__(self, table, row_fields, col_fields, expressions):
    '''Sets up the crosstable.  Don't use this object directly.  Call pivot, pivot_source,
       and pivot_map instead.
    
       @param table:        the source Picalo table (list of rows (which are lists themselves))
       @type  table:        Table
       @param row_fields:   a list containing the field names of the fields used to group rows
       @type  row_fields:   list
       @param col_fields:   a list containing the field names of the fields used to group columns
       @type  col_fields:   list
       @param expressions:  a list containing expressions for groupings; for each matching col/row value, each expression is run with the matching records in the "group" variable. 
       @type  expressions:  list
    '''
    # save the information, ensuring we have lists for the col, row, and expressions
    self.table = table
    self.row_fields = _ensure_tuple(row_fields)
    check_valid_table(table, *self.row_fields)
    self.col_fields = _ensure_tuple(col_fields)  
    check_valid_table(table, *self.col_fields)
    self.cell_fields = self.row_fields + self.col_fields
    self.expressions = [ PicaloExpression(expression) for expression in _ensure_tuple(expressions) ]


  def get_col_labels(self):
    '''Returns the unique labels for the column names.  If col_fields was a single value,
       the labels are single values.  If col_fields was a list of values, the labels
       are tuples of values.'''
    return self.table.index(*self.col_fields).keys()
    
    
  def get_row_labels(self):
    '''Returns the unique labels for the column names.  If row_fields was a single value,
       the labels are single values.  If row_fields was a list of values, the labels
       are tuples of values.'''
    return self.table.index(*self.row_fields).keys()
    
    
  def _get_records(self, indexfields, key):
    '''Returns the records that match the given key in the given index'''
    index = self.table.index(*indexfields)  # this is an efficient method, see the Table class.  It also automatically updates when the table changes.
    if len(indexfields) == 1:  # Table.index doesn't use tuples for 1-length tuple keys
      if index.has_key(key[0]):
        return Simple.select_records(self.table, index[key[0]])
      return Simple.select_records(self.table, [])
    else:
      if index.has_key(key):
        return Simple.select_records(self.table, index[key])
      return Simple.select_records(self.table, [])
    
    
  def _get_calculations(self, indexfields=None, key=None):
    '''Returns the calculations for records that match the given key in the given index'''
    if indexfields == None or key == None:  # if indexfields or key is None, then we're doing the entire table
      group = self.table
    else:
      group = self._get_records(indexfields, key)
    ret = []
    for exp in self.expressions:
      ret.append(exp.evaluate([{'group':group}]))
    return tuple(ret)
    
    
  def get_cell_records(self, rowlabel, collabel):
    '''Returns the records that match the given rowlabel and collabel unique values'''
    return self._get_records(self.cell_fields, _ensure_tuple(rowlabel) + _ensure_tuple(collabel))
    
    
  def get_cell_calculations(self, rowlabel, collabel):
    '''Returns the cell calculations for the cell with the given row label unique value
       and column label unique value'''
    return self._get_calculations(self.cell_fields, _ensure_tuple(rowlabel) + _ensure_tuple(collabel))
    
    
  def get_row_records(self, rowlabel):
    '''Returns the records that match the given rowlabel unique value'''
    return self._get_records(self.row_fields, _ensure_tuple(rowlabel))

    
  def get_row_calculations(self, rowlabel):
    '''Returns the cell calculations for the row with the given row label'''
    return self._get_calculations(self.row_fields, _ensure_tuple(rowlabel))
    
    
  def get_col_records(self, collabel):
    '''Returns the records that match the given collabel unique value'''
    return self._get_records(self.col_fields, _ensure_tuple(collabel))

    
  def get_col_calculations(self, collabel):
    '''Returns the cell calculations for the col with the given row label'''
    return self._get_calculations(self.col_fields, _ensure_tuple(collabel))
    
    
  def get_table_calculations(self):
    '''Returns the grand total calculations for the entire table'''
    return self._get_calculations()
    
    
    
#########################################
###   Helper functions

def _ensure_tuple(var):
  '''Ensures the given variable is a tuple'''
  if isinstance(var, types.TupleType):
    return var
  elif isinstance(var, types.ListType):
    return tuple(var)
  return tuple((var,))  # without the comma, strings are split into characters
  
  
      
