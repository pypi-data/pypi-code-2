#!/usr/bin/python
"""\
@file   test_exc.py
@author Nat Goodspeed
@date   2011-01-04
@brief  Test exc.py functionality

Copyright (c) 2011, Nat Goodspeed
"""

from __future__ import with_statement   # for Python 2.5

import sys
import unittest
import exc

class FooError(Exception):
    pass

def raiser(exc):
    raise exc

class TestExc(unittest.TestCase):
    def setUp(self):
        pass

    def test_plain_raise(self):
        # Prove claim that no-args 'raise' can get confused
        try:                            # this is outer code
            try:
                raiser(FooError("foo"))
            except FooError, err:
                # This is cleanup code
                try:
                    x = int("7a")
                except ValueError:
                    # it's okay, we've handled it...
                    x = 7
                # except now we've reset the global exception info...
                raise
        except FooError, err:
            # This we do NOT expect, at least not in Python 2.x.
            self.assert_(False)
        except ValueError, err:
            self.assert_(True)
        else:
            # There better be an exception of SOME kind!
            self.assert_(False)

    def test_reraise(self):
        # reraise should handle this better
        try:                            # this is outer code
            try:
                raiser(FooError("foo"))
            except FooError, err:
                with exc.reraise():
                    # This is cleanup code
                    try:
                        x = int("7a")
                    except ValueError:
                        # it's okay, we've handled it...
                        x = 7
        except FooError, err:
            # This time we should get our original FooError
            self.assertEqual(str(err), "foo")
        except ValueError, err:
            self.assert_(False)
        else:
            self.assert_(False)

    def test_cleanup_exc(self):
        # reraise lets cleanup exception propagate out
        try:                            # this is outer code
            try:
                raiser(FooError("foo"))
            except FooError, err:
                with exc.reraise():
                    # This is cleanup code -- whoops, uncaught exception!
                    x = int("7a")
        except FooError, err:
            # reraise shouldn't discard cleanup exception
            self.assert_(False)
        except ValueError, err:
            self.assert_(True)
        else:
            self.assert_(False)

    def test_no_current_exc(self):
        # If there wasn't already a current exception, reraise doesn't
        # introduce one.
        try:                            # this is outer code
            with exc.reraise():
                pass
        except FooError, err:
            self.assert_(False)
        except ValueError, err:
            self.assert_(False)
        except TypeError, err:
            self.assert_(False)
        else:
            self.assert_(True)

if __name__ == "__main__":
    unittest.main()
