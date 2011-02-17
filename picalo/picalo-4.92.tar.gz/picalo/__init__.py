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
# The modules in the base/ directory are globally imported into the Python namespace
# when you run "from picalo import *".  They are separated here into different files
# for convenience (rather than putting it all in __init__.py).  See picalo/__init__.py
# for how they are globally imported into Picalo.
#                                                                                  
####################################################################################

# this documentation is placed on the top page of the epydoc API documentation
__doc__ = '''
Picalo is a Python library to help anyone who works with data files, 
especially those who work with data in relational/spreadsheet format.  
It is primarily created for investigators and auditors search through 
data sets for anomalies, trends, ond other information, but it is 
generally useful for any type of data or text files.

Picalo is different from NumPy/Numarray in that it is meant for
heterogeneous data rather than homogenous data.  In NumPy, you
have an array (table) of the same type--all ints, for example.
In Picalo, you have a table made up of different column types,
very similar to a database.

One of Picalo's primary purposes is making relational
databases easier to work with.  Once you have a Picalo table, 
you can add, move, or delete columns; work with records (horizontal
slices of the data); select and group records in various ways;
and run analyses on tables.  Picalo includes adapters for popular
databases, and it provides a Query object that make queries seem
just like regular Tables (except they are live from the database).

If you work with relational databases, delimited (CSV/TSV) files, 
EBCDIC files, MS Excel files, log files, text files, or other 
heterogeneous datasets, Picalo might make your life easier.

Picalo is programmed to be as Pythonic as possible.  It's core objects--
tables, columns, records--they act like lists.  A column is a list of cells.
A record is a list of cells.  A table is a list of records.  Tables can be 
sorted via the sort function, just like the Sorting HowTo shows.  The return
values of almost all functions are new tables, so functions can be chained
together like pipes in Unix.

Picalo includes an optional Project object that stores tables in
Zope Object DB files.  When Projects are used, Picalo automatically
swaps records in and out of memory as needed to ensure efficient use of 
resources.  Projects allow Picalo to work with essentially an unlimited
amount of data.

The project was started in 2003 by Conan C. Albrecht, a professor
in Information Systems at Brigham Young University.  Conan remains
the primary developer of Picalo.

Picalo is released in two formats.  First, as a pure-Python library that is used 
by simply "import picalo" or "from picalo import *" in any Python script.  
Python programmers will be primarily interested in the library
version.  This format is installed in the typical Python fashion, either
as an .egg via setuptools, or via "python setup.py install" from
the source.

Second, Picalo is released as a standalone, wx-Python-based GUI environment that allow
end users to access the Picalo libraries. This version is packaged as a Windows setup.exe file, Mac
application bundle, and Linux rpm and deb files.  The user
may not realize Python is even being used when running the
full application environment.
</ol>

Enjoy!  Please report any bugs to me.  I also welcome additions to the toolkit.
  
Dr. Conan C. Albrecht
conan@warp.byu.edu
http://www.picalo.org/
'''



########################################################
###   Imports

import sys, types, re, inspect, os, os.path, threading, decimal



######################################################
###   Value formatting and parsing routines

format_cache = {}
format_parser = re.compile('^([^#0]*?)([#0]*?),{0,1}([0#]*)\.{0,1}(0*)(%{0,1})(e\+(0+)){0,1}$', re.IGNORECASE)

