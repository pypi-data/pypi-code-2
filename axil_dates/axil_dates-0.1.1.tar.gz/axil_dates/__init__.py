'''
Utilities for common date and time features.
'''
import datetime as original
from dateutil.parser import parse
from dateutil.tz import tzlocal

from django.conf import settings

datetime  = original.datetime
time      = original.time
date      = original.date
timedelta = original.timedelta

TZLOCAL       = tzlocal()
MIDNIGHT      = time(0)
END_OF_DAY    = time(23, 59, 59)
PAST_24_HOURS = timedelta(hours=24)
SIX_AM        = time(6, 0)
WEEK_DELTA    = timedelta(days=6)

Q1 = (1,  1,  3, 31)
Q2 = (2,  4,  6, 30)
Q3 = (3,  7,  9, 30)
Q4 = (4, 10, 12, 31)

QUARTERS_BOUNDRIES = {
     1 : Q1,  2 : Q1,  3 : Q1,
     4 : Q2,  5 : Q2,  6 : Q2,
     7 : Q3,  8 : Q3,  9 : Q3,
    10 : Q4, 11 : Q4, 12 : Q4,
}

_now = datetime.now


#===============================================================================
class IterDates(object):
    '''
    Date range generators
    '''
    QUARTER_MONTHS = dict([q[:2] for q in (Q1, Q2, Q3, Q4)])
    
    #---------------------------------------------------------------------------
    @staticmethod
    def imonth(dt):
        '''
        Month generator
        '''
        m, y = dt.month, dt.year
        while 1:
            yield date(y, m, 1)
            if m == 12:
                m = 1
                y += 1
            else:
                m += 1

    #---------------------------------------------------------------------------
    @staticmethod
    def iday(dt, days=1):
        '''
        Day generator
        '''
        td = timedelta(days=days)
        while 1:
            yield dt
            dt += td
        
    #---------------------------------------------------------------------------
    @staticmethod
    def idays(days):
        '''
        Day generator factory
        '''
        def inner(dt):
            return IterDates.iday(dt, days)
                
        return inner
        
    #---------------------------------------------------------------------------
    @staticmethod
    def iyear(dt):
        '''
        Year generator
        '''
        y = dt.year
        while 1:
            yield date(y, 1, 1)
            y += 1
            
    #---------------------------------------------------------------------------
    @staticmethod
    def iquarter(dt):
        '''
        Quarter generator
        '''
        Q = IterDates.QUARTER_MONTHS
        q, y = QUARTERS_BOUNDRIES[dt.month][0], dt.year
        while 1:
            yield date(y, Q[q], 1)
            if q == 4:
                q = 1
                y += 1
            else:
                q += 1



#-------------------------------------------------------------------------------
def quarter_boundaries(dt):
    quarter, m1, m2, m2d = QUARTERS_BOUNDRIES[dt.month]
    return quarter, date(dt.year, m1, 1), date(dt.year, m2, m2d)

#-------------------------------------------------------------------------------
def day_diff(date1,date2):
    """
    Given two dates it will return their difference in days.
    
    >>> import datetime
    >>> date_1 = datetime.datetime(2010, 3, 23, 0, 0)
    >>> date_2 = datetime.datetime(2010, 3, 24, 0, 0)
    >>> date_3 = datetime.date(2010, 3, 23)
    >>> date_4 = datetime.date(2010, 3, 24)
    >>> date_5 = datetime.datetime(2010, 3, 24, 9, 30)
    
    >>> day_diff(date_1,date_2)
    -1
    >>> day_diff(date_2,date_1)
    1
    >>> day_diff(date_1,date_4)
    -1
    >>> day_diff(date_4,date_1)
    1
    >>> day_diff(date_3,date_4)
    -1
    >>> day_diff(date_4,date_3)
    1
    >>> day_diff(date_1,date_3)
    0
    >>> day_diff(date_3,date_1)
    0
    >>> day_diff(date_1,date_1)
    0
    >>> day_diff(date_3,date_3)
    0
    >>> day_diff(date_1,date_5)
    -2
    >>> day_diff(date_5,date_1)
    1
    >>> day_diff(date_4,date_5)
    -1
    >>> day_diff(date_5,date_4)
    0
    """
    
    n_date1 = normalize(date1)
    n_date2 = normalize(date2)
    n_diff =  n_date1 - n_date2
    return n_diff.days

