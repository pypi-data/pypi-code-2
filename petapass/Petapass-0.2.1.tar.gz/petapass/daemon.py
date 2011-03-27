import threading

class Daemon(object):

    def __init__(self, duration):
        if not isinstance(duration, int) or duration < 1:
            raise ValueError(duration)

        self.duration = duration
        self._master = None
        self._resetter = None

    def set(self, x):
        if not x:
            self.forget()
        elif self._master != x:
            r = self._resetter
            if r is not None:
                r.cancel()

            self._resetter = threading.Timer(self.duration, self._reset_master)
            self._resetter.setDaemon(True)
            self._resetter.start()
            self._master = x

    def get(self):
        return self._master

    def forget(self):
        r = self._resetter
        if r is not None:
            r.cancel()
        self._master = None

    def _reset_master(self):
        self._master = None
        self._resetter = None