class NumberFormat:
  def __init__(self, format):
    '''Initializes the NumberFormat from the given format'''
    self.prefix = None
    self.decimalplaces = None
    self.commapos = None
    self.percent = False
    self.sciplaces = None
    result = format_parser.search(format.strip())
    assert result != None, 'Invalid number format: %s' % format
    if result.group(1):
      self.prefix = result.group(1)
    if result.group(2) and result.group(3):
      self.commapos = len(result.group(3))
    if result.group(3) and result.group(3)[-1] == '0':
      self.decimalplaces = 0
    if result.group(4):
      self.decimalplaces = len(result.group(4))
    if result.group(5):
      self.percent = True
    if result.group(6):
      self.sciplaces = len(result.group(7))

    
  def format_value(self, value, typ):
    '''Returns the value as a formatted string'''
    # scientific notation
    if self.sciplaces != None:
      val = float(value)
      exp = 0
      if abs(val) >= 1:
        while abs(val) >= 10:
          val = val / 10
          exp += 1
        return ('%0.' + unicode(self.sciplaces) + 'fE+%i') % (val, exp)
      else:  # less than 1
        while abs(val) < 1:
          val = val * 10
          exp += 1
        return ('%0.' + unicode(self.sciplaces) + 'fE-%i') % (val, exp)
    
    # if we're adding a percent, times the number by 100
    value2 = decimal.Decimal(unicode(value))
    if self.percent:
      value2 = value2 * 100
      
    # round the number to the specified number of decimal places
    # the decimal.quantize method isn't working for some reason, so I'll temporarily use round for now
    if self.decimalplaces != None:
      value2 = decimal.Decimal(unicode(round(value2, self.decimalplaces)))

    # get the parts of the number
    parts = value2.as_tuple()
    if parts[2] == 0:
      intpart = [ unicode(s) for s in parts[1] ]
      decpart = []
    else:
      intpart = [ unicode(s) for s in parts[1][:parts[2]] ]
      decpart = [ unicode(s) for s in parts[1][parts[2]:] ]
    
    # do the integer part
    if self.commapos:
      i = len(intpart) - 1
      x = 0
      while i > 0:
        x += 1
        if x  % self.commapos == 0:
          intpart.insert(i, ',')
        i -= 1
      ret = ''.join(intpart)
    else:
      ret = unicode(int(value))
    
    # do the decimal part
    if self.decimalplaces == None and not typ in (int, long):
      ret += '.' + ''.join([ unicode(s) for s in decpart ])
    elif self.decimalplaces > 0:
      while len(decpart) < self.decimalplaces:
        decpart.append('0')
      ret += '.' + ''.join([ unicode(s) for s in decpart ])
      
    # add the percent symbol if we've been asked to
    if self.percent:
      ret += '%'
    
    # add the prefix
    if self.prefix:
      ret = self.prefix + ret
      
    # return the string
    return ret
    

def format_value_from_type(value, typ, format=None):
  '''Utility method that does the actual formatting.  See the Column.set_format method
     for a description of the format used here.'''
  # short circuit if there's an error here
  if isinstance(value, error):
    return unicode(value)
    
  # if the None value
  if value == None:
    return '<N>'
     
  # if a date format
  if typ in (Date, DateTime):
    if format != None:
      return value.strftime(format)
    elif typ == Date:
      return value.strftime("%Y-%m-%d")
    elif typ == DateTime:
      return value.strftime("%Y-%m-%d %H:%M:%S")
  
  # if a number format
  if typ in (int, long, float, number, currency):
    if format:
      # get this format object from the cache
      if format_cache.has_key(format):
        fmt = format_cache[format]
      else:
        fmt = NumberFormat(format)
        format_cache[format] = fmt
      # return the formated value
      return fmt.format_value(value, typ)
    else:   # just use the type's native format
      return unicode(value)
  
  # if any other format, just convert to a string
  return unicode(value)
  
  
# regular expressions used in parsing numbers
number_parser_main = re.compile('[^-0-9.]', re.DOTALL)
number_parser_dot_remover = re.compile('^(.*?\..*?)\.', re.DOTALL)
number_parser_percent = re.compile('^(.*?)%', re.DOTALL)
number_parser_sci_note = re.compile('^(.*?)E([-+])([0-9]+)', re.IGNORECASE | re.DOTALL)

