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
    """
    
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
    
    if basic:
        chars = len(data.split('T')[1])
        if chars == 2:
            TIME = "%H"
        elif chars == 4:
            TIME = "%H%M"
        elif chars == 6:
            TIME = "%H%M%S"
    else:
        if data.count(':') == 0:
            TIME = "%H"
        elif data.count(':') == 1:
            TIME = "%H:%M"
        elif data.count(':') == 2:
            TIME = "%H:%M:%S"
    
    if 'T24' in data:
        time = data.split('T')[1][2:].replace(':','')
        if time != '' and int(time) != 0:
            raise ValueError('hour=24 is only permitted at midnight')
        data = data.replace('T24', 'T00')
        add_day = True
    else:
        add_day = False
        
    date = datetime.datetime.strptime(data, DATE + 'T' + TIME)
    
    if add_day:
        date = date + datetime.timedelta(1)
    
    return date

if __name__ == "__main__":
    import doctest
    doctest.testmod()