import unittest

from os.path import dirname
from os.path import join

import bz2
import sys

import doctest

# Custom libraries
import libtest
from aeso import AB_TZ
from aeso import eventlog

class TestEventLog(unittest.TestCase):
    def test_parse_asset_list_file(self):
        test_file = join(dirname(__file__), 'res', 'RealTimeShiftReportServlet.csv.bz2')
        f = bz2.BZ2File(test_file)

        num_rows = 0
        for dt, entry in eventlog.parse_eventlog_file(f):
                num_rows += 1
                #print dt.astimezone(AB_TZ), entry
        f.close()
        self.assertEquals(num_rows, 29)


class TestEventLogWebservice(unittest.TestCase):
    def test_parse_asset_list_file(self):
        f = eventlog.urlopen()
        rows = list(eventlog.parse_eventlog_file(f))
        f.close()
        self.assertTrue(len(rows) > 5)


loader = unittest.TestLoader()
remote_suites = [
    loader.loadTestsFromTestCase(TestEventLogWebservice),
    doctest.DocTestSuite(eventlog),
]

local_suites = [
    loader.loadTestsFromTestCase(TestEventLog),
]


if __name__ == '__main__':
    sys.exit(libtest.main(sys.argv[1:], local_suites, remote_suites))