def parse_value_to_type(value, typ, format=None):
  '''Utility method that does the actual parsing.  See the Column.set_format method
     for a description of the format used here.'''
  # short circuit if we're already the right type
  # short circuit if we have the None type (don't ever coerce that one)
  # short circuit if we don't have a column type (which should really never happen)
  if value == None or isinstance(value, typ) or typ == None:
    return value
  
  # if a date format
  if typ == Date:
    if format != None:
      return Date(value, format)
    return Date(value)
  elif typ == DateTime:
    if format != None:
      return DateTime(value, format)
    return DateTime(value)
  
  # if a number format
  if typ in (int, long, float, number, currency):
    num = unicode(value)
    # check for scientific notation, and separate it out if necessary
    result_scinote = number_parser_sci_note.search(num)
    if result_scinote != None:
      num = result_scinote.group(1)

    # check for a percent sign
    result_perc = number_parser_percent.search(num)
    if result_perc:
      num = result_perc.group(1)

    # this removes everything except numbers and dots
    num = number_parser_main.sub('', num)

    # check for multiple dots, and ignore anything after the second dot
    result = number_parser_dot_remover.search(num)
    if result:
      num = result.group(1)

    # if we have parsed everything out of the string, assign a 0 to the value
    if num == '':
      num = 0
  
    # we can now convert to an actual number
    conv = typ(number(num))  # have to go through number because int can't parse a string containing a period
    if result_scinote != None and result_scinote.group(2) == '-':
      conv = typ(conv / (10 ** int(result_scinote.group(3))))
    if result_scinote != None and result_scinote.group(2) == '+':
      conv = typ(conv * (10 ** int(result_scinote.group(3))))
    if result_perc != None:
      conv = typ(conv / 100.0)
    return conv
  
  # if any other format, try to coerce using the type itself (like int("5"))
  return typ(value)
    


########################################################################
###  Imports must come after the above because the above are needed
###  in some of these imports    
from Calendar import RE_DATE_FORMATS, RE_DATETIME_FORMATS, DateTime, Date
from Number import number
from Currency import currency
from Boolean import boolean
from picalo.lib import stats
from picalo.lib import progressbar
from Error import error
    


#########################################################
###  types used below in Database.post_table
###

VARIABLE_TYPES_RE = []
VARIABLE_TYPES_RE.append(  [ re.compile("^-{0,1}\d+$")            ,     int      ])
VARIABLE_TYPES_RE.append(  [ re.compile("^-{0,1}\d+$")            ,     long     ])
VARIABLE_TYPES_RE.append(  [ re.compile("^-{0,1}\d+(\.\d+){0,1}$"),     float    ])
VARIABLE_TYPES_RE.append(  [ re.compile('^TRUE|FALSE$', re.IGNORECASE), boolean  ])
VARIABLE_TYPES_RE.append(  [ re.compile('^T|F$',        re.IGNORECASE), boolean  ])
VARIABLE_TYPES_RE.append(  [ re.compile('^YES|NO$', re.IGNORECASE),     boolean  ])
for item in RE_DATE_FORMATS:
  VARIABLE_TYPES_RE.append([ item.regex, Date ])
for item in RE_DATETIME_FORMATS:
  VARIABLE_TYPES_RE.append([ item.regex, DateTime ])


# conversions from python types to database types
# maps to the database create string and whether to use quotes around values
TYPE_TO_DB = {
  DateTime: 'TIMESTAMP',
  Date:     'DATE',
  int:      'INTEGER',
  long:     'BIGINT',
  float:    'FLOAT',
  boolean:  'BOOLEAN',
  # str and unicode types (VARCHAR) should not be listed here - see Database.post_table
}
  



