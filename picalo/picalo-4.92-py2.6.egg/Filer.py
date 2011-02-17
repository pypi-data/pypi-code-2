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

from Table import Table
from TableList import TableList
from TableArray import TableArray
import xml.dom.minidom, re, os, os.path, sys, gzip, types, time, codecs
try:
  import cPickle as pickle
except ImportError:
  import pickle
from picalo import show_progress, clear_progress, ensure_valid_variables, ensure_unique_colname, make_unique_colnames
import picalo.lib.pyExcelerator
import picalo.lib.pyExcelerator.CompoundDoc
import picalo.lib.delimitedtext


# global functions (defined in this file)
__all__ = [
  'load',
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
  'save_excel'
]



#################################################
###   Standard Picalo format saving and loading
###   Version functions are tied to each other.  When changes are made to the Dataset
###   class above, new save and load functions should be created so old picalo files
###   can always be read.  Also change save() just above to use the new
###   version.
###
###   I can't just pickle the entire Table object because it has circular references
###   all over the place that cause errors

# pickle protocol to use
PICKLE_PROTOCOL = 2

def save(table, filename, respect_filter=False):
  '''Saves this table in native Picalo format.  This is the preferred
     format to save tables in because all column types, formulas, and so
     forth are saved.

     @deprecated: Add tables to Project objects and load/save the project.  Loading/saving tables directly (the .pco format) is no longer supported.

     @param filename: The filename to save to.  This can also be an open stream.
     @type  filename: str
     @param respect_filter Whether to save the entire file or only those rows available through any current filter.
     @type  respect_filter bool
  '''
  try:
    assert isinstance(table, (Table, TableList, TableArray)), 'Only Tables, TableLists, and TableArrays can be saved.'
  
    # get a file pointer
    fileopened = 0
    if type(filename) in types.StringTypes:
      table.filename = filename
      filename = open(filename, 'wb')
      fileopened = 1
      
    # gzip it on the fly (if it is not already a GzipFile)
    openedzip = False
    gout = filename
    if not isinstance(gout, gzip.GzipFile):
      gout = gzip.GzipFile(fileobj=gout, mode='wb')
      openedzip = True
    
    # save the pre-data
    predata = {}
    predata['version'] = 1
    predata['timestamp'] = time.time()
    predata['type'] = table.__class__.__name__
    predata['len'] = len(table)  # this is particularly useful when we have a TableList rather than a table
    pickle.dump(predata, gout, PICKLE_PROTOCOL)
    
    # now save the data
    if isinstance(table, Table):
      _saveVersion1(table, gout, respect_filter)
      
    elif isinstance(table, (TableList, TableArray)):
      for i, subtable in enumerate(table):
        show_progress('Save file...', float(i) / float(len(table)))
        save(subtable, gout, respect_filter)

    # close up shop   
    gout.flush()
    if openedzip:
      gout.close()
    if fileopened:
      filename.close()
    table.set_changed(False)
  finally:
    clear_progress()
  
  

def _saveVersion1(table, gout, respect_filter=False):
  '''Internal method to save version 1
     @deprecated: Add tables to Project objects and load/save the project.  Loading/saving tables directly (the .pco format) is no longer supported.
  '''
  try:
    # we first create a dictionary for meta information about the table (makes it easy to add more things later)    
    meta = {}

    # save the columns
    cols = [ col._get_columnloader() for col in table.columns ]
    meta['columns'] = cols
    
    # save the meta information to the stream
    pickle.dump(meta, gout, PICKLE_PROTOCOL)
        
    # save individual rows. this is not in a dictionary because the size would be prohibitive
    pickle.dump(table.record_count(respect_filter=respect_filter), gout, PICKLE_PROTOCOL)
    for r, row in enumerate(table.iterator(respect_filter)):
      show_progress('Save file...', float(r) / float(table.record_count(respect_filter=respect_filter)))
      row = table.record(r, respect_filter=respect_filter)
      for i in range(len(table.columns)):
        pickle.dump(row[i], gout, PICKLE_PROTOCOL)
  finally:
    clear_progress()

     
      
def load(filename):
  '''Loads a native picalo file.  Determines the version of the picalo file, then
     calls the appropriate load routine for that version.
     
     @deprecated: Add tables to Project objects and load/save the project.  Loading/saving tables directly (the .pco format) is no longer supported.
     
     @param filename:  The name of the file to load.  This can also be an open stream.
     @type  filename:  str
     @return:          A Picalo table containing the data from the file.
     @rtype:           Table or TableList or TableArray
  '''
  try:
    fileopened = 0
    if type(filename) in types.StringTypes:
      filepath = filename
      filename = open(filename, 'rb')
      fileopened = 1
      
    # ungzip it on the fly (if it is not already a GzipFile)
    startedzip = False
    gin = filename
    if not isinstance(gin, gzip.GzipFile):
      gin = gzip.GzipFile(fileobj=gin, mode='rb')
      startedzip = True
      
    # get the pre-data
    predata = pickle.load(gin)
  
    # switch based on what type of data we have
    if predata['type'] == 'Table':
      # load the table
      if predata['version'] == 1:
        table = _loadVersion1(gin)
      else:
        raise IOError('Picalo save format version could not be determined.')
      
      # save the filename
      if fileopened:
        table.filename = filepath
    
    elif predata['type'] == 'TableList':
      table = TableList()
      for i in range(predata['len']):
        show_progress('Loading...', float(i) / float(predata['len']))
        table.append(load(gin))
    
    elif predata['type'] == 'TableArray':
      table = TableArray()
      for i in range(predata['len']):
        show_progress('Loading...', float(i) / float(predata['len']))
        table.append(load(gin))
  
    # close up shop and return
    if startedzip:
      gin.close() 
    if fileopened:
      filename.close()
    table.set_changed(False)
    return table
  finally:
    clear_progress()



def _loadVersion1(gin):
  '''Internal method to load version 1 (this would take less memory with sax, but that can be done another day)
     @deprecated: Add tables to Project objects and load/save the project.  Loading/saving tables directly (the .pco format) is no longer supported.
  '''
  try:
    # grab the meta information
    meta = pickle.load(gin)
    
    # create the intial table
    table = Table(meta['columns'])
    
    # load the rows into the dataset
    numcols = len(table.get_columns())
    numrows = pickle.load(gin)
    for r in range(numrows):
      show_progress('Loading file...', float(r) / float(numrows))
      row = []
      for c in range(numcols):
        row.append(pickle.load(gin))
      table.append(row)

    # create and return the table
    return table

  finally:
    clear_progress()
      
      
      
      
#####################################################
###   Delimted File loading and saving
###   CSV, TSV, etc.      
      
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

