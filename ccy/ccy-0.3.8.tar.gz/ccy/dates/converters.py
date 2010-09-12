import time
from datetime import datetime, date

__all__ = ['todate',
           'date2timestamp',
           'timestamp2date',
           'yyyymmdd2date',
           'date2yyyymmdd',
           'juldate2date',
           'date2juldate']

def todate(val):
    if not val:
        raise ValueError("Value not provided")
    if isinstance(val,datetime):
        return val.date()
    elif isinstance(val,date):
        return val
    else:
        try:
            return yyyymmdd2date(val)
        except ValueError:
            return juldate2date(val)


def date2timestamp(dte):
    return int(time.mktime(dte.timetuple()))


def timestamp2date(tstamp):
    "Converts a unix timestamp to a Python datetime object"
    return datetime.fromtimestamp(tstamp).date()


def yyyymmdd2date(dte):
    try:
        y = dte / 10000
        md = dte % 10000
        m = md / 100
        d = md % 100
        return date(y,m,d)
    except:
        raise ValueError('Could not convert %s to date' % dte)
    
def date2yyyymmdd(dte):
    return dte.day + 100*(dte.month + 100*dte.year)
    
def juldate2date(val):
    try:
        val4 = 4*val
        yd  = val4 % 1461
        st  = 1899
        if yd >= 4:
            st = 1900
        yd1 = yd - 241
        y   = val4 / 1461 + st
        if yd1 >= 0:
            q = yd1 /4 * 5 + 308
            qq = q / 153
            qr = q % 153
        else:
            q = yd /4 * 5 + 1833
            qq = q / 153
            qr = q % 153
        m = qq % 12 + 1
        d = qr / 5 + 1
        return date(y,m,d)
    except:
        raise ValueError('Could not convert %s to date' % val)

def date2juldate(val):
    f = 12*val.year + val.month - 22803
    fq = f/12
    fr = f%12
    return (fr*153 + 302)/5 + val.day + fq*1461/4
