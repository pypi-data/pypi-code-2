####################################################################################
#                                                                                  #
# Copyright (c) 2007 Dr. Conan C. Albrecht <conan_albrechtATbyuDOTedu>             #
#                                                                                  #
# This software is free software; you can redistribute it and/or modify            #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation; either version 2 of the License, or                # 
# (at your option) any later version.                                              #
#                                                                                  #
# This software is distributed in the hope that it will be useful,                 #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with Foobar; if not, write to the Free Software                            #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA        #
#                                                                                  #
####################################################################################

__doc__ = '''
This module implements a memory-efficient CSV reader and writer.  Although 
Python 2.4+ has a built-in csv module, real-world tests by me show that it
is not memory efficient.  In other words, it runs out of memory on files
with 25 million or more records in it.

While this implementation may not be as fast (because it is written in
pure Python), it only holds one line at a time in memory.  It is up to
the calling application to make efficient use of these records.
'''

import os, cStringIO, codecs
from chardet.universaldetector import UniversalDetector


########################################################
###   Utility functions and variables

def make_unicode(value):
  '''Makes a value (of any type) into unicode using utf_8'''
  if isinstance(value, unicode):
    return value
  elif isinstance(value, str):
    return unicode(value, 'utf_8')
  else:
    return unicode(repr(value), 'utf_8')



########################################################
###   Delimited Writer

class DelimitedWriter:
  '''A writer of delimited text files'''
  def __init__(self, f, delimiter=',', qualifier='"', line_ending=os.linesep, none='', encoding='utf_8'):
    '''Constructor for a delimited writer object.
    
       @param f:            A file object that allows writing.  You must have already opened the file for writing.  This class does NOT close the writer.
       @type  f:            str
       @param delimiter:    A field delimiter character, defaults to a comma (,)
       @type  delimiter:    str
       @param qualifier:    A qualifier to use when delimiters exist in field records, defaults to a double quote (")
       @type  qualifier:    str
       @param line_ending:  A line ending to separate rows with, defaults to os.linesep (\n on Unix, \r\n on Windows)
       @type  line_ending:  str
       @param none:         An parameter specifying what to write for cells that have the None value, defaults to an empty string ('')
       @type  none:         str
       @param encoding:     The unicode encoding to write with.  This should be a value from the codecs module, defaults to 'utf_8'.
       @type  encoding:     str
    '''  
    self.f = codecs.EncodedFile(f, 'utf_8', encoding)
    self.delimiter = make_unicode(delimiter)
    self.qualifier = make_unicode(qualifier)
    self.doublequalifier = self.qualifier + self.qualifier
    self.line_ending = make_unicode(line_ending)
    self.none = none
    self.encoding = encoding


  def writerow(self, row, lastrow=False):
    '''Writes a row to the file.  This method is not thread-safe on the same DelimitedWriter object.
    
    @param row:     An iterable object to encode, such as a Python list or tuple.
    @type  row:     iterable object
    @param lastrow: Whether this is the last row of the file.  If True, no line ending is written.
    @type  lastrow: bool
    '''
    fields = []
    # encode for delimited text
    for val in row:
      val = make_unicode(val)
      if self.delimiter in val or self.qualifier in val or self.line_ending in val:
        fields.append(self.qualifier + val.replace(self.qualifier, self.doublequalifier) + self.qualifier)
      else:
        fields.append(val)
    
    # finally, write to the file in the desired encoding
    self.f.write(self.delimiter.join(fields).encode(self.encoding))
    if not lastrow:
      self.f.write(self.line_ending)
    self.f.flush()
    





###############################################
###   Delimited Reader