# regular expression to check for a valid python variable      
VARIABLE_RE = re.compile('^[A-Za-z_][A-Za-z0-9_]*$')
FIRST_LETTER_RE = re.compile('[A-Za-z_]')
LETTER_RE = re.compile('[A-Za-z0-9_]')
RESERVED_COLUMN_NAMES = {  # these would conflict in expressions
  'record': None,
  'recordindex': None,
  'startrecord': None,
  'record1': None,
  'record1index': None,
  'record2index': None,
  'record2': None, 
  'value': None,
  'group': None,
}
# more RESERVED_COLUMN_NAMES are lower in this module
  



###########################################################
###   A few simple functions to help users do common tasks.
###   These override some Python functions like sum, but
###   they take the exact same arguments and call the
###   built-in functions.  Putting them here allows
###   us to create custom documentation.
_builtinsum = sum
def sum(sequence, start=0):
  '''Returns the sum of the given sequence of numbers
     plus the value of start.  When the sequence is empty,
     returns start.
     
     @param sequence:   A sequence of numbers
     @type  sequence:   list
     @param start:      The starting value, usually 0
     @type  start:      int
     @return:           The sum of the sequence, plus the start value
     @rtype:            int
  '''
  return _builtinsum(sequence, start)
  
  
def mean(sequence, default=0):
  '''Returns the average of the given sequence,
     or the default if the sequence is empty.
     More advanced statistical routines can be found in the picalo.lib.stats
     module.
  
     @param sequence:    A sequence of numbers
     @type  sequence:    list
     @param default:     The default value to return when the list is empty
     @type  default:     int
     @return:            The average of the numbers
     @rtype:             float
  '''
  if len(sequence) == 0:
    return default
  elif len(sequence) == 1:
    return sequence[0]
  else:
    return stats.mean(sequence)
    

def count(sequence):
  '''Returns the number of items in the sequence.
     The built in function "len" also gives this value.
     
     @param sequence:    A sequence of items of any type.  If not a sequence, returns 1.
     @type  sequence:    list
     @return:              The number of items in the sequence
     @rtype:               float
  '''
  try:
    return len(sequence)
  except:
    return 1
  

_builtinmax = max
def max(*args, **kargs):
  '''With a single sequence argument, return its largest item.
     With two or more arguments, return the largest argument.
     
     @param args:   A sequence of items.
     @return:       The largest item in the sequence
     @rtype:        object
  '''
  return _builtinmax(*args, **kargs)
  
  
_builtinmin = min
def min(*args, **kargs):
  '''With a single sequence argument, return its smallest item.
     With two or more arguments, return the smallest argument.
     
     @param args:       A sequence of items.
     @return:           The smallest item in the sequence
     @rtype:            object
  '''
  return _builtinmin(*args, **kargs)

  
def stdev(sequence, default=0):
  '''Returns the standard deviation of the given sequence,
     or the default if the sequence contains zero or one items.
     More advanced statistical routines can be found in the picalo.lib.stats
     module.
     
     @param sequence:   A sequence of items.
     @type  sequence:   list
     @param default:    The default if a standard deviation cannot be calculated.
     @type  default:    float
     @return:           The standard deviation of the sequence, or the default if len(sequence) < 2.
     @rtype:            float
  '''
  if len(sequence) < 2:
    return default
  return stats.stdev(sequence)
  
  
def variance(sequence, default=0):
  '''Returns the variance of the given sequence,
     or the default if the sequence contains zero or one items.
     More advanced statistical routines can be found in the picalo.lib.stats
     module.
     
     @param sequence:   A sequence of items.
     @type  sequence:   list
     @param default:    The default if a variance cannot be calculated.
     @type  default:    float
     @return:           The variance of the sequence, or the default if len(sequence) < 2.
     @rtype:            float
  '''
  if len(sequence) < 2:
    return default
  return stats.var(sequence)
  
  
#################################################################################
###   Whether Picalo is being run in GUI mode.
###   This has to be in a module that doesn't import (or indirectly import wx)
###   so Picalo can be used from command line without loading wx all the time

