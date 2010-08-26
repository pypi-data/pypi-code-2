#!/usr/bin/env python

# Test what happens if the client isn't careful about cleaning up the log handlers. Does it shut-down correctly?

# Cannot be included with other tests in the same Python interpreter.
# Note: There are three variants to this test.

import logging


import sys
sys.path = [".."] + sys.path

import nonblockingloghandler

def termination_test_with_close():
    # Passes
    logging.basicConfig()
    stdout_handler = logging.StreamHandler(sys.stdout)
    nh = nonblockingloghandler.NonblockingLogHandler(stdout_handler)
    logging.getLogger("").addHandler(nh)
    logging.error("Logging message")
    nh.close()

print "This test passes if it terminates."
import threading
thread = threading.Thread(target=termination_test_with_close)
thread.start()
