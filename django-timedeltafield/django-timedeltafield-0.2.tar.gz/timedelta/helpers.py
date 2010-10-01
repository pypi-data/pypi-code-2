
import re
import datetime
from decimal import Decimal

def nice_repr(timedelta, display="long"):
    """
    Turns a datetime.timedelta object into a nice string repr.
    
    display can be "minimal", "short" or "long" [default].
    
    >>> from datetime import timedelta as td
    >>> nice_repr(td(days=1, hours=2, minutes=3, seconds=4))
    '1 day, 2 hours, 3 minutes, 4 seconds'
    >>> nice_repr(td(days=1, seconds=1), "minimal")
    '1d, 1s'
    """
    
    assert isinstance(timedelta, datetime.timedelta), "First argument must be a timedelta."
    
    result = ""
    
    weeks = timedelta.days / 7
    days = timedelta.days % 7
    hours = timedelta.seconds / 3600
    minutes = (timedelta.seconds % 3600) / 60
    seconds = timedelta.seconds % 60
    
    if display == 'minimal':
        words = ["w", "d", "h", "m", "s"]
    elif display == 'short':
        words = [" wks", " days", " hrs", " min", " sec"]
    else:
        words = [" weeks", " days", " hours", " minutes", " seconds"]
    
    values = [weeks, days, hours, minutes, seconds]
    
    for i in range(len(values)):
        if values[i]:
            if values[i] == 1 and len(words[i]) > 1:
                result += "%i%s, " % (values[i], words[i].rstrip('s'))
            else:
                result += "%i%s, " % (values[i], words[i])
    
    return result[:-2]

def parse(string):
    """
    Parse a string into a timedelta object.
    
    >>> parse("1 day")
    datetime.timedelta(1)
    >>> parse("2 days")
    datetime.timedelta(2)
    """
    # This is the format we sometimes get from Postgres.
    d = re.match(r'((?P<days>\d+) days )?(?P<hours>\d+):'
                 r'(?P<minutes>\d+)(:(?P<seconds>\d+))?',
                 str(string))
    if d: 
        d = d.groupdict(0)
    else:
        # This is the more flexible format
        d = re.match(
                     r'^((?P<weeks>((\d*\.\d+)|\d+))\W*w((ee)?k(s)?)(,)?\W*)?'
                     r'((?P<days>((\d*\.\d+)|\d+))\W*d(ay(s)?)?(,)?\W*)?'
                     r'((?P<hours>((\d*\.\d+)|\d+))\W*h(ou)?r(s)?(,)?\W*)?'
                     r'((?P<minutes>((\d*\.\d+)|\d+))\W*m(in(ute)?)?(s)?(,)?\W*)?'
                     r'((?P<seconds>((\d*\.\d+)|\d+))\W*s(ec(ond)?(s)?)?)?\W*$',
                     str(string))
        if not d:
            raise TypeError("'%s' is not a valid time interval" % string)
        d = d.groupdict()
    
    return datetime.timedelta(**dict(( (k, float(v)) for k,v in d.items() 
        if v is not None )))


def divide(obj1, obj2, float=False):
    """
    Allows for the division of timedeltas by other timedeltas, or by
    floats/Decimals
    """
    assert isinstance(obj1, datetime.timedelta), "First argument must be a timedelta."
    #assert isinstance(obj2, (datetime.timedelta, int, float, Decimal)), "Second argument must be a timedelta or number"
    
    sec1 = obj1.days * 86400 + obj1.seconds
    if isinstance(obj2, datetime.timedelta):
        sec2 = obj2.days * 86400 + obj2.seconds
        if float:
            sec1 *= 1.0
        return sec1 / sec2
    else:
        if float:
            assert None, "float=True is inappropriate when dividing timedelta by a number."
        secs = sec1 / obj2
        if isinstance(secs, Decimal):
            secs = float(secs)
        return datetime.timedelta(seconds=secs)

def percentage(obj1, obj2):
    """
    What percentage of obj2 is obj1? We want the answer as a float.
    >>> percentage(datetime.timedelta(2), datetime.timedelta(4))
    50.0
    """
    assert isinstance(obj1, datetime.timedelta), "First argument must be a timedelta."
    assert isinstance(obj2, datetime.timedelta), "Second argument must be a timedelta."
    
    return divide(obj1 * 100, obj2, float=True)

def multiply(obj, val):
    """
    Allows for the multiplication of timedeltas by float values.
    """
    
    assert isinstance(obj, datetime.timedelta), "First argument must be a timedelta."
    assert isinstance(val, (int, float, Decimal)), "Second argument must be a number."
    
    sec = obj.days * 86400 + obj.seconds
    sec *= val
    if isinstance(sec, Decimal):
        sec = float(sec)
    return datetime.timedelta(seconds=sec)


def round_to_nearest(obj, timedelta):
    """
    The obj is rounded to the nearest whole number of timedeltas.
    
    obj can be a timedelta, datetime or time object.
    """
    
    assert isinstance(obj, (datetime.datetime, datetime.timedelta, datetime.time)), "First argument must be datetime, time or timedelta."
    assert isinstance(timedelta, datetime.timedelta), "Second argument must be a timedelta."
    
    time_only = False
    if isinstance(obj, datetime.timedelta):
        counter = datetime.timedelta(0)
    elif isinstance(obj, datetime.datetime):
        counter = datetime.datetime.combine(obj.date(), datetime.time(0, tzinfo=obj.tzinfo))
    elif isinstance(obj, datetime.time):
        counter = datetime.datetime.combine(datetime.date.today(), datetime.time(0, tzinfo=obj.tzinfo))
        obj = datetime.datetime.combine(datetime.date.today(), obj)
        time_only = True
    
    diff = abs(obj - counter)
    while counter < obj:
        old_diff = diff
        counter += timedelta
        diff = abs(obj - counter)
    
    if counter == obj:
        result = obj
    elif diff <= old_diff:
        result = counter
    else:
        result = counter - timedelta
    
    if time_only:
        return result.time()
    else:
        return result

def decimal_hours(timedelta):
    """
    Return a decimal value of the number of hours that this timedelta
    object refers to.
    """
    return Decimal(timedelta.days*24) + Decimal(timedelta.seconds) / 3600