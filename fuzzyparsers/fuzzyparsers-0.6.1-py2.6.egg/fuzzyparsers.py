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

def default_match(t,item):
    return t.lower()[:len(item)] == item.lower()

def fuzzy_match(target,item,match_fucn=None):
    """
    This function matches an item to a target list.  It is expected that the 'item' comes from user input and 
    we want to accept a 'close-enough' match to the target list and validate that there is a unique close-enough 
    match.
    
    :param target:  list of possible matches
    :param item:  item to find in the list
    :param match_fucn:  callable function taking 2 parameters (first from the target list, second is item) and returning a boolean
        if match_fucn is None then it will default initial lower-case matching of strings

    The default approach to matching is testing against case-insensitive prefixes from the target strings. 
    This is illustrated in the examples below.

    Examples:
    >>> fuzzy_match(['aab','bba','abc'],'aa')
    'aab'
    >>> try:
    ...     fuzzy_match(['aab','bba','abc'],'a')  # two strings starting with 'a'.
    ... except Exception, e:
    ...     repr(e)
    "ValueError('ambigious match',)"
    >>> fuzzy_match(['aab','bba','abc'],'b')
    'bba'
    """

    if match_fucn is None:
        def default_match(t,item):
            return t.lower()[:len(item)] == item.lower()

        match_fucn = default_match

    candidates = [t for t in target if match_fucn(t,item)]
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        return None
    else:
        raise ValueError("ambigious match")

def str_to_month(s):
    """
    >>> str_to_month("ja")
    1
    >>> str_to_month("mar")
    3
    """
    months = ["january","february","march","april","may","june","july","august","september","october","november","december"]
    indexed = [(months[i], i)for i in range(len(months))]
    return fuzzy_match(indexed, s, match_fucn=lambda x, y: default_match(x[0], y))[1]+1

def str_to_date_int(s):
    """
    :param s:  an input string to parse
    :return: a 3-tuple of numeric 4 digit year, month index 1-12 and day 1-31

    This function probably has a twisted american bias.  I say "twisted" because I tend to prefer yyyy-mm-dd for my own 
    personal date entry.  However, the applications I write are for US citizens.
    
    >>> str_to_date_int("feb 2 2011")
    (2011, 2, 2)
    >>> str_to_date_int("2010.3.11")
    (2010, 3, 11)
    """
    m = re.match("([a-zA-Z]*) ([0-9]+)(,|) ([0-9]+)",s)
    if m:
        return int(m.group(4)),str_to_month(m.group(1)),int(m.group(2))
    m = re.match("([a-zA-Z]*) ([0-9]+)",s)
    if m:
        return None,str_to_month(m.group(1)),int(m.group(2))
    # yyyy-mm-dd
    m = re.match("([0-9]{4})[-./]([0-9]{1,2})[-./]([0-9]{1,2})",s)
    if m:
        return int(m.group(1)),int(m.group(2)),int(m.group(3))
    # mm-dd-yyyy
    m = re.match("([0-9]{1,2})[-./]([0-9]{1,2})[-./]([0-9]{4})",s)
    if m:
        return int(m.group(3)),int(m.group(1)),int(m.group(2))
    m = re.match("(-|\+)([0-9]+)",s)
    if m:
        if m.group(1)=='+':
            d = datetime.date.today() + datetime.timedelta(int(m.group(2)))
        elif m.group(1)=='-':
            d = datetime.date.today() - datetime.timedelta(int(m.group(2)))
        return d.year,d.month,d.day
    raise NotImplementedError
    return None,None,None

def str_to_date(s):
    """
    Parses input `s` into a date.  The accepted date formats are quite flexible.
    
    jan 12, 2003
    jan 5
    2004-3-5
    +34 -- 34 days in the future (relative to todays date)
    -4 -- 4 days in the past (relative to todays date)
    """
    year,month,day = str_to_date_int(s)
    if year is None:
        year = datetime.date.today().year
    if month is None:
        month = datetime.date.today().month
    if day is None:
        day = datetime.date.today().day
    return datetime.date(year,month,day)

def sanitized_date(d):
    """
    :param d: d can be a datetime.date, None or something else.
    
    This function only pre-checks the type for a date type or None before passing the 
    lone parameter on to str_to_date.
    
    Examples:
    >>> sanitized_date('jan 9 1979') # my birthday
    datetime.date(1979, 1, 9)
    >>> sanitized_date('2010-06-17') # my youngest son's birthday
    datetime.date(2010, 6, 17)
    >>> sanitized_date('f 29, 2012')  # february is the unique month starting with 'f'
    datetime.date(2012, 2, 29)
    >>> sanitized_date('+35')-datetime.date.today()
    datetime.timedelta(35)
    """
    if d is None or isinstance(d,datetime.date):
        return d
    else:
        return str_to_date(d)
