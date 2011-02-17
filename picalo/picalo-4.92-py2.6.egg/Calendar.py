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

import sys, time, datetime, types, re
from Number import number
from picalo import parse_value_to_type
  
# global functions (defined in this file)
__all__ = [
  'Date', 
  'DateTime',
  'DateFormat',
  'DateTimeFormat',
  'TimeDelta',
  'DateDelta',
]


class DateFormatInfo:
  '''A simple class to represent information about a date format'''
  def __init__(self, regex, format):
    self.regex = regex
    self.format = format


# these are all the date formats we search through to autodiscover the format a date is in.  
# this is mostly used in Column.parse_value()
DATE_FORMATS = [
  [ '\d{4}-\d{1,2}-\d{1,2}',   '%Y-%m-%d' ],   # 2010-01-31
  [ '\d{2}-\d{1,2}-\d{1,2}',   '%y-%m-%d' ],   # 10-01-31
  [ '\d{1,2}-\d{1,2}-\d{4}',   '%m-%d-%Y' ],   # 01-31-2010

  [ '\d{4}\.\d{1,2}\.\d{1,2}', '%Y.%m.%d' ],   # 2010.01.31
  [ '\d{2}\.\d{1,2}\.\d{1,2}', '%y.%m.%d' ],   # 10.01.31
  [ '\d{1,2}\.\d{1,2}\.\d{4}', '%m.%d.%Y' ],   # 01.31.2010

  [ '\d{4} \d{1,2} \d{1,2}',   '%Y %m %d' ],   # 2010 01 31
  [ '\d{2} \d{1,2} \d{1,2}',   '%y %m %d' ],   # 10 01 31
  [ '\d{1,2} \d{1,2} \d{4}',   '%m %d %Y' ],   # 01 31 2010

  [ '\d{4}\/\d{1,2}\/\d{1,2}', '%Y/%m/%d' ],   # 2010/01/31
  [ '\d{2}\/\d{1,2}\/\d{1,2}', '%y/%m/%d' ],   # 10/01/31
  [ '\d{1,2}\/\d{1,2}\/\d{4}', '%m/%d/%Y' ],   # 01/31/2010

  [ '\d{4}-\w{3}-\d{1,2}',     '%Y-%b-%d' ],   # 2010-Jan-31
  [ '\d{2}-\w{3}-\d{1,2}',     '%y-%b-%d' ],   # 10-Jan-31
  [ '\d{4}-\w{3,}-\d{1,2}',    '%Y-%B-%d' ],   # 2010-January-31
  [ '\d{2}-\w{3,}-\d{1,2}',    '%y-%B-%d' ],   # 10-January-31

  [ '\d{1,2} \w{3} \d{4}',     '%d %b %Y' ],   # 25 Jan 2005
  [ '\d{1,2} \w{3} \d{2}',     '%d %b %y' ],   # 25 Jan 05
  [ '\d{1,2} \w{3,} \d{4}',    '%d %B %Y' ],   # 25 January 2005
  [ '\d{1,2} \w{3,} \d{2}',    '%d %B %y' ],   # 25 January 05
  [ '\w{3} \d{1,2}, \d{4}',    '%b %d, %Y' ],  # Jan 25, 2005
  [ '\w{3} \d{1,2}, \d{2}',    '%b %d, %Y' ],  # Jan 25, 05
  [ '\w{3,} \d{1,2}, \d{4}',   '%B %d, %Y' ],  # January 25, 2005
  [ '\w{3,} \d{1,2}, \d{2}',   '%B %d, %Y' ],  # January 25, 05
]
RE_DATE_FORMATS = []  # used in the TableProperties dialog
RE_DATETIME_FORMATS = []
# first add the native datetime format
NATIVE_FORMAT_PARSER = re.compile('^(\d{4})-(\d{2})-(\d{2}) +(\d{2}):(\d{2}):(\d{2}).(\d{2,7})$')
RE_DATETIME_FORMATS.append(DateFormatInfo(re.compile('^\d{4}-\d{2}-\d{2} +\d{2}:\d{2}:\d{2}.\d+$'), ''))  
# now add some other formats
for repattern, timepattern in DATE_FORMATS:  # make reg expressions for date plus different forms of time and zone (makes a lot of patterns!)
  RE_DATE_FORMATS.append(DateFormatInfo(re.compile('^' + repattern + "$"), timepattern))   
  RE_DATETIME_FORMATS.append(DateFormatInfo(re.compile('^' + repattern + "$"), timepattern))
  RE_DATETIME_FORMATS.append(DateFormatInfo(re.compile('^' + repattern + ' +\d{1,2}:\d{1,2}:\d{1,2}$'), timepattern + ' %H:%M:%S'))
  RE_DATETIME_FORMATS.append(DateFormatInfo(re.compile('^' + repattern + ' +\d{1,2}:\d{1,2}:\d{1,2}(AM|PM|am|pm)$'), timepattern + ' %I:%M:%S%p'))
  RE_DATETIME_FORMATS.append(DateFormatInfo(re.compile('^' + repattern + ' +\d{1,2}:\d{1,2}:\d{1,2} +(AM|PM|am|pm)$'), timepattern + ' %I:%M:%S %p'))


