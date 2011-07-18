from threading import Timer

class set_timeout(object):
    def __init__(self, f, time=None):
        self._time = None

        if time==None:
            #f is actually time
            self._time = f
        else:
            self._set_timeout(f, time)

    #For the decorators.
    def __call__(self, g):
        self._set_timeout(g, self._time)

    def _set_timeout(self, f, time):
        self._timeout = Timer(time, f)
        self._timeout.start()

def clear_timeout(timeout_obj):
    timeout_obj._timeout.cancel()


class set_interval(object):
    def __init__(self, f, time=None):
        self._time = None
        if time==None:
            self._time = f
        else:
            self._set_interval(f, time)

    #For the decorators.
    def __call__(self, g):
        self._set_interval(g, self._time)

    def _set_interval(self, f, time):
        def again(g, t):
            def _again():
                g()
                self._set_interval(g, t)
            return _again

        self._interval = Timer(time, again(f, time))
        self._interval.start()

def clear_interval(interval_obj):
    interval_obj._interval.cancel()
