# This file is part of the egoboost package which is release under the MIT
# License. You can find the full text of the license in the LICENSE file.
# Copyright (C) 2010 Sebastian Rahlf <basti at redtoad dot de>

from datetime import date, timedelta

def drange(min, max):
    """
    Iterates over day range from min to (excluding) max date.
    """
    day = min
    while day < max:
        yield day
        day += timedelta(days=+1)

def pairs(val):
    """
    Splits a list of values into pairs.
    Example: (a, b, c, d) -> (a, b), (b, c), (c, d)
    """
    if len(val) == 0:
        raise StopIteration
    if len(val) == 1:
        yield (val[0], val[0])
    else:
        pos = iter(val)
        first = pos.next()
        for second in pos:
            yield (first, second)
            first = second

def linear_interpolation(ts):
    """
    Interpolates linearly between points in a time series.
    """
    positions = sorted(ts.keys())
    if len(positions) > 0:
        for tn, tm in pairs(positions):
            dt = (tm-tn).days
            n0 = ts[tn]
            dn = ts[tm] - ts[tn]
            for day in drange(tn, tm):
                yield day, n0 + float((day-tn).days)/dt*dn
        yield tm, ts[tm]

if __name__ == '__main__':
    ts = {
        date(2010,  1,  1) : 0,
        date(2010,  2,  1) : 131,
        date(2010,  3,  1) : 261,
        date(2010,  5,  1) : 1000,
    }

    for day, val in linear_interpolation(ts): 
        print day, val