#-------------------------------------------------------------------------------
def datetime_now():
    '''
    A smart wrapper for the ``datetime.now`` factory which allows the possible 
    "faking" of date and timestamps (see ``set_fake_datetime``).
    '''
    return _now()
  
#-------------------------------------------------------------------------------
def set_time_for_date(dt,time_to_set):
    '''
    Given a date reset it's time to the time passed
    '''
    return datetime.combine(dt, time_to_set) 
   
#-------------------------------------------------------------------------------
def hours_ago(hours):
    '''
    A smart wrapper around today, that allow you to specify a date in the past by the number of hours.
    which allows the possible "faking" of date and timestamps (see ``set_fake_datetime``).
    '''
    return today() - timedelta(hours=hours)

#-------------------------------------------------------------------------------
def days_ago(days):
    '''
    A smart wrapper around today, that allow you to specify a date in the past by the number of days.
    which allows the possible "faking" of date and timestamps (see ``set_fake_datetime``).
    '''
    return today() - timedelta(days=days)
    
#-------------------------------------------------------------------------------
def days_in_future(days):
    '''
    A smart wrapper around today, that allow you to specify a date in the future by the number of days.
    which allows the possible "faking" of date and timestamps (see ``set_fake_datetime``).
    '''
    return today() + timedelta(days=days)

#-------------------------------------------------------------------------------
def today():
    '''
    A smart wrapper for the ``date.today()`` factory that allows for "faking" 
    of system dates (see ``set_fake_datetime``).
    '''
    return datetime_now().today()


#-------------------------------------------------------------------------------
def date_now():
    '''
    A smart wrapper for the ``datetime.now().date()`` factory that allows for 
    "faking" of system dates (see ``set_fake_datetime``).
    '''
    return datetime_now().date()
    

#-------------------------------------------------------------------------------
def time_now():
    '''
    A smart wrapper for the ``datetime.now().time()`` factory that allows for 
    "faking" of system dates (see ``set_fake_datetime``).
    '''
    return datetime_now().time()


#-------------------------------------------------------------------------------
def set_fake_datetime(*dt):
    '''
    Sets the current datetime to a relative point in time for faking system
    timestamps. 
    
    Accepts the same parameters as ``datetime.datetime``.
    '''
    global _now
    ago = original.datetime.now() - original.datetime(*dt)
    
    #---------------------------------------------------------------------------
    def __now():
        return original.datetime.now() - ago
        
    _now = __now
    
    # global datetime, time, date
    # ago = original.datetime.now() - original.datetime(*dt)
    # 
    # #===========================================================================
    # class DateTime(original.datetime):
    #     
    #     #-----------------------------------------------------------------------
    #     @staticmethod
    #     def now():
    #         return original.datetime.now() - ago
    # 
    # datetime = DateTime
    #         
    # #===========================================================================
    # class Date(original.date):
    # 
    #     #-----------------------------------------------------------------------
    #     @staticmethod
    #     def today():
    #         return (original.datetime.now() - ago).date()
    # 
    # date = Date


#-------------------------------------------------------------------------------
def _get_datetime_now():
    '''
    If the standard Django settings file has an entry for ``DATETIME_NOW``, it will
    be used to calculate the result for calls to `datetime_now`, below.
    
    Options for ``DATETIME_NOW`` are:
    
    *   A callable accepting no args
    *   A list or tuple of inputs to be passed to the ``datetime.now`` factory
    *   A ``datetime object``, as is
     
    '''
    dtn = getattr(settings, 'DATETIME_NOW', None)
    if dtn:
        # for testing purposes
        if callable(dtn):
            return dtn
            
        if isinstance(dtn, (tuple, list)):
            dtn = datetime(*dtn)
            
        return lambda: dtn
        
    return datetime.now


