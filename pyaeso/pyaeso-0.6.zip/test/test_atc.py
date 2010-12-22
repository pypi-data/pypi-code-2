########################################################################
## Standard library imports
from datetime import datetime
from datetime import date
from datetime import timedelta
import unittest
import doctest
import sys
import os
import bz2
from cStringIO import StringIO


########################################################################
## AESO Modules
from aeso import UTC_TZ
from aeso import atc
import libtest


class TestAtcLimits(unittest.TestCase):
    def test_date_parsing(self):
        converstions = [
            # Standard time -> daylight saavings time transition
            (('2000-04-01', '24'), datetime(2000, 4, 2, 7)),
            (('2000-04-02', '1'), datetime(2000, 4, 2, 8)),
            (('2000-04-02', '2'), datetime(2000, 4, 2, 9)),
            (('2000-04-02', '4'), datetime(2000, 4, 2, 10)),
            (('2000-04-02', '5'), datetime(2000, 4, 2, 11)),

            # Daylight-savings time -> standard time transition
            (('2009-10-31', '23'), datetime(2009, 11, 1, 5)),
            (('2009-10-31', '24'), datetime(2009, 11, 1, 6)),
            (('2009-11-01', '1'), datetime(2009, 11, 1, 7)),
            (('2009-11-01', '2'), datetime(2009, 11, 1, 8)),
            (('2009-11-01', '25'), datetime(2009, 11, 1, 9)),
            (('2009-11-01', '3'), datetime(2009, 11, 1, 10)),
            (('2009-11-01', '4'), datetime(2009, 11, 1, 11)),
        ]

        for cells, expected in converstions:
            expected = UTC_TZ.localize(expected)
            actual = atc._normalize_atc_dtstr_to_utc(cells)
            self.assertEquals(actual, expected)

    def test_parse_atc_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'atc_report.csv.bz2')

        atc_points = []
        f = bz2.BZ2File(test_series_file)
        atc_points.extend(atc.parse_atc_file(f))
        f.close()


class TestAtcLimitRemote(unittest.TestCase):
    def test_atc_connection(self):
        start_date = date(1999, 12, 22)
        end_date = date.today() + timedelta(1)

        f = StringIO()
        atc.dump_atc(f, start_date, end_date)
        f.seek(0)
        points = list(atc.parse_atc_file(f))
        f.close()


loader = unittest.TestLoader()
remote_suites = [
    loader.loadTestsFromTestCase(TestAtcLimitRemote),
    doctest.DocTestSuite(atc),
]

local_suites = [
    loader.loadTestsFromTestCase(TestAtcLimits),
]


if __name__ == '__main__':
    sys.exit(libtest.main(sys.argv[1:], local_suites, remote_suites))
