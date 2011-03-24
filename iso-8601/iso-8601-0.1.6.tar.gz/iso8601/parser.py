import datetime

def parse(data):
    """
    Handle any of the valid ISO 8601 times, and convert to a python
    datetime object.
    
    >>> parse('2010-01-01')
    datetime.datetime(2010, 1, 1, 0, 0)
    >>> parse('2010-01-01T00:00:00')
    datetime.datetime(2010, 1, 1, 0, 0)
    >>> parse('2010-01-01 00:00:00')
    datetime.datetime(2010, 1, 1, 0, 0)
    >>> parse('2010-01-01 24:00:00')
    datetime.datetime(2010, 1, 2, 0, 0)
    >>> parse('2010-01-01 24:01:00')
    Traceback (most recent call last):
        ...
    ValueError: hour=24 is only permitted at midnight
    >>> parse('2010-01-01T24')
    datetime.datetime(2010, 1, 2, 0, 0)
    
    >>> parse('2010-01-01T01.5')
    datetime.datetime(2010, 1, 1, 1, 30)
    >>> parse('2010-01-01T01:01.5')
    datetime.datetime(2010, 1, 1, 1, 1, 30)
    >>> parse('2010-01-01T01:01:01.5')
    datetime.datetime(2010, 1, 1, 1, 1, 1, 500000)
    >>> parse('2010-01-01T24.5')
    Traceback (most recent call last):
        ...
    ValueError: hour=24 is only permitted at midnight
    >>> parse('2010-01-01T01.5:00')
    Traceback (most recent call last):
        ...
    ValueError: fractional time may only apply to last component
    >>> parse('2010-01-01T01.5:00.5')
    Traceback (most recent call last):
        ...
    ValueError: fractional time may only apply to last component
    
    """
    
    if isinstance(data, (datetime.datetime, datetime.date)):
        return data
    
    if 'T' not in data:
        data = data.replace(' ', 'T')
    
    if '-' not in data.split('T')[0]:
        basic = True
        DATE = "%Y%m%d"
    else:
        basic = False
        DATE = "%Y-%m-%d"
    
    if 'T' not in data:
        return datetime.datetime.strptime(data, DATE)
    
    time = data.split('T')[1].replace(',', '.')
    fraction = 0
    
    if time.count('.') > 1:
        raise ValueError('fractional time may only apply to last component')
    if time.count('.'):
        try:
            fraction = float("0.%s" %time.split('.')[1])
        except ValueError, arg:
            if arg.args[0].startswith('invalid literal for float():'):
                raise ValueError("fractional time may only apply to last component")
            raise
    
    time = time.split('.')[0]
    
    if basic:
        chars = len(time)
        if chars == 2:
            TIME = "%H"
        elif chars == 4:
            TIME = "%H%M"
        elif chars == 6:
            TIME = "%H%M%S"
    else:
        if time.count(':') == 0:
            TIME = "%H"
        elif time.count(':') == 1:
            TIME = "%H:%M"
        elif time.count(':') == 2:
            TIME = "%H:%M:%S"
    
    if "%S" in TIME:
        addition = datetime.timedelta(seconds=fraction)
    elif "%M" in TIME:
        addition = datetime.timedelta(minutes=fraction)
    elif "%H" in TIME:
        addition = datetime.timedelta(hours=fraction)
    
    if time.startswith('24'):
        no_hours = time[2:].replace(':','')
        if (no_hours != '' and int(no_hours) != 0) or addition:
            raise ValueError('hour=24 is only permitted at midnight')
        data = data.replace('T24', 'T00')
        add_day = True
    else:
        add_day = False
        
    date = datetime.datetime.strptime(data.split('.')[0], DATE + 'T' + TIME)
    
    if add_day:
        date = date + datetime.timedelta(1)
    
    return date + addition

if __name__ == "__main__":
    import doctest
    doctest.testmod()