#####################################################
###   Date arithmetic helper method

def __coerce_value__(other):
  '''Function that allows Date arithmetic with standard Python types'''
  if isinstance(other, (int, long, float, number)):
    return TimeDelta(other)
  elif isinstance(other, (unicode, str)):
    return TimeDelta(parse_value_to_type(other, float))
  return other
    
    


####################################################
###  Standard DateTime type used in Picalo


def _parse(klass, subklass, stdate, format):
  '''Internal function to initialize a date into a date or datetime object'''
  if format:
     parts = time.strptime(stdate, format)
     if klass == datetime.datetime:
       return klass.__new__(subklass, parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])
     elif klass == datetime.date:
       return klass.__new__(subklass, parts[0], parts[1], parts[2])
     raise SystemError, 'Invalid klass used in DateTime._parse'
  # special code to parse the native datetime format, since strptime can't do it
  m = NATIVE_FORMAT_PARSER.search(stdate)  # milliseconds
  if m and klass == datetime.datetime:
    msec = m.group(7)
    microsecs = int(msec + ('0' * (6-len(msec))))
    return klass.__new__(subklass, int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)), microsecs)
  elif m and klass == datetime.date:
    return klass.__new__(subklass, int(m.group(1)), int(m.group(2)), int(m.group(3)))
  raise ValueError, 'Value is not one of the known date formats'


last_re_date_used = 0  # see the function below for this
def _create(klass, subklass, *args, **kargs):
  '''Internal function to create a date or time'''
  # these if statements in the function are in order of the most-used to least used, for a speed increase
  global last_re_date_used
  
  # check if we have exactly one argument
  if len(args) == 1:
    # see if we already have a datetime
    if isinstance(args[0], (datetime.datetime, datetime.date)):
      if klass == datetime.datetime and type(args[0]) in (DateTime, datetime.datetime):  # if already the right type, just return it (btw, isinstance doesn't work)
        return args[0]
      return klass.__new__(subklass, args[0].year, args[0].month, args[0].day)  
      
    # check if we have a single string for the argument
    if isinstance(args[0], types.StringTypes):
      # first check the last one we used, since we often parse thousands of rows with the same format in each row
      match = RE_DATETIME_FORMATS[last_re_date_used].regex.match(args[0])
      if match:
        return _parse(klass, subklass, args[0], RE_DATETIME_FORMATS[last_re_date_used].format)
      # the last one didn't match, so go through the entire list of patterns
      for i in range(len(RE_DATETIME_FORMATS)):
        match = RE_DATETIME_FORMATS[i].regex.match(args[0])
        if match:
          last_re_date_used = i
          return _parse(klass, subklass, args[0], RE_DATETIME_FORMATS[last_re_date_used].format)
      raise ValueError, 'Value is not in one of the known date formats: ' + args[0] + '.  Use Date(value, format) or DateTime(value, format) instead.'
    
  # check if we have a specific string format
  if len(args) == 2 and isinstance(args[0], types.StringTypes) and isinstance(args[1], types.StringTypes):
    return _parse(klass, subklass, args[0], args[1])
    
  # check for empty parameters
  if len(args) == 0 and len(kargs) == 0:
    parts = time.localtime()
    if klass == datetime.datetime:
      return klass.__new__(subklass, parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])
    elif klass == datetime.date:
      return klass.__new__(subklass, parts[0], parts[1], parts[2])
    raise SystemError, 'Invalid klass used in DateTime._create'
    
  # check for none type
  if len(args) >= 1 and args[0] == None:
    return None
    
  # revert to the datetime or date constructor
  return klass.__new__(subklass, *args, **kargs)
    

