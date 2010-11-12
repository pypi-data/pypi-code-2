"""\
Data conversion functions for signal handling.

"""
__docformat__ = "reStructuredText"

import signal


def name2signal(string):
    """Converts a signal name to canonical form.

    Signal names are recognized without regard for case:

      >>> name2signal('sighup')
      'SIGHUP'
      >>> name2signal('SigHup')
      'SIGHUP'
      >>> name2signal('SIGHUP')
      'SIGHUP'

    The leading 'SIG' is not required::

      >>> name2signal('hup')
      'SIGHUP'
      >>> name2signal('HUP')
      'SIGHUP'

    Names that are not known cause an exception to be raised::

      >>> name2signal('woohoo')
      Traceback (most recent call last):
      ValueError: could not convert 'woohoo' to signal name

      >>> name2signal('sigwoohoo')
      Traceback (most recent call last):
      ValueError: could not convert 'sigwoohoo' to signal name

    Numeric values are converted to names as well::

      >>> name2signal(str(signal.SIGHUP))
      'SIGHUP'

    Numeric values that can't be matched to any signal known to Python
    are treated as errors::

      >>> name2signal('-234')
      Traceback (most recent call last):
      ValueError: unsupported signal on this platform: -234

      >>> name2signal(str(signal.NSIG))  #doctest: +ELLIPSIS
      Traceback (most recent call last):
      ValueError: unsupported signal on this platform: ...

    Non-signal attributes of the signal module are not mistakenly
    converted::

      >>> name2signal('_ign')
      Traceback (most recent call last):
      ValueError: could not convert '_ign' to signal name

      >>> name2signal('_DFL')
      Traceback (most recent call last):
      ValueError: could not convert '_DFL' to signal name

      >>> name2signal('sig_ign')
      Traceback (most recent call last):
      ValueError: could not convert 'sig_ign' to signal name

      >>> name2signal('SIG_DFL')
      Traceback (most recent call last):
      ValueError: could not convert 'SIG_DFL' to signal name

      >>> name2signal('getsignal')
      Traceback (most recent call last):
      ValueError: could not convert 'getsignal' to signal name

    """
    try:
        v = int(string)
    except ValueError:
        if "_" in string:
            raise ValueError("could not convert %r to signal name" % string)
        s = string.upper()
        if not s.startswith("SIG"):
            s = "SIG" + s
        v = getattr(signal, s, None)
        if isinstance(v, int):
            return s
        raise ValueError("could not convert %r to signal name" % string)
    if v >= signal.NSIG:
        raise ValueError("unsupported signal on this platform: %s" % string)
    for name in dir(signal):
        if "_" in name:
            continue
        if getattr(signal, name) == v:
            return name
    raise ValueError("unsupported signal on this platform: %s" % string)


class SignalHandlers(object):

    def __init__(self, section):
        self.handlers = section.mapping
        self.name = section.getSectionName()

        # Convert to an isolated signalnum->[handlers] mapping:
        self._handlers = {}
        self._oldhandlers = {}
        for name in self.handlers:
            signalnum = getattr(signal, name)
            self._handlers[signalnum] = self.handlers[name][:]

        self.install()

    def install(self):
        if not self.installed:
            for signum in self._handlers:
                old = signal.signal(signum, self._dispatch)
                self._oldhandlers[signum] = old

    def uninstall(self):
        while self._oldhandlers:
            signum, handler = self._oldhandlers.popitem()
            signal.signal(signum, handler)

    @property
    def installed(self):
        return self._oldhandlers

    def _dispatch(self, signum, frame):
        for f in self._handlers[signum]:
            f()

    # HACK: Thse are needed to keep zope.app.appsetup.product happy.

    def getSectionName(self):
        return self.name

    @property
    def mapping(self):
        return self
