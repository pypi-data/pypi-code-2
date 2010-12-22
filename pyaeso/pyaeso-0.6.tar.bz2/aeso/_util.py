from datetime import timedelta

class DayBlockIt(object):
    '''Steps over blocks of days between two time periods.  Each call to
    next() will return a 2-tuple containing a start date and end date as
    far apart as is permitted by the /days/ parameter.

    .. versionadded:: 0.6

    Example::

        >>> from aeso._util import DayBlockIt
        >>> from datetime import date
        >>>
        >>> start_date = date(1995, 1, 1)
        >>> end_date = date(1995, 1, 10)
        >>>
        >>> it = DayBlockIt(start_date, end_date, 4)
        >>> for first, last in it:
        ...   print first, last
        ...
        1995-01-01 1995-01-04
        1995-01-05 1995-01-08
        1995-01-09 1995-01-10
    '''

    def __init__(self, start_date, end_date, days):
        '''Create an object that iterates blocks of start/end dates of length
        /days/.

        @param days:  maximum number of days in each step.

        @type start_date: datetime.date
        @type end_date: datetime.date
        @type days: int
        '''
        if days == 0:
            raise ValueError('DayBlockIt() arg 3 must not be zero')
        self._delta = timedelta(days)
        self._delta_less_one = timedelta(days - days / abs(days))
        self._now = start_date
        self._start_date = start_date
        self._end_date = end_date

    def __iter__(self):
        return self

    def next(self):
        if (self._start_date <= self._now and self._now <= self._end_date) or \
            (self._start_date >= self._now and self._now >= self._end_date):
            start_date = self._now
            end_date = self._now + self._delta_less_one

            self._now = self._now + self._delta
            if self._start_date <= self._end_date:
                if self._now > self._end_date:
                    end_date = self._end_date
            else:
                if self._now < self._end_date:
                    end_date = self._end_date

            return (start_date, end_date)
        else:
            raise StopIteration()
