#!/usr/bin/python
"""\
@file   exc.py
@author Nat Goodspeed
@date   2011-01-04
@brief  Utilities for manipulating Python exceptions

Copyright (c) 2011, Nat Goodspeed
"""

import sys

class reraise(object):
    """
    Consider this cleanup pattern:

    try:
        some_code()
    except Exception:
        essential_cleanup()
        raise

    You want to perform the cleanup on exception, but nonetheless you want to
    propagate the original exception out to the caller, original traceback and
    all.

    Sadly, because of Python's global current exception, that works only if
    essential_cleanup() does not itself handle any exceptions. For instance:

    try:
        x = some_dict[some_key]
    except KeyError:
        print "No key %r" % some_key

    This innocuous code is enough to foul up the no-args 'raise' statement in
    the 'except' clause that calls essential_cleanup().

    You can capture sys.exc_info() and re-raise specifically that exception:

    try:
        some_code()
    except Exception:
        type, value, tb = sys.exc_info()
        essential_cleanup()
        raise type, value, tb

    But now you've constructed the kind of reference loop against which
    http://docs.python.org/release/2.5.4/lib/module-sys.html#l2h-5141
    specifically warns, storing a traceback into a local variable.

    This is better:

    try:
        some_code()
    except Exception:
        type, value, tb = sys.exc_info()
        try:
            essential_cleanup()
            raise type, value, tb
        finally:
            del tb

    but you must admit it's pretty verbose -- it almost completely obscures
    the nature of the cleanup. Plus it's a PITB to remember.

    reraise encapsulates that last pattern, permitting you to write:

    try:
        some_code()
    except Exception:
        with reraise():
            essential_cleanup()

    This is as terse as the original, guarantees to preserve the original
    exception and avoids reference loops.

    As in the original construct, if essential_cleanup() itself raises an
    exception, that exception propagates out to the caller instead of the one
    raised by some_code().
    """
    def __enter__(self):
        self.type, self.value, self.tb = sys.exc_info()
        return self

    def __exit__(self, type, value, tb):
        try:
            if type or value or tb:
                # If code in the 'with' block raised an exception, just let that
                # exception propagate.
                return False

            if not (self.type or self.value or self.tb):
                # If there wasn't a current exception at __enter__() time,
                # don't raise one now.
                return False

            # This 'with' statement was entered with a current exception, and
            # code in the block did not override it with a newer exception.
            # Re-raise the one we captured in __enter__().
            raise self.type, self.value, self.tb

        finally:
            # No matter how we leave this method, always delete the traceback
            # member.
            del self.tb