class Date(datetime.date):
  '''The Picalo date type to represent dates.'''
  
  def __new__(*args, **kargs):
    '''Date objects can be created in many different ways:
       
       Option 1: No arguments for now.
         - Date()
         
       Option 2: Provide the individual parts as numbers.  The year is
       the only one that is absolutely necessary.
         - Date(year, month, day, hour, minute, second)
         - Date(year, month, day)
         - Date(year)
  
       Option 3: Converts a string using a custom format.  Format options are
       described in the strftime manpage.  Search the web for
       "strftime unix manpage" for the options.
         - Date('2010-01-31', '%Y-%m-%d') 
         
       Option 4: Converts a string using ISO 8601 date format or a few other common formats
         - Date('2010-01-31')      
         - Date('10-01-31')      
         - Date('01-31-2010')      
         - Date('2010 01 31')      
         - Date('10 01 31')      
         - Date('01 31 2010')      
         - Date('2010.01.31')      
         - Date('10.01.31')      
         - Date('01.31.2010')      
         - Date('2010/01/31')      
         - Date('10/01/31')      
         - Date('01/31/2010')      
         - Date('2010-Jan-01')          
         - Date('25 JAN 2005')          
         - Date('25 Jan 2010')    
         - Date('25 January 2005')      
         - Date('2010-January-01')      
         - Date('January 1, 2010')      
         - Date('Jan 1, 2010')          
         
       Time can be specified with any of the above formats with hh:mm:ss, as in
         - Date('2010-01-31 14:15:25')
         - Date('2010-01-31 02:15:25am')
         - Date('2010-01-31 02:15:25 am')
       but with the Date() function, the time information is ignored.  Use
       DateTime if you want to keep time information as well.
    '''
    return _create(datetime.date, *args, **kargs)


  def __reduce_ex__(self, pickle_protocol):
    '''Helps in saving and loading the object'''
    return (Date, (self.strftime('%Y-%m-%d %H:%M:%S'), ))
    

  def __add__(self, other):   return datetime.date.__add__(self, __coerce_value__(other))
  def __radd__(self, other):  return datetime.date.__radd__(self, __coerce_value__(other))
  def __sub__(self, other):   return datetime.date.__sub__(self, __coerce_value__(other))
  def __rsub__(self, other):  return datetime.date.__rsub__(self, __coerce_value__(other))

    

