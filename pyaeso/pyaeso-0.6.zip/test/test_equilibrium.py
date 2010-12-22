########################################################################
## Standard library imports
import unittest
from os.path import dirname
from os.path import join
import doctest
#from datetime import date
from datetime import datetime
#from datetime import timedelta
import sys
import libtest
from cStringIO import StringIO
import bz2

########################################################################
## AESO Modules
from aeso import AB_TZ
from aeso import UTC_TZ
from aeso import equilibrium


class TestEquilibrium(unittest.TestCase):
    def test_parse_pool_price_file(self):
        test_series_file = join(dirname(__file__), 'res', 'ets_testseries.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        points = list(equilibrium.parse_equilibrium_file(f))
        self.assertEquals(len(points), 6728)
        f.close()

    def test_datetime_normalization(self):
        # Test DST handling
        lut = {
            # DST active
            "10/26/1996 00" : datetime(1996, 10, 26, 6),
            "10/26/1996 01" : datetime(1996, 10, 26, 7),
            "10/26/1996 02" : datetime(1996, 10, 26, 8),
            "10/26/1996 03" : datetime(1996, 10, 26, 9),

            # DST ends this day
            "10/27/1996 00" : datetime(1996, 10, 27, 6),
            "10/27/1996 01" : datetime(1996, 10, 27, 7),
            "10/27/1996 02" : datetime(1996, 10, 27, 8),
            "10/27/1996 02*" : datetime(1996, 10, 27, 9),
            "10/27/1996 03" : datetime(1996, 10, 27, 10),

            # DST inactive
            "10/28/1996 00" : datetime(1996, 10, 28, 7),
            "10/28/1996 01" : datetime(1996, 10, 28, 8),
            "10/28/1996 02" : datetime(1996, 10, 28, 9),
            "10/28/1996 03" : datetime(1996, 10, 28, 10),
        }
        for datetime_str, expected_utc_datetime in lut.items():
            actual_dt = equilibrium._normalize_pool_price_dtstr_to_utc(datetime_str)
            expected_dt = UTC_TZ.localize(expected_utc_datetime)
            self.assertEquals(actual_dt, expected_dt)

        # Test handling of 24
        # '03/02/2005 24' -> 2009-03-03 0
        self.assertEquals(equilibrium._normalize_pool_price_dtstr_to_utc('03/02/2005 24'), AB_TZ.localize(datetime(2005, 3, 3, 0)).astimezone(UTC_TZ))


class TestEquilibriumRemote(unittest.TestCase):
    def test_pool_price_connection(self):
        '''ETS-Coupled Test.'''
        f = StringIO()
        equilibrium.dump_equilibrium(f)
        f.seek(0)
        points = list(equilibrium.parse_equilibrium_file(f))
        f.close()


loader = unittest.TestLoader()
remote_suites = [
    loader.loadTestsFromTestCase(TestEquilibriumRemote),
    doctest.DocTestSuite(equilibrium),
]

local_suites = [
    loader.loadTestsFromTestCase(TestEquilibrium),
]


if __name__ == '__main__':
    sys.exit(libtest.main(sys.argv[1:], local_suites, remote_suites))
