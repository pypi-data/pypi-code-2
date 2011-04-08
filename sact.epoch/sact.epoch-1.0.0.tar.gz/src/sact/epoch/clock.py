# -*- coding: utf-8 -*-
"""
.. :doctest:

"""


import datetime
import time

from zope.interface import classProvides, implements
from zope.component import queryUtility

from .interfaces import ITime, IClock
from .timezone import UTC, TzLocal
from sact.epoch.utils import datetime_to_timestamp


def round_date(date):
    """Round a timedelta to the last minute (remove seconds and microseconds).

    Setup:

         >>> from sact.epoch import round_date, Time

    Nothing to do:

         >>> round_date(Time(2010, 1, 1, 1, 1, 0))
         <Time 2010-01-01 01:01:00+00:00>

    Round to 1 minute when we have 1 minute and 30 seconds:

         >>> round_date(Time(2010, 1, 1, 1, 1, 30))
         <Time 2010-01-01 01:01:00+00:00>

    """
    assert(isinstance(date, Time))

    if date.second or date.microsecond:
        return date - datetime.timedelta(seconds=date.second,
                                         microseconds=date.microsecond)
    return date


class Clock(object):
    """Time Factory

    Will only serve the current time.

    Usage
    =====

        >>> from sact.epoch.clock import Clock
        >>> c = Clock()

    We can use property 'ts' to get the timestamp and it should change very
    accurately at each call:

        >>> t1 = c.ts
        >>> t2 = c.ts
        >>> t1 < t2
        True

    If we need a full object we should use:

        >>> c.time
        <Time ...>

    """

    implements(IClock)

    @property
    def time(self):
        """Should return later a Time object"""

        return Time.utcfromtimestamp(self.ts)

    @property
    def ts(self):
        return time.time()


class ManageableClock(Clock):
    """Creates a manageable time object

    Can be used to control what time it is. Start/Stop method can
    start/stop time, and wait/set will alter current time.

    Usage
    =====

        >>> from sact.epoch.clock import ManageableClock
        >>> mc = ManageableClock()

    Stopping time
    -------------

        >>> mc.stop()
        >>> t1 = mc.ts
        >>> t2 = mc.ts
        >>> assert t1 == t2, 'time %r should be equal to %r and it isn\'t' \
        ...              % (t1, t2)
        >>> mc.is_running
        False

    Stoping while running should do nothing:

        >>> mc.stop()
        >>> mc.is_running
        False


    Restarting time
    ---------------

        >>> mc.start()
        >>> t1 = mc.ts
        >>> t2 = mc.ts
        >>> assert t1 != t2, 'time %r should NOT be equal to %r and it is' \
        ...              % (t1, t2)
        >>> mc.is_running
        True

    Restarting while running should do nothing:

        >>> mc.start()
        >>> mc.is_running
        True

        >>> t3 = mc.ts
        >>> assert t1 < t3, \
        ...    'time %r should be superior to %r and it isn\'t' \
        ...    % (t3, t1)


    Setting time
    ------------

        >>> mc.stop()
        >>> mc.ts = 0
        >>> mc.ts
        0
        >>> mc.start()
        >>> ts = mc.ts
        >>> assert ts > 0, \
        ...    'clock should have been running and thus timestamp should be greater than 0.' \
        ...    'It was %r.' % ts

    Altering time
    -------------

        >>> mc.stop()
        >>> mc.ts = 20
        >>> mc.ts += 10
        >>> mc.ts
        30
        >>> mc.start()
        >>> ts = mc.ts
        >>> assert ts > 30, \
        ...    'clock should have been running and thus timestamp should be greater than 30.' \
        ...    'It was %r.' % ts

    Setting time should not stop the clock if it was running:

        >>> mc.ts = 20
        >>> mc.is_running
        True


    Altering with wait
    ------------------

        >>> mc.stop()
        >>> mc.ts = 0
        >>> mc.wait(minutes=5)
        >>> mc.ts
        300
        >>> mc.start()
        >>> mc.wait(minutes=5)
        >>> ts = mc.ts
        >>> assert ts > 600, \
        ...    'clock should have been running and thus timestamp should be greater than 600.' \
        ...    'It was %r.' % ts

    """

    implements(IClock)

    def __init__(self):
        self.delta = 0
        self._ft = None ## freezed time

    def start(self):
        if self.is_running:
            return
        ## use _ft to calculate the time delta
        self.delta = self.ts - self.delta - self._ft
        self._ft = None

    def stop(self):
        ## save real current time
        self._ft = self.ts - self.delta

    @property
    def is_running(self):
        return self._ft is None

    def get_ts(self):
        if not self.is_running:
            return self._ft
        return time.time() + self.delta

    def set_ts(self, value):
        self.delta = value - time.time()
        # don't forget to update self._ft
        if self._ft is not None:
            self._ft = value

    ts = property(get_ts, set_ts)

    def wait(self, timedelta=None, **kwargs):
        """Provide a convenient shortcut to alter the current time

        timedelta can be an int/float or a timedelta objet from timedelta

        """
        if timedelta is None:
            timedelta = datetime.timedelta(**kwargs)

        if isinstance(timedelta, datetime.timedelta):
            secs = timedelta.days * 86400 + timedelta.seconds
        else:
            secs = int(timedelta)

        self.ts += secs


