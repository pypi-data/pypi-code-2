# -*- coding: utf-8 -*-

import sys
from nose.tools import *
from StringIO import StringIO

# functions for test
import ikazuchi.utils


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
