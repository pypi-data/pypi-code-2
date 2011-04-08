#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
"""
.. :doctest:


"""

import time
import datetime
import calendar

from .timezone import UTC


def datetime_to_timestamp(dt):
    """Converts a datetime object to UTC timestamp

    This function uses utc_mktime (see doc).

    Usage
    =====

    >>> from sact.epoch import datetime_to_timestamp
    >>> from sact.epoch import utc_mktime
    >>> import datetime

    >>> epoch = datetime.datetime(1970,1,1)
    >>> datetime_to_timestamp(epoch)
    0

    Let's add one hour:

    >>> anhour = datetime.timedelta(hours=1)
    >>> datetime_to_timestamp(epoch + anhour)
    3600

    """
    return int(utc_mktime(dt.timetuple()))


def ts2iso(ts):
    """Returns a ISO representation of a timestamp

    >>> from sact.epoch import iso2ts, ts2iso

    >>> ts2iso(iso2ts('1970-01-01 00:00:00'))
    '1970-01-01 00:00:00'

    >>> ts2iso(iso2ts('2008-11-01 10:00:00'))
    '2008-11-01 10:00:00'

    """
    return datetime.datetime.utcfromtimestamp(ts).isoformat(" ")


def localtime_to_utctime(dt):
    """Convert local time to utc time.

    The datetime argument must be set with tzinfo.
    It is used only for test.

    Return a datetime object with utc tzinfo setted.

    >>> from sact.epoch import localtime_to_utctime, TzLocal, datetime_to_timestamp
    >>> import datetime
    >>> import time
    >>> import pytz

    Now we have a datetime with time zone info setted to the locale time zone.
    With that we only have to change timezone to have the time we want.

    >>> localtime = datetime.datetime(2008, 07, 01, 10, 00, 00, tzinfo=TzLocal())

    Get timestamp from localtime

    >>> local_timestamp = time.mktime(localtime.timetuple())

    >>> utctime = localtime_to_utctime(localtime)

    Get timestamp from utc datetime

    >>> utc_timestamp = datetime_to_timestamp(utctime)
    >>> utc_timestamp - local_timestamp
    0.0

    Normal, it's the same timestamp !

    Note that datetime without time zone setted is a naïve datetime.
    Normaly, we do not use it everywhere

    >>> localtime = datetime.datetime(2008, 07, 01, 10, 00, 00)
    >>> localtime_to_utctime(localtime)
    Traceback (most recent call last):
    ...
    Exception: Datetime is naive, need tzinfo value

    """

    if dt.tzinfo is None:
        raise Exception("Datetime is naive, need tzinfo value")
    return dt.astimezone(UTC())


def iso2ts(iso_repr):
    """Returns a timestamp from a full iso represenation

    Note that it doesn't take into account local representation.

    >>> from sact.epoch import iso2ts
    >>> import datetime
    >>> import time

    EPOCH should return 0 as expected:

    >>> iso2ts('1970-01-01 00:00:00')
    0

    >>> iso2ts('1970-01-01 00:01:00')
    60

    >>> iso2ts('1970-01-01 01:00:00')
    3600

    And with any date, we should be able to reconstruct it:

    >>> time.gmtime(iso2ts('1970-01-01 00:00:00'))[0:6]
    (1970, 1, 1, 0, 0, 0)

    >>> time.gmtime(iso2ts('2008-12-06 12:17:31'))[0:6]
    (2008, 12, 6, 12, 17, 31)

    >>> time.gmtime(iso2ts('2008-05-06 12:17:31'))[0:6]
    (2008, 5, 6, 12, 17, 31)

    """

    return int(utc_mktime(time.strptime(iso_repr + " UTC",
                                        "%Y-%m-%d %H:%M:%S %Z")))


def utc_mktime(utc_tuple):
    """Returns number of seconds elapsed since epoch

    Note that no timezone are taken into consideration. So
    this is equivalent to consider the time tuple as an UTC
    time tuple.

    utc tuple must be: (year, month, day, hour, minute, seconde)

    >>> from sact.epoch import utc_mktime
    >>> import time

    >>> utc_mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))
    0.0
    >>> timestamp = utc_mktime((2008, 8, 8, 8, 8, 8, 0, 0, 0))


    utc mktime is gmtime oposite

    >>> time.gmtime(timestamp)[0:6]
    (2008, 8, 8, 8, 8, 8)

    Checking that locale time is not taken into account:

    >>> t1 = utc_mktime((2008, 12, 6, 12, 15, 15, 0, 0, 0))
    >>> t2 = utc_mktime((2008, 5, 6, 12, 15, 15, 0, 0, 0))

    >>> time.gmtime(t1)[3]
    12
    >>> time.gmtime(t2)[3]
    12

    """
    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return time.mktime(utc_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))


def min_interval(nbseconds, timestamp):
    """Get greatest grid boundary smaller than timestamp on a timegrid of nbseconds width"""
    return timestamp - (timestamp % nbseconds)


def max_interval(nbseconds, timestamp):
    """Get smallest grid boundary greater than timestamp on a timegrid of nbseconds width"""
    return timestamp - (timestamp % nbseconds) + nbseconds



def lt_strptime_to_utc_ts(str, format, tzinfo=None):
    """Returns an UTC timestamp from user defined format localtime strptime

    Optionaly you can specify tzinfo which will be defaulted to local timezone.

    Usage
    =====

    >>> from sact.epoch import lt_strptime_to_utc_ts, TzTest

    Let's use our testing GMT timezone. Notice that it is 5 minute
    ahead from UTC.

    Let's check that 'local' EPOCH is 5 minutes ahead from real UTC EPOCH:

    >>> lt_strptime_to_utc_ts('1970-01-01 00:05',
    ...     format='%Y-%m-%d %H:%M', tzinfo=TzTest())
    0

    """

    if tzinfo is None:
        tzinfo = tz.TzLocal()

    lt_time_tuple = time.strptime(str, format)

    naive_dt = datetime.datetime.strptime(str, format)
    lt_dt = naive_dt.replace(tzinfo=tzinfo)
    utc_ts = calendar.timegm(lt_dt.utctimetuple())
    return utc_ts
