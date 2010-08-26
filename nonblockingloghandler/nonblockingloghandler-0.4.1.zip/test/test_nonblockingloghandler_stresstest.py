#!/usr/bin/env python

# Test that under extreme conditions, the logging doesn't use up too many system resources.
# This test FAILED in versin 0.2 and 0.3.

import logging

import sys
sys.path = [".."] + sys.path

import nonblockingloghandler

def main():
    stdout_handler = logging.StreamHandler(sys.stdout)
    nh = nonblockingloghandler.NonblockingLogHandler(stdout_handler)
    logging.getLogger("").addHandler(nh)

    for i in xrange(10000):
        if i%100 == 0:
            print "CLIENT THREAD: Up to message # %s" % i
        logging.error("   LOGHANDLER THREAD: Up to message # %s", i)

    print "TEST PASSED" # Failure is seen with an exception.

main()