class DateTime(datetime.datetime):
  '''The Picalo date/time type to represent dates and times.'''
  def __new__(*args, **kargs):
    '''The Picalo date/time type to represent dates and times.
       DateTime objects can be created in many different ways:
       
       Option 1: No arguments.
         - DateTime()
         
       Option 2: Provide the individual parts as numbers.  The year is
       the only one that is absolutely necessary.
         - DateTime(year, month, day, hour, minute, second)
         - DateTime(year, month, day)
         - DateTime(year)
  
       Option 3: Converts a string using a custom format.  Format options are
       described in the strftime manpage.  Search the web for
       "strftime unix manpage" for the options.
         - DateTime('2010-01-31', '%Y-%m-%d') 
         
       Option 4: Converts a string using ISO 8601 date format or a few other common formats
         - DateTime('2010-01-31')      
         - DateTime('10-01-31')      
         - DateTime('01-31-2010')      
         - DateTime('2010 01 31')      
         - DateTime('10 01 31')      
         - DateTime('01 31 2010')      
         - DateTime('2010.01.31')      
         - DateTime('10.01.31')      
         - DateTime('01.31.2010')      
         - DateTime('2010/01/31')      
         - DateTime('10/01/31')      
         - DateTime('01/31/2010')      
         - DateTime('2010-Jan-01')          
         - DateTime('25 JAN 2005')          
         - DateTime('25 Jan 2010')    
         - DateTime('25 January 2005')      
         - DateTime('2010-January-01')      
         - DateTime('January 1, 2010')      
         - DateTime('Jan 1, 2010')          
         
       Time can be specified with any of the above formats with hh:mm:ss, as in
         - DateTime('2010-01-31 14:15:25')
         - DateTime('2010-01-31 02:15:25am')
         - DateTime('2010-01-31 02:15:25 am')
         - Time zone information is not supported with Option 4 at this point.
    '''
    return _create(datetime.datetime, *args, **kargs)


  def __reduce_ex__(self, pickle_protocol):
    '''Helps in saving and loading the object'''
    return (DateTime, (self.strftime('%Y-%m-%d %H:%M:%S'), ))

  def __add__(self, other):   return datetime.datetime.__add__(self, __coerce_value__(other))
  def __radd__(self, other):  return datetime.datetime.__radd__(self, __coerce_value__(other))
  def __sub__(self, other):   return datetime.datetime.__sub__(self, __coerce_value__(other))
  def __rsub__(self, other):  return datetime.datetime.__rsub__(self, __coerce_value__(other))


def DateTimeFormat(datetime_value, format=None):
  '''Formats a DateTime or Date object for printing using the
     given format.  Search the web for "strftime unix manpage" for 
     the formatting tokens.
  '''
  assert isinstance(datetime_value, (datetime.datetime, datetime.date, types.NoneType)), 'The datetime_value must be a DateTime object: ' + str(datetime_value)
  assert isinstance(format, (types.StringType, types.UnicodeType, types.NoneType)), 'The format must be a string or None: ' + str(format)
  if datetime_value == None:
    return datetime_value
  if format:
    return datetime_value.strftime(format)
  if isinstance(datetime_value, datetime.datetime):  # override default formatting for datetime
    return datetime_value.strftime('%Y-%m-%d %H:%M:%S')
  return str(datetime_value)
  
# alias to the DateTimeFormat
DateFormat = DateTimeFormat


# function to create a TimeDelta
def TimeDelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
  '''A duration in time, such as the difference between two DateTimes.  This is often
     used in Grouping.stratify_by_date and Grouping.summarize_by_date.  Negative numbers
     specify durations that go backwards in time.
     
     @param   days:         The number of days in this duration
     @type    days:         int, long, or float
     @param   seconds:      The number of seconds in this duration
     @type    seconds:      int, long, or float
     @param   microseconds: The number of microseconds in this duration
     @type    microseconds: int, long, or float
     @param   milliseconds: The number of milliseconds in this duration
     @type    milliseconds: int, long, or float
     @param   minutes:      The number of minutes in this duration
     @type    minutes:      int, long, or float
     @param   hours:        The number of hours in this duration
     @type    hours:        int, long, or float
     @param   weeks:        The number of weeks in this duration
     @type    weeks:        int, long, or float
     @return: A datetime.timedelta object
     @rtype:  datetime.timedelta
  '''
  return datetime.timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)
  
# alias to a TimeDelta
DateDelta = TimeDelta


