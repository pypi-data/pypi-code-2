# -*- coding: utf-8 -*-
import sys
if sys.version >= (2, 7):
    import unittest
else:
    try:
        import unittest2 as unittest
    except ImportError:
        raise Exception("You MUST install unittest2 to run these tests")
