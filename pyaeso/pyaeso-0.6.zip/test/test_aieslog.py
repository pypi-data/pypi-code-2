import unittest
import warnings

from os.path import dirname
from os.path import join

import bz2
import sys

import doctest

# Custom libraries
import libtest
from aeso import AB_TZ


class WarningMessage(object):
    """Copied from 2.6 sourcecode so that this works in Python >= 2.4"""

    _WARNING_DETAILS = ("message", "category", "filename", "lineno", "file",
                        "line")

    def __init__(self, message, category, filename, lineno, file=None,
                    line=None):
        local_values = locals()
        for attr in self._WARNING_DETAILS:
            setattr(self, attr, local_values[attr])

        self._category_name = category.__name__

    def __str__(self):
        return ("{message : %r, category : %r, filename : %r, lineno : %s, "
                    "line : %r}" % (self.message, self._category_name,
                                    self.filename, self.lineno, self.line))

_warning_log = []
_saved_showarning = warnings.showwarning
_saved_filters = warnings.filters
def _showwarning(*args, **kwargs):
    global _warning_log
    _warning_log.append(WarningMessage(*args, **kwargs))
warnings.showwarning = _showwarning

warnings.simplefilter("always")

# Trigger a warning.
from aeso import aieslog

# Verify some things
assert len(_warning_log) == 1
assert issubclass(_warning_log[-1].category, DeprecationWarning)
assert "deprecated" in str(_warning_log[-1].message)

warnings.showwarning = _saved_showarning
warnings.filters = _saved_filters



class TestAiesLog(unittest.TestCase):
    def test_parse_asset_list_file(self):
        test_file = join(dirname(__file__), 'res', 'RealTimeShiftReportServlet.csv.bz2')
        f = bz2.BZ2File(test_file)

        num_rows = 0
        for dt, entry in aieslog.parse_aieslog_file(f):
                num_rows += 1
                #print dt.astimezone(AB_TZ), entry
        f.close()
        self.assertEquals(num_rows, 29)


class TestAiesLogWebservice(unittest.TestCase):
    def test_parse_asset_list_file(self):
        f = aieslog.urlopen()
        rows = list(aieslog.parse_aieslog_file(f))
        f.close()
        self.assertTrue(len(rows) > 5)


loader = unittest.TestLoader()
remote_suites = [
    loader.loadTestsFromTestCase(TestAiesLogWebservice),
    doctest.DocTestSuite(aieslog),
]

local_suites = [
    loader.loadTestsFromTestCase(TestAiesLog),
]


if __name__ == '__main__':
    sys.exit(libtest.main(sys.argv[1:], local_suites, remote_suites))
