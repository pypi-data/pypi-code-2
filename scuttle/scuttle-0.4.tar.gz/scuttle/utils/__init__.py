import datetime
import re
import time

IP_RE = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
URL_RE = re.compile("^(https?|ftp)://")
    # r'^(https?|ftp)://' # http:// or https:// or ftp://
    # r'(?:(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6}|' #domain...
    # r'localhost|' #localhost...
    # r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    # r'(?::\d+)?' # optional port
    # r'(?:/?|/\S+)$', re.IGNORECASE)

def encode_value(value):
    if isinstance(value, basestring):
        if isinstance(value, unicode):
            value = value.encode('utf-8')

        if URL_RE.match(value):
            typ = 'url'
        elif IP_RE.match(value):
            typ = 'ip_address'
        else:
            typ = 'string'
    elif isinstance(value, bool):
        value = str(int(value))
        typ = 'bool'
    elif isinstance(value, (int, long)):
        value = str(value)
        typ = 'integer'
    elif isinstance(value, float):
        value = "%.3f" % value
        typ = 'float'
    elif isinstance(value, datetime.timedelta):
        value = str(int(value.days*24*60*60 + value.seconds))
        typ = 'duration'
    elif isinstance(value, datetime.datetime):
        value = str(int(time.mktime(value.timetuple())))
        typ = 'timestamp'
    elif isinstance(value, (list, tuple)):
        value = ",".join(value)
        typ = 'tags'
    else:
        raise TypeError("Unsupported attribute value of type %s" % type(value))

    return (value, typ)
