# This file is part of the egoboost package which is release under the MIT
# License. You can find the full text of the license in the LICENSE file.
# Copyright (C) 2010-2010 Sebastian Rahlf <basti at redtoad dot de>

from datetime import date, timedelta
from collections import defaultdict

class GuessedValue (float):

    """
    GuessedValue marks a float value that has been inter- or extrapolated. It
    can used and calculated with like any normal float.
    """

    def __add__(self, other):
        return GuessedValue(super(GuessedValue, self).__add__(other))
    def __radd__(self, other):
        return GuessedValue(super(GuessedValue, self).__radd__(other))
    def __sub__(self, other):
        return GuessedValue(super(GuessedValue, self).__sub__(other))
    def __rsub__(self, other):
        return GuessedValue(super(GuessedValue, self).__rsub__(other))
    def __div__(self, other):
        return GuessedValue(super(GuessedValue, self).__div__(other))
    def __rdiv__(self, other):
        return GuessedValue(super(GuessedValue, self).__rdiv__(other))
    def __mul__(self, other):
        return GuessedValue(super(GuessedValue, self).__mul__(other))
    def __rmul__(self, other):
        return GuessedValue(super(GuessedValue, self).__rmul__(other))
    def __pow__(self, other):
        return GuessedValue(super(GuessedValue, self).__pow__(other))
    def __rpow__(self, other):
        return GuessedValue(super(GuessedValue, self).__rpow__(other))
    def __repr__(self):
        return '~%s' % self

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
                value = n0 + float((day-tn).days)/dt*dn
                if day in positions:
                    yield day, ts[day]
                else:
                    yield day, GuessedValue(value)
        yield tm, ts[tm]

def lazy_extrapolation(tp, ts):
    """
    Extrapolates value at timepoint (tp) from timeseries data points (ts).
    """
    tps = sorted(ts.keys())
    first, last = tps[0], tps[-1]
    if tp == first:
        return ts[first]
    if tp == last:
        return ts[last]
    if tp < first:
        return GuessedValue(0)
    if tp > last:
        return GuessedValue(ts[last])
    raise ValueError('%s inside data set!')

def accumulate_timeseries(datasets,
        inter=linear_interpolation, extra=lazy_extrapolation):
    """
    Accumulates (adds) a list of time series data sets. Missing points inside
    each set are interpolated (using ``inter``), points outside the different
    which covered in another set are extrapolated (using ``extra``).

    Example::

        >>> A = {
        ...     date(2011, 1, 2) : 4,
        ...     date(2011, 1, 3) : 5,
        ...     date(2011, 1, 5) : 6,
        ...     date(2011, 1, 6) : 6,
        ...     date(2011, 1, 7) : 7
        ...     }
        >>> B = {
        ...     date(2011, 1, 1) : 1,
        ...     date(2011, 1, 2) : 2,
        ...     date(2011, 1, 4) : 2,
        ...     date(2011, 1, 5) : 2,
        ...     date(2011, 1, 6) : 3
        ... }
        >>> accumulate_timeseries([A, B])
        {
            date(2011, 1, 1) : GuessedValue(1),
            date(2011, 1, 2) : 6,
            date(2011, 1, 3) : GuessedValue(7),
            date(2011, 1, 4) : GuessedValue(7.5),
            date(2011, 1, 5) : 8,
            date(2011, 1, 6) : 9,
            date(2011, 1, 7) : GuessedValue(10)
        }
    """
    data = []
    # determine overall date range
    for dataset in datasets:
        dates = sorted(dataset.keys())
        data.append({
            'range' : (dates[0], dates[-1]),
            'data' : dataset
        })
    first = min(d['range'][0] for d in data)
    last = max(d['range'][1] for d in data)

    result = defaultdict(int)
    for dataset in data:
        dataset['data'][first] = extra(first, dataset['data'])
        dataset['data'][last] = extra(last, dataset['data'])
        for day, val in inter(dataset['data']):
            result[day] += val
            print '%r += %r' % (result[day], val)
            print 'result(%s) = %r' % (day, result[day])
        del dataset['data']
    return result