DefaultClock = Clock()
DefaultManageableClock = ManageableClock()


class Time(datetime.datetime):
    """Time Factory

      Time is an abstraction of a specific point of time. As a subclass of
    datetime, it provides the same functionality. Additionaly it ensures that a
    timezone is always associated to the Time instance, and some simple common
    representation are provided as properties.

      And most important: Time.now() will silently request for the registered
    clock to get time information, allowing to manage time easily.

      Same mecanism is used to get the local time zone, allowing to override
    the detection of the local time zone when using Time.now_lt().

    Usage
    =====

    This is quite straightforward to use:

        >>> from sact.epoch.clock import Time
        >>> Time.now()
        <Time ...+00:00>

    Notice that it has a timezone information set. Silently, the current time
    was asked to the registered clock available, which is by default the normal
    clock.


    We can give a better view thanks to a manageable clock as time reference:

        >>> from sact.epoch.clock import ManageableClock
        >>> clock = ManageableClock()

    We will stop the time to epoch:

        >>> clock.stop()
        >>> clock.ts = 0

    Let's set it as reference:

    >>> from zope.component import globalSiteManager as gsm
    >>> gsm.registerUtility(clock)

    Now, let's set our TzTest as local timezone, remember it has 5 minutes
    difference to UTC:

    >>> from sact.epoch import testTimeZone
    >>> from sact.epoch.interfaces import ITimeZone

    >>> gsm.registerUtility(testTimeZone, ITimeZone, name='local')

    Here is the result of each function:

        >>> Time.now()
        <Time 1970-01-01 00:00:00+00:00>

        >>> Time.now_lt()
        <Time 1970-01-01 00:05:00+00:05>

    Please note that there are 5 minutes of diff to UTC


    Instanciation
    =============

    It takes same arguments than datetime legacy object:

        >>> Time(1980, 01, 01)
        <Time 1980-01-01 00:00:00+00:00>

    Notice that in this case, it takes the UTC timezone.

    Additionnaly it can take a real datetime as argument:

        >>> from datetime import datetime
        >>> d = datetime(1970, 01, 01, tzinfo=testTimeZone)
        >>> t = Time(d)
        >>> t
        <Time 1970-01-01 00:00:00+00:05>

        >>> Time(t)
        <Time 1970-01-01 00:00:00+00:05>

    Representations
    ^^^^^^^^^^^^^^^

    There are several standard representation that are available:

        >>> t.iso_local
        '1970-01-01 00:00:00+00:05'

    Short local (remove time zone):

        >>> t.short_local
        '1970-01-01 00:00:00'

    Short short local (remove seconds):

        >>> t.short_short_local
        '1970-01-01 00:00'

    """

    classProvides(ITime)

    def __new__(cls, *args, **kwargs):
        if len(args) and isinstance(args[0], datetime.datetime):
            return Time.from_datetime(args[0])

        if 'tzinfo' not in kwargs and len(args) < 8:
            # XXXjballet: to test
            kwargs['tzinfo'] = UTC()
        return super(Time, cls).__new__(cls, *args, **kwargs)

    def __repr__(self):
        return "<Time %s>" % self

    @classmethod
    def from_datetime(cls, dt):
        """Convert a datetime object with timezone to a Time object

        This method provides a handy way to convert datetime objects to Time
        objects:

            >>> import datetime
            >>> from sact.epoch import UTC
            >>> dt = datetime.datetime(2000, 1, 1, tzinfo=UTC())
            >>> Time.from_datetime(dt)
            <Time 2000-01-01 00:00:00+00:00>

        The provided datetime should contain a timezone information or the
        conversion will fail:

            >>> Time.from_datetime(datetime.datetime.now())
            Traceback (most recent call last):
            ...
            ValueError: no timezone set for ...

        """

        if dt.tzinfo is None:
            raise ValueError("no timezone set for %r" % dt)

        return cls(dt.year, dt.month, dt.day, dt.hour,
                   dt.minute, dt.second, dt.microsecond,
                   dt.tzinfo)

    def __add__(self, delta):
        """Override datetime '+' to return a Time object

        Add a timedelta:

            >>> Time(2010, 1, 1) + datetime.timedelta(days=1)
            <Time 2010-01-02 00:00:00+00:00>

        Add an other Time (send the original exception):

            >>> Time(2010, 1, 1) + Time(1970, 1, 1)
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for +: 'Time' and 'Time'

        """
        d = super(Time, self).__add__(delta)
        if isinstance(d, datetime.datetime):
            return self.from_datetime(d)
        return d

    def __sub__(self, delta):
        """Override datetime '-' to return a Time object

        Sub a timedelta:

            >>> Time(2010, 1, 1) - datetime.timedelta(days=1)
            <Time 2009-12-31 00:00:00+00:00>

        Sub an other Time:

            >>> Time(2010, 1, 2) - Time(2010, 1, 1)
            datetime.timedelta(1)

        """
        d = super(Time, self).__sub__(delta)
        if isinstance(d, datetime.datetime):
            return self.from_datetime(d)
        return d

    @staticmethod
    def now():
        utility = queryUtility(IClock, default=DefaultClock)
        return utility.time.replace(tzinfo=UTC())

    @staticmethod
    def now_lt():
        return Time.now().astimezone(TzLocal())

    @classmethod
    def utcfromtimestamp(cls, ts):
        """Return a UTC datetime from a timestamp.

            >>> Time.utcfromtimestamp(0)
            <Time 1970-01-01 00:00:00+00:00>

        """

        dt = super(Time, cls).utcfromtimestamp(ts)
        return dt.replace(tzinfo=UTC())

    @classmethod
    def strptime(cls, value, format, tzinfo):
        """Parse a string to create a Time object.

            >>> from sact.epoch import UTC, TzTest
            >>> Time.strptime('2000-01-01', '%Y-%m-%d', UTC())
            <Time 2000-01-01 00:00:00+00:00>

            >>> tz_test = testTimeZone
            >>> Time.strptime('2000-01-01', '%Y-%m-%d', tz_test).tzinfo == tz_test
            True

        """

        dt = super(Time, cls).strptime(value, format)
        return dt.replace(tzinfo=tzinfo)

    def astimezone(self, tz):
        """Convert Time object to another timezone and return a Time object

        This overrides the datetime's method to return a Time object instead of
        a datetime object:

            >>> type(Time.now().astimezone(testTimeZone))
            <class 'sact.epoch...Time'>

        """

        dt = super(Time, self).astimezone(tz)
        return self.from_datetime(dt)

    @property
    def timestamp(self):
        """Convert this Time instance in a unix timestamp in UTC

        See sact.epoch.utils

            >>> Time(1970, 1, 1, 0, 0, 1).timestamp
            1

        """
        return datetime_to_timestamp(self)

    @property
    def aslocal(self):
        return self.astimezone(TzLocal())

    def strftime_local(self, *args, **kwargs):
        return self.aslocal.strftime(*args, **kwargs)

    @property
    def iso_local(self):
        """Return the iso format in local time

            >>> Time(1970, 1, 1, 1, 1).iso_local
            '1970-01-01 01:06:00+00:05'

        """
        return self.aslocal.isoformat(" ")

    @property
    def short_local(self):
        """Idem than iso_local with without time zone"""
        return self.strftime_local('%Y-%m-%d %H:%M:%S')

    @property
    def short_short_local(self):
        """Idem without seconds"""
        return self.strftime_local('%Y-%m-%d %H:%M')


"""
Let's unregister the test Timezone and test Clock:

    >>> gsm.unregisterUtility(clock)
    True

    >>> gsm.unregisterUtility(testTimeZone, ITimeZone, 'local')
    True

"""