#-------------------------------------------------------------------------------
def normalize_datetime_range(start=None, end=None):
    '''
    Gets a 2-tuple of ``(start, end)`` values normalized to ``datetime`` objects,
    where ``start`` is set to midnight and ``end`` is set to 23:59:59.
    
    Allowable inputs: ``datetime``, ``date``, ``str``, or ``unicode``. ``end``
    is optional and will default to today.
    '''
    if not start:
        start = today()
    elif isinstance(start, datetime):
        start = start.date()
    elif isinstance(start, basestring):
        start = parse(start).date()

    if not end:
        end = today()
    else:
        if isinstance(end, datetime):
            end = end.date()
        elif isinstance(end, basestring):
            end = parse(end).date()

    return (
        datetime.combine(start, MIDNIGHT),
        datetime.combine(end, END_OF_DAY)
    )

#-------------------------------------------------------------------------------
def datetime_tzutc(dt_string):
    '''
    Parse the ``dt_string`` as a UTC timezone string and return the UTC 
    ``datetime`` object.
    '''
    return parse(dt_string)


#-------------------------------------------------------------------------------
def datetime_tzlocal(dt_string):
    '''
    Parse the ``dt_string`` as a local timezone string and return the timezone
    aware ``datetime`` object.
    '''
    return parse(dt_string).astimezone(TZLOCAL)


#-------------------------------------------------------------------------------
def datetime_utc(dt_string):
    '''
    Parse the ``dt_string`` as a UTC timezone string and return the ``datetime`` 
    object **without** the timezone.
    '''
    return datetime_tzutc(dtstring).replace(tzinfo=None)


#-------------------------------------------------------------------------------
def datetime_local(dt_string):
    '''
    Parse the ``dt_string`` as a local timezone string and return the ``datetime`` 
    object **without** the timezone.
    '''
    return datetime_tzlocal(dt_string).replace(tzinfo=None)


#-------------------------------------------------------------------------------
def date_to_datetime(dt):
    '''
    Convert a ``date`` object to a ``datetime`` object set to midnight.
    '''
    return datetime.combine(dt, MIDNIGHT)
    

#-------------------------------------------------------------------------------
def time_to_datetime(tm):
    '''
    Convert a ``time`` object to a ``datetime`` object with today's date
    '''
    return datetime.combine(today().date(), tm)


_NORMALIZERS = {
    type(time(0))        : time_to_datetime,
    type('')             : parse,
    type(u'')            : parse,
    type([])             : lambda v: datetime(*v),
    type(())             : lambda v: datetime(*v),
    type({})             : lambda v: datetime(**v)
}


#-------------------------------------------------------------------------------
def normalize(value):
    '''
    Converts various object types to a ``datetime`` object. Allowed input objects:
    
    * ``datetime``, ``date`` or ``time``
    * ``str`` or ``unicode`` (parses using ``parse``)
    * ``list``, ``tuple``, or ``dict`` (valid ``datetime`` parameters)
    '''
    if isinstance(value, original.datetime):
        return value
    elif isinstance(value, original.date):
        return date_to_datetime(value)
    else:
        return _NORMALIZERS.get(type(value))(value)


#-------------------------------------------------------------------------------
def timedelta_now(**kws):
    '''
    Gets a ``timedelta`` object relative to now.
    '''
    return datetime_now() + timedelta(**kws)
    

#-------------------------------------------------------------------------------
def test():
    """
    >>> set_fake_datetime(2009, 9, 12, 13, 14,0,0)
    >>> datetime_now()
    datetime.datetime(2009, 9, 12, 13, 14)
    >>> today()
    2009-09-12
    """
    print datetime.now()
    print date.today()
    set_fake_datetime(2009, 9, 12, 13, 14)
    print datetime.now()
    print date.today()


################################################################################
if __name__ == '__main__':
    test()
    import doctest
    doctest.testmod()