# a reference to the main frame of the GUI program.  PicaloApp.py sets this.
# if None, we're running in console mode.
mainframe = None
guiUpdateProgressDialog = None
useProgress = False  # this is set to True at the end of picalo/__init__.py
lastcaller = None
lastprogress = 0.0
progress_lock = threading.RLock()

def _updateProgress(msg='', progress=1, title='Progress', force=False):
  '''Initializes the progress bar if it's being used.  Progress should be from 0 to 1.
     This function SHOULD NOT be called directly.  Instead, call the show_progress()
     method global to Picalo (imported when you "from picalo import *").
     
     See the documentation for show_progress for information on the parameters.
  '''
  global lastcaller, lastprogress
  progress_lock.acquire()
  try:
    # if we're not using the progress bars, short circuit now
    if not useProgress:
      return
  
    # short circuit if the last frame who called this isn't the current one
    # I do this because so many functions try to show a progress dialog
    # If one opens the progress dialogs, then another tries to, it would blast the
    # original one away.  So the first to open the dialog is the winner, others get
    # short circuited right here
    caller = id(inspect.currentframe().f_back.f_back.f_code)
    if caller != None and lastcaller != None and caller != lastcaller and force == False:
      # still call the progress bar to give the dialog a chance to catch the cancel button
      if mainframe == None:  # text progress bar
        _updateProgressDialog(progress=lastprogress)
      else:  # GUI progress dialog
        guiUpdateProgressDialog(progress=lastprogress, parent=mainframe)
      return
    lastcaller = caller  
    
    # remove the lastcaller if we're done
    if not msg or progress >= 1.0 or progress < 0.0:
      lastcaller = None
  
    # switch to either text or GUI progress bar
    lastprogress = progress
    if mainframe == None:  # text progress bar
      _updateProgressDialog(msg=msg, progress=progress)
    else:  # GUI progress dialog
      guiUpdateProgressDialog(msg=msg, progress=progress, title=title, parent=mainframe)

  finally:
    progress_lock.release()
    

def use_progress_indicators(show):
  '''Sets whether Picalo shows progress dialogs in text or GUI mode.
     Send False into this method to make Picalo quiet.  Send True
     to see progress bars for operations.
  '''
  global useProgress
  useProgress = show
  

def show_progress(msg='', progress=1.0, title='Progress', force=False):
  '''Updates the progress bar with a message and
     a percentage progress between 0 and 1. To remove the progress
     bar, call clear_progress().
     
     This function is important because it gives feedback to the user.
     In addition, and perhaps more importantly, it gives the user a 
     cancel button (in GUI mode) that allows the user to cancel
     your script.  Be sure to call show_progress throughout your
     script.
     
     Sometimes multiple functions try to show or clear a progress bar.
     For example, a top-level script might show a master progress bar
     and then call load().  The load() function tries to show another
     progress bar, which Picalo normally circumvents or the load() function
     would take over the top-level script's progress bar.  In other words,
     the first script to show a progress bar is the only one that can update
     and/or clear the dialog.  By setting force to True, you can override this
     default behavior.  This should not normally be used as it takes control 
     when the top-level script should keep control.

     @param msg:        The message to show the user.
     @type  msg:        str
     @param progress:   A value between 0 and 1 indicating the percentage finished.
     @type  progress:   float
     @param title:      The title of the progress bar.  Defaults to 'Progress'.
     @type  title:      str
     @param force:      Whether to force control of the dialog to the calling code.  
     @type  force:      boolean
  '''
  _updateProgress(msg=msg, progress=progress, title=title, force=force)  # just a convenience function


def clear_progress(force=False):
  '''Clears the progress bar from the screen.  
  
     Sometimes multiple functions try to show or clear a progress bar.
     For example, a top-level script might show a master progress bar
     and then call load().  The load() function tries to show another
     progress bar, which Picalo normally circumvents or the load() function
     would take over the top-level script's progress bar.  In other words,
     the first script to show a progress bar is the only one that can update
     and/or clear the dialog.  By setting force to True, you can override this
     default behavior.  This should not normally be used as it takes control 
     when the top-level script should keep control.

     @param force:      Whether to force control of the dialog to the calling code.  
     @type  force:      boolean
  '''
  _updateProgress(force=force)  # just a convenience function



