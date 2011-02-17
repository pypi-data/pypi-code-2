# -*- coding: utf-8 -*-

import sys
from nose.tools import *
from StringIO import StringIO

# functions for test
import ikazuchi.utils


def test_get_encoding():
    class Parser(object):
        class Values(object):
            encoding = None
        values = Values()
    parser = Parser()
    ikazuchi.utils.get_encoding(None, None, "utf-8", parser)
    assert_equal(["utf-8", "utf-8"], parser.values.encoding)
    ikazuchi.utils.get_encoding(None, None, "utf-8, euc-jp", parser)
    assert_equal(["utf-8", "euc-jp"], parser.values.encoding)

def test_check_encoding():
    errs = ikazuchi.utils.check_encoding(["euc-jp", "utf-8"])
    assert_equals([], errs)
    errs = ikazuchi.utils.check_encoding(["unknown", "utf-8"])
    assert_equals(["unknown"], errs)
    errs = ikazuchi.utils.check_encoding(["utf-8", "unknown"])
    assert_equals(["unknown"], errs)
    errs = ikazuchi.utils.check_encoding(["unknown", "notexist"])
    assert_equals(["unknown", "notexist"], errs)

def test_python_version():
    data = [(2, 6, 4, 'final', 0), (2, 5, 1, 'final', 0)]
    sys.stdout = StringIO()
    for ver in data:
        sys.version_info = ver
        try:
            ikazuchi.utils.check_python_version()
            assert_equals("", sys.stdout.getvalue())
        except SystemExit:
            assert_equals(ikazuchi.utils._UNSUPPORTED_VERSION,
                            sys.stdout.getvalue().rstrip('\r\n'))