class DelimitedReader:
  '''A reader for delimited text files'''
  def __init__(self, f, delimiter=',', qualifier='"', encoding=None, errors='replace'):
    '''Constructor for a delimited text file reader.  Windows, Unix, and Mac line endings are automatically supported.
       The object can be iterated across (ex: for row in DelimitedReader(...) ) efficiently.  Each iteration produces
       a list of fields for the current row.  StopIteration is raised when no more records exist.

       @param f:            A file object that allows writing.  You must have already opened the file for writing.  This class does NOT close the writer.
       @type  f:            str
       @param delimiter:    A field delimiter character, defaults to a comma (,)
       @type  delimiter:    str
       @param qualifier:    A qualifier that denotes fields with special characters in them, defaults to a double quote (")
       @type  qualifier:    str
       @param encoding:     The unicode encoding to read with.  This should be a value from the codecs module.  If None, the encoding is guessed to utf_8, utf-16, utf-16-be, or utf-16-le
       @type  encoding:     str
       @param errors:       How to handle characters that cannot be decoded.  Options are 'replace', 'strict', and 'ignore'.  See 'codecs' in the Python documentation for more information.
       @type  errors:       str
    '''
    self.delimiter = delimiter
    self.qualifier = qualifier
    self.doublequalifier = qualifier + qualifier
    if encoding != None:
      self.encoding = encoding
    else: # we'll have to guess it with the chardet module
      startpos = f.tell()  # we'll have to read the file a bit, then reset at the end
      detector = UniversalDetector()
      while True:
        block = f.read(1024)  # read in 1K chunks
        detector.feed(block)
        if detector.done or not block:
          break
      detector.close()
      f.seek(startpos) # reset to the beginning position to read with the given encoding
      self.encoding = detector.result['encoding']
    # open the file with the given encoding
    self.f = codecs.EncodedFile(f, 'utf_8', self.encoding, errors)

    
  def __iter__(self):
    '''Returns an iterator to this DelimitedReader.  This allows code like the following:
    
       for record in delimitedtext.DelimitedReader(file):
         print record
    '''
    return self
    
    
  def _getnextline(self):
    '''Internal method that retrieves the next line of the file, separating the text from the line separator'''
    line = unicode(self.f.next(), 'utf_8')
    if line[-2:] in (u'\r\n', u'\n\r'):
      return line[:-2], line[-2:]
    elif line[-1:] in (u'\n', u'\r'):
      return line[:-1], line[-1:]
    return line, ''
    
  
  def _isendqualifier(self, field):
    '''Internal method that returns true if the given field ends with a qualifier.
       A field ends with a qualifier when it has an *odd* number
       of qualifiers at the end.  If it has an even number of qualifiers,
       the qualifiers are part of the actual field rather than a qualifier.
    '''
    qualifiers = self.qualifier
    count = 0
    while field.endswith(qualifiers):
      count += 1
      qualifiers += self.qualifier
    return count % 2 == 1
    

  def next(self):
    '''Reads a CSV record from the file and returns a list of fields encoded as unicode objects.
       A CSV record normally corresponds to a single line of the file, but it can span more than one
       line if the record contains hard returns in the values.  The method can handle these multi-line
       records.
       
       The method raises a StopIteration when done.  This supports the python Iterator interface.
       
       @returns  The fields from the next row.
       @rtype    list
    '''
    # The algorithm works by splitting the line by all delimiters first.  This will split some
    # (qualified) fields that shouldn't have been split.  It then goes through the splits 
    # and puts back together everything that shouldn't have been split.
    record = []
    combofield = None
    while True:
      line, linesep = self._getnextline()
      fields = line.split(self.delimiter)
      for field in fields:
        if combofield == None:    # we're not in quotes at the moment
          if field.startswith(self.qualifier) and self._isendqualifier(field[len(self.qualifier):]): # starts and ends with qualifier
            # remove the qualifiers and add now
            field = field[len(self.qualifier): -1*len(self.qualifier)]  # take off beginning and ending quotes
            record.append(field.replace(self.doublequalifier, self.qualifier))
        
          elif field.startswith(self.qualifier):  # starts with a qualifier but doesn't end yet
            # start quotes mode by assigning combofield (take off initial qualifier)
            combofield = field[len(self.qualifier):]
          
          else: # no qualifiers
            # this is just a regular field, so add it now
            record.append(field.replace(self.doublequalifier, self.qualifier))
        
        else:  # in quotes mode right now
          if self._isendqualifier(field[len(self.qualifier):]):  # we found the end qualifier, so add entire combofield now
            combofield += self.delimiter + field[:-1*len(self.qualifier)]  # take off ending quote
            record.append(combofield.replace(self.doublequalifier, self.qualifier))
            combofield = None
        
          else:  # not at end qualifier yet, so add to combofield and continue searching for end
            combofield += self.delimiter + field
            
      # if we're not in a combofield, we're done
      if combofield == None:
        return record
      
      # we're in a combofield, so add the line separator back into the file
      combofield += linesep


  def readrow(self):
    '''Reads a CSV record from the file and returns a list of fields encoded as unicode objects.
       A CSV record normally corresponds to a single line of the file, but it can span more than one
       line if the record contains hard returns in the values.  The method can handle these multi-line
       records.

       The method returns None when no more records exist.

       @returns  The fields from the next row.
       @rtype    list
    '''
    try:
      return self.next()
    except StopIteration:
      return None