###################################
###   Text-based progress bar


class MessageProgressBarWidget(progressbar.ProgressBarWidget):
  '''Extension to display a message'''
  def __init__(self):
    self.msg = ''
  def update(self, pbar):
    return self.msg
message_widget = MessageProgressBarWidget()
    
widgets = (
  message_widget,
  '  ',
  progressbar.Percentage(), 
  ' ', 
  progressbar.Bar(marker="#", left="|", right="|"), 
  ' ', 
  progressbar.ETA() 
)

progressDialog = None

def _updateProgressDialog(msg='', progress=1):
  '''Initializes the progress bar.  This should not be called directly.
     Call show_progress() instead, which gets imported when you run
     "from picalo import *".
     '''
  global progressDialog
  # if progress is done, hide the dialog
  if progress >= 1.0 or progress < 0.0:
    if progressDialog:
      progressDialog.finish()
    progressDialog = None
    return

  # create the progress dialog if necessary
  if not progressDialog:
    progressDialog = progressbar.ProgressBar(maxval=100, widgets=widgets, fd=sys.stdout)
    progressDialog.start()
    
  # update the message if necessary
  if msg:
    message_widget.msg = msg

  # update the progress
  progressDialog.update(int(progress*100.0))
  sys.stdout.flush()




  
##################################
###   Assertion code for errors

def check_valid_table(table, *columns):
  '''Checks to ensure the table is a valid table object, and that the columns
     are valid columns in the table.  Throws an AssertionError if anything is
     wrong.'''
  assert isinstance(table, Table), 'Please specify a valid table for this function.'
  for column in columns:
    if isinstance(column, (list, tuple)):
      check_valid_table(table, *column)
    else:
      table.deref_column(column) # checks that the column index/name is valie


def is_valid_variable(varname):
  '''Returns whether the given varname is a valid python variablename'''
  return VARIABLE_RE.match(varname) != None


def make_valid_variable(varname, repl='_'):
  '''Makes the given variable a valid variable name'''
  # ensure a string
  if not isinstance(varname, types.StringTypes):
    varname = unicode(varname)
  # if empty
  if len(varname) == 0:
    varname = repl
  # check the first variable
  if not FIRST_LETTER_RE.match(varname[0]):  
    if LETTER_RE.match(varname[0]): # if the letter works as a second character, just add a _ on to the first, this often prevents a larger change
      varname = repl + varname
    else:  
      varname = repl + varname[1:]
  # check the rest of the characters and replace each letter that doesn't match with a _
  for i in range(1, len(varname)):
    if not LETTER_RE.match(varname[i]):
      varname = varname[:i] + repl + varname[i+1:]
  return varname
  

def ensure_valid_variables(lst, repl='_'):
  '''Ensures the strings in the list are valid Picalo/Python variables.
     This is used to create column names during loading picalo tables.
     
     This method modifies the lst directly.  It also returns the lst for
     convenience reasons.
  '''
  for i in range(len(lst)):
    lst[i] = make_valid_variable(lst[i], repl)
  return lst
  
  
  
#############################################################
###  Helps create new column names that are unique for 
###  a table.  This is used in various picalo functions
###  that need to calculate unique names.

def make_unique_colnames(columns):
  '''Takes a list of names and adds the appropriate values to
     each value to ensure each is unique'''
  unique = []
  for i in range(len(columns)):
    unique.append(ensure_unique_list_value(unique, columns[i]))
  return unique
  

def ensure_unique_colname(table, name):
  '''Ensures the name is unique for the columns in the table.  It
     adds _1, _2, _3, and so forth if needed to the name.
  '''
  colnames = [ col.name for col in table.get_columns() ]
  return ensure_unique_list_value(colnames, name)
  
  
