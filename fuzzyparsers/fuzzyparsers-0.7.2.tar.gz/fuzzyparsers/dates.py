# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPLv2 or later)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
Date and string matching functions.
"""

import datetime
import re
from strings import fuzzy_match, default_match

def str_to_month(s):
    """
    >>> str_to_month("ja")
    1
    >>> str_to_month("mar")
    3
    """
    months = ["january","february","march","april","may","june","july","august","september","october","november","december"]
    indexed = [(months[i], i) for i in range(len(months))]
    return fuzzy_match(indexed, s, match_fucn=lambda x, y: default_match(x[0], y))[1]+1

class DateParser:
    def __init__(self,today=None):
        if today is None:
            today = datetime.date.today()
        self.today=today

    def str_to_date_int(self,s):
        """
        :param s:  an input string to parse
        :return: a 3-tuple of numeric 4 digit year, month index 1-12 and day 1-31

        This function probably has a twisted american bias.  I say "twisted" because I tend to prefer yyyy-mm-dd for my own 
        personal date entry.  However, the applications I write are for US citizens.
        
        >>> DateParser().str_to_date_int("feb 2 2011")
        (2011, 2, 2)
        >>> DateParser().str_to_date_int("2010.3.11")
        (2010, 3, 11)
        >>> DateParser().str_to_date_int("12 1 2020")
        (2020, 12, 1)
        >>> DateParser().str_to_date_int("total junk")
        Traceback (most recent call last):
        ...
        NotImplementedError: The input date 'total junk' is unrecognized.
        """
        m = re.match("([a-zA-Z]*) ([0-9]+)(,|) ([0-9]+)",s)
        if m:
            return int(m.group(4)),str_to_month(m.group(1)),int(m.group(2))
        # month year
        m = re.match("([a-zA-Z]*) ([0-9]{4})",s)
        if m:
            # this is a little curious, but I think it makes sense to a human
            # If I enter "March 2011", I think I mean the 1st of march ... maybe
            return int(m.group(2)),str_to_month(m.group(1)),1
        # month day
        m = re.match("([a-zA-Z]*) ([0-9]+)",s)
        if m:
            return None,str_to_month(m.group(1)),int(m.group(2))
        # yyyy-mm-dd
        m = re.match("([0-9]{4})[-./ ]([0-9]{1,2})[-./ ]([0-9]{1,2})",s)
        if m:
            return int(m.group(1)),int(m.group(2)),int(m.group(3))
        # mm-dd-yyyy
        m = re.match("([0-9]{1,2})[-./ ]([0-9]{1,2})[-./ ]([0-9]{4})",s)
        if m:
            return int(m.group(3)),int(m.group(1)),int(m.group(2))
        # mm-dd-yy
        # this is an American bias here, but perhaps we should look at the locale ??
        m = re.match("([0-9]{1,2})[-./ ]([0-9]{1,2})[-./ ]([0-9]{2})",s)
        if m:
            return int(m.group(3))+2000,int(m.group(1)),int(m.group(2))
        m = re.match("(-|\+)([0-9]+)",s)
        if m:
            if m.group(1)=='+':
                d = self.today + datetime.timedelta(int(m.group(2)))
            elif m.group(1)=='-':
                d = self.today - datetime.timedelta(int(m.group(2)))
            return d.year,d.month,d.day
        raise NotImplementedError("The input date '%s' is unrecognized." % (s,))

    def str_to_date(self,s):
        """
        Parses input `s` into a date.  The accepted date formats are quite flexible.
        
        jan 12, 2003
        jan 5
        2004-3-5
        +34 -- 34 days in the future (relative to todays date)
        -4 -- 4 days in the past (relative to todays date)
        >>> DateParser(datetime.date(2011,4,15)).str_to_date("may 1")
        datetime.date(2011, 5, 1)
        """
        year,month,day = self.str_to_date_int(s)
        if year is None:
            year = self.today.year
        if month is None:
            month = self.today.month
        if day is None:
            day = self.today.day
        return datetime.date(year,month,day)

    def parse_date(self,d):
        """
        >>> DateParser(datetime.date(2011,1,1)).parse_date("+10")
        datetime.date(2011, 1, 11)
        """
        if d is None or isinstance(d,datetime.date):
            return d
        else:
            return self.str_to_date(d)

def parse_date(d):
    """
    :param d: d can be a datetime.date, None or anything with string semantics.
    
    This function only pre-checks the type for a date type or None before passing the 
    lone parameter on to str_to_date.
    
    Certain import formats assume a current date to fill in missing pieces of the date 
    or as a baseline for relative dates.  To provide your own baseline date, use 
    the DateParser class directly.
    
    Examples:
    >>> parse_date('jan 9 1979') # my birthday
    datetime.date(1979, 1, 9)
    >>> parse_date('2010-06-17') # my youngest son's birthday
    datetime.date(2010, 6, 17)
    >>> parse_date('f 29, 2012')  # february is the unique month starting with 'f'
    datetime.date(2012, 2, 29)
    >>> parse_date('mar 2015')  # with no date, but a full month & year, assume the first
    datetime.date(2015, 3, 1)
    >>> parse_date('+35')-datetime.date.today()
    datetime.timedelta(35)
    >>> parse_date('-35')-datetime.date.today()
    datetime.timedelta(-35)
    >>> parse_date(None)  # None is simply returned unchanged

    >>> # We'd expect to be able to parse any locale date
    >>> x = parse_date( 'jan 13 2012' )
    >>> x
    datetime.date(2012, 1, 13)
    >>> parse_date(x.strftime("%x"))==x
    True
    """
    return DateParser().parse_date(d)
