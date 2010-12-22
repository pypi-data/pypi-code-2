import unittest
import os.path
from StringIO import StringIO
from datetime import datetime
from datetime import date
import bz2

from shutil import copyfileobj
import sys

# 3rd Party Required Libraries
import pytz

# Custom Libraries
from pyaeso import ets


class TestDayBlockIt(unittest.TestCase):
    def test_iteration(self):
        start_date = date(1995, 1, 1)
        end_date = date(1995, 1, 10)

        it = ets.DayBlockIt(start_date, end_date, 10)
        self.assertEquals(it.next(), (start_date, end_date))
        self.assertRaises(StopIteration, it.next)

        it = ets.DayBlockIt(start_date, end_date, 5)
        self.assertEquals(it.next(), (date(1995, 1, 1), date(1995, 1, 5)))
        self.assertEquals(it.next(), (date(1995, 1, 6), date(1995, 1, 10)))
        self.assertRaises(StopIteration, it.next)


    def test_negative(self):
        start_date = date(1995, 1, 10)
        end_date = date(1995, 1, 1)

        it = ets.DayBlockIt(start_date, end_date, -10)
        self.assertEquals(it.next(), (start_date, end_date))

        it = ets.DayBlockIt(start_date, end_date, -5)
        self.assertEquals(it.next(), (date(1995, 1, 10), date(1995, 1, 6)))
        self.assertEquals(it.next(), (date(1995, 1, 5), date(1995, 1, 1)))
        self.assertRaises(StopIteration, it.next)


class TestPoolPrice(unittest.TestCase):
    def test_parse_pool_price_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'ets_testseries.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        points = list(ets.parse_pool_price_file(f))
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
            actual_dt = ets._normalize_pool_price_dtstr_to_utc(datetime_str)
            expected_dt = pytz.utc.localize(expected_utc_datetime)
            self.assertEquals(actual_dt, expected_dt)

        # Test handling of 24
        # '03/02/2005 24' -> 2009-03-03 0
        self.assertEquals(ets._normalize_pool_price_dtstr_to_utc('03/02/2005 24'), ets.ALBERTA_TZ.localize(datetime(2005, 3, 3, 0)).astimezone(pytz.utc))


class TestAssetList(unittest.TestCase):
    def test_parse_asset_list_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'asset_list.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        assets = list(ets.parse_asset_list_file(f))
        self.assertEquals(len(assets), 1862)
        for asset in assets:
            for char in '<>':
                # ETS embeds HTML anchors in the asset name.  Test to
                # make sure they have been properly stripped out.
                self.assertTrue(char not in asset.asset_name)
        f.close()


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
            expected = pytz.utc.localize(expected)
            actual = ets._normalize_atc_dtstr_to_utc(cells)
            self.assertEquals(actual, expected)

    def test_parse_atc_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'atc_report.csv.bz2')

        atc_points = []
        f = bz2.BZ2File(test_series_file)
        atc_points.extend(ets.parse_atc_file(f))
        f.close()






class TestLiveEtsConnection(unittest.TestCase):
    def test_asset_list_connection(self):
        '''ETS-Coupled Test.'''
        f = StringIO()
        ets.dump_asset_list(f)
        assets = list(ets.parse_asset_list_file(f))
        f.close()

    def test_pool_price_connection(self):
        '''ETS-Coupled Test.'''
        f = StringIO()
        ets.dump_pool_price(f)
        f.seek(0)
        points = list(ets.parse_pool_price_file(f))
        f.close()

    def test_atc_connection(self):
        start_date = date(1999, 12, 22)
        end_date = date.today()

        f = StringIO()
        ets.dump_atc(f, start_date, end_date)
        f.seek(0)
        points = list(ets.parse_atc_file(f))
        f.close()


if __name__ == '__main__':
    unittest.main()