def ensure_unique_list_value(lst, name):
  '''Ensures that the name is unique for the names
     already in the list.  It adds _1, _2, _3, and so forth
     if needed to the name.  This function is split out
     because functions like Crosstable need to create the
     column name list before creating the table.
  '''
  ret = name
  i = 1
  while ret in lst:
    ret = name + '_' + str(i)
    i += 1
  return ret
  
  
  
##############################################
###   Converts any value to unicode using utf-8

def make_unicode(value):
  '''Makes a value (of any type) into unicode using utf_8'''
  if isinstance(value, unicode):
    return value
  elif isinstance(value, str):
    return unicode(value, 'utf_8')
  else:
    return unicode(repr(value), 'utf_8')



###########################################
###   Runs functions for table lists

def run_tablearray(msg, func, tablearray, *args, **kargs):
  '''Runs the given function on every table in the TableArray.  If the 
     function returns a Table, the results are collected into another
     TableList and returned.
     
     It assumes that the first parameter in the function is the table.
  '''
  # we assume the types have already been checked since this method is called
  # only by Picalo code (not by end users)
  # first put the tablelist into the arguments
  try:
    results = TableArray()
    return_results = False
    for i, table in enumerate(tablearray):
      show_progress(msg, float(i) / float(len(tablearray)))
      ret = func(table, *args, **kargs)
      if isinstance(ret, (Table, TableArray, TableList)):
        return_results = True
        results.append(ret)
    if return_results:
      return results
  finally:
    clear_progress()
  
  
  
  
  


###########################################################
###   General helper methods

def create_directory(directory):
  '''Creates the given directory, including all required
     directories.  This works equally well on Windows 
     and Unix (the os.mkdirs doesn't seem to like c: in paths).
  '''
  # figure out how much of the path needs to be created
  parts = []
  lastdir = None # to detect an infinite loop -- where os.path.split(directory) == directory
  while not os.path.exists(directory) and lastdir != directory:
    lastdir = directory
    directory, tail = os.path.split(directory)
    if tail:
      parts.append(tail)
  parts.reverse()
  
  # go through each one and make the directory
  for part in parts:
    directory = os.path.join(directory, part)
    os.mkdir(directory)
  
  
  
#####################################################
###   An abstract decorator for any class

class AbstractDecorator:
  '''An abstract decorator that directs all attribute/method access first
     here, then to the decorated object, then back here (for the first time something is set).
     
     Subclasses *must* call AbstractDecorator.__init__ before setting any self. variables or
     other attributes (so the _decorated_object can be set up).
  '''
  def __init__(self, obj):
    self._decorated_object = obj
    
  def __getattr__(self, name):
    try:
      return self.__dict__[name]
    except KeyError:
      return getattr(self._decorated_object, name)
    
  def __setattr__(self, name, value):
    if name == '_decorated_object' or name in self.__dict__.keys() or not hasattr(self._decorated_object, name):
      self.__dict__[name] = value
    else:
      setattr(self._decorated_object, name, value)
    
  def __delattr__(self, name):
    if name == '_decorated_object' or name in self.__dict__.keys() or not hasattr(self._decorated_object, name):
      del(self.__dict__[name])
    else:
      delattr(self._decorated_object, name)
      
  # is there a better way to do this?
  def __str__(self): return str(self._decorated_object)
  def __repr__(self): return repr(self._decorated_object)
  def __eq__(self, other): return self._decorated_object == other
  def __ne__(self, other): return self._decorated_object != other
  def __lt__(self, other): return self._decorated_object < other
  def __le__(self, other): return self._decorated_object <= other
  def __gt__(self, other): return self._decorated_object > other
  def __ge__(self, other): return self._decorated_object >= other
  def __cmp__(self, other): return cmp(self._decorated_object, other)
  def __hash__(self): return hash(self._decorated_object)
  def __nonzero__(self): return self._decorated_object != None


  
