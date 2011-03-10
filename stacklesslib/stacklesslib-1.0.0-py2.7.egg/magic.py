# slmagic.py
# This module switches a threaded program to a tasklet based one.

import imp
import os
import sys
import time

import stackless
from stacklesslib import main


def monkeypatch():
    from stacklesslib.replacements import thread, threading, popen
    
    # Inject slthreading as threading.
    sys.modules["threading"] = threading
    sys.modules["thread"] = thread
    
    # Fudge time.sleep.
    time.sleep = main.sleep
    
    # Fudge popen4.
    os.popen4 = popen.popen4

    monkeypatch_select()

    # Select the best socket module to inject as a replacement.
    monkeypatch_socket()


def monkeypatch_select():
    """ Selectively choose to monkey-patch the 'select' module. """
    from stacklesslib.replacements import select

    sys.modules["select"] = select
    

def monkeypatch_socket(will_be_pumped=True):
    """
    Selectively choose to monkey-patch the 'socket' module.

    If 'will_be_pumped' is set to False, the patched socket module will take
    care of polling networking events in a scheduled tasklet.  Otherwise, the
    controlling application is responsible for pumping these events.
    """
    # Disable preferred socket solution of stacklessio for now.
    stacklessio = False
    if False:
        try:
            import stacklessio
        except:
            stacklessio = False

    # Fallback on the generic 'stacklesssocket' module.
    from stacklesslib.replacements import socket
    socket._sleep_func = main.sleep
    socket._schedule_func = lambda: main.sleep(0)
    if will_be_pumped:
        socket._manage_sockets_func = lambda: None
    socket.install()
        

if __name__ == "__main__":
    # Shift command line arguments.
    me = sys.argv.pop(0)

    # Remove our directory from the path, in case we were invoked as a script.
    p = os.path.dirname(me)
    if not p:
        p = "."
    try:
        sys.path.remove(os.path.abspath(p))
    except ValueError:
        pass # Ok, we were probably run as a -m flag.

    # Rename ourselves, so we don't get clobbered.
    __name__ = "__slmain__"
    sys.modules["__slmain__"] = sys.modules["__main__"]
    del sys.modules["__main__"]

    # Run next argument as main:
    if sys.argv:
        p = os.path.dirname(sys.argv[0])
        if not p:
            p = "."
        sys.path.insert(0, os.path.abspath(p))

    # The actual __main__ will be run here in a tasklet
    def Main():
        try:
            if sys.argv:
                imp.load_source("__main__", os.path.abspath(sys.argv[0]))
        except Exception:
            main.mainloop.exception = sys.exc_info()
            raise
        finally:
            main.mainloop.running = False

    monkeypatch()
    main.set_scheduling_mode(main.SCHEDULING_ROUNDROBIN)
    stackless.tasklet(Main)()
    main.mainloop.run()
