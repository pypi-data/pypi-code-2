import threading

from watchdog.utils import has_attribute, DaemonThread

def monkey_patch():
    """Watchdog has a bug in Python2.5, reference to
    
    https://github.com/gorakhargosh/watchdog/issues#issue/34
    
    Here we patch the bug
    
    """
    def __init__(self):
        threading.Thread.__init__(self)
        if has_attribute(self, 'daemon'):
            self.daemon = True
        else:
            self.setDaemon(True)
        self._stopped_event = threading.Event()
    
        # this line is wrong originally
        if not has_attribute(self._stopped_event, 'is_set'):
            self._stopped_event.is_set = self._stopped_event.isSet
            
    DaemonThread.__init__ = __init__