# now that we have some constants and basic classes defined, import more modules (that need the constants above)
from Table import Table
from TableList import TableList
from TableArray import TableArray
from Record import Record
from Column import Column


    
# add all record methods to the reserved column names list
# keep the methods and class variables in Record low because we allow record.column access
# and each method added further limits the available column names the users can use
table = Table(['id'], [[0]])  # get a table so we can do a dir() on a Record object
RESERVED_COLUMN_NAMES.update([ (name, None) for name in dir(table[0]) ])

  
  
##############################################################################################################
###   Alter the stats functions to accept
###   Columns and Records in addition to
###   Lists and Tuples.  That way Picalo objects
###   can be inputs into the stats functions

# this is a bit invasive and expects exact structures within stats, 
# so check that we are using the expected version of stats.
assert stats.__version__ == 0.6, 'The picalo.lib.stats module has been upgraded.  The Picalo developers need to modify the picalo.lib.__init__ file to match it.'

# add Column and Record to every function that accepts a Python list
for name in dir(stats):
  func = getattr(stats, name)
  if isinstance(func, stats.Dispatch):
    if types.ListType in func._dispatch:
      func._dispatch[Column] = func._dispatch[types.ListType]
      func._dispatch[Record] = func._dispatch[types.ListType]
      


##################################################################################
###   Import the other Picalo files and objects into the "picalo." namespace

# the order here is important!
# the from xxx import * is important for "from picalo import *" syntax
import Boolean as BooleanModule
from Boolean import *
import Number as NumberModule
from Number import *
import Currency as CurrencyModule
from Currency import *
import Error as ErrorModule
from Error import *
import Calendar as CalendarModule
from Calendar import *
import Filer as FilerModule
from Filer import *
import Table as TableModule
from Table import *
import TableArray as TableArrayModule
from TableArray import *
import TableList as TableListModule
from TableList import *
import Project as ProjectModule
from Project import *
global_variables =         \
  BooleanModule.__all__    +\
  NumberModule.__all__     +\
  CurrencyModule.__all__   +\
  ErrorModule.__all__      +\
  CalendarModule.__all__   +\
  FilerModule.__all__      +\
  TableModule.__all__      +\
  TableArrayModule.__all__ +\
  TableListModule.__all__  +\
  ProjectModule.__all__      

# this part is required for the "import picalo" use
import Benfords
import Crosstable
import Financial
import Grouping
import Trending
import Simple  
  
# modules that load with picalo.  these modules must be used with
# their names, as in "Simple.describe" rather than simply "describe".
global_modules = [
  'Benfords',
  'Boolean',
  'Crosstable',
  'Currency',
  'Column',
  'Calendar',
  'Database',
  'Error',
  'Expression',
  'Financial',
  'Grouping',
  'Number',
  'Filer',
  'Table',
  'Project',
  'Record',
  'Simple',
  'TableArray',
  'TableList',
  'Trending',
]

# the gui imports these into the shell automatically for the user
# yes, I arbitrarily decided which ones most users would want always
# included based on my experience with quite a few users using Picalo
python_modules = [
  'string',
  'sys',
  're',
  'random',
  'os',
  'os.path',
  'urllib',
  'xml.etree.ElementTree',
  
]


# global functions (defined in this file)
global_functions = [
  'sum',
  'count',
  'mean',
  'max',
  'min',
  'stdev',
  'variance',
  'use_progress_indicators',
  'show_progress',
  'clear_progress',
  'check_valid_table',
  'format_value_from_type',
  'parse_value_to_type',
]


# export the variables and modules in the __all__ variable
__all__ = global_variables + global_modules + global_functions



###############################################################################################
###   Final setup  

# now that we're done setting up, show progress indicators for user code 
use_progress_indicators(True)





