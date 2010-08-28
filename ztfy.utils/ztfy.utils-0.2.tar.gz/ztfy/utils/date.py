### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
from datetime import datetime

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.datetime import parseDatetimetz

# import local packages
from timezone import gmtime


def unidate(value):
    """Get specified date converted to unicode ISO format
    
    Dates are always assumed to be stored in GMT timezone
    
    @param value: input date to convert to unicode
    @type value: date or datetime
    @return: input date converted to unicode
    @rtype: unicode
    """
    if value is not None:
        value = gmtime(value)
        return unicode(value.isoformat('T'), 'ascii')
    return None


def parsedate(value):
    """Get date specified in unicode ISO format to Python datetime object
    
    Dates are always assumed to be stored in GMT timezone
    
    @param value: unicode date to be parsed
    @type value: unicode
    @return: the specified value, converted to datetime
    @rtype: datetime
    """
    if value is not None:
        return gmtime(parseDatetimetz(value))
    return None


def datetodatetime(value):
    """Get datetime value converted from a date or datetime object
    
    @param value: a date or datetime value to convert
    @type value: date or datetime
    @return: input value converted to datetime
    @rtype: datetime
    """
    if type(value) is datetime:
        return value
    return datetime(value.year, value.month, value.day)
