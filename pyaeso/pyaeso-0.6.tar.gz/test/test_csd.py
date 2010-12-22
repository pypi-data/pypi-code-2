# Built-in modules
import unittest

from datetime import datetime
from datetime import timedelta

from os.path import dirname
from os.path import join

from StringIO import StringIO

from time import strptime
import doctest
import sys

import bz2

# 3rd party libraries
import pytz
from pytz import utc as UTC

# Custom libraries
import libtest
from aeso import AB_TZ
from aeso import csd

class TestCsd(unittest.TestCase):
    CSD_DT_FORMAT = '%b %d, %Y %H:%M'

    def test_parse_asset_list_file(self):
        test_file = join(dirname(__file__), 'res', 'CSDReportServlet.csv.bz2')
        f = bz2.BZ2File(test_file)

        num_rows = 0
        for cells in csd.parse_csd_file(f):
            num_rows += 1
            self.assertTrue(len(cells) in (3, 5))
            #~ print entries[0].astimezone(AB_TZ), entries[1:]
        self.assertEquals(num_rows, 115)


    def _test_dst_begin(self):
        # Dst begins 2010-03-14
        template_fn = join(dirname(__file__), 'res', 'csdreport_dst.csv.bz2')

        f = bz2.BZ2File(template_fn)
        template_text = f.read()
        f.close()

        cursor = datetime(2010, 3, 14, 0)
        max_dt = datetime(2010, 3, 14, 4)

        while cursor < max_dt:
            report_dt_str = cursor.strftime(type(self).CSD_DT_FORMAT)
            text = template_text % (report_dt_str,)
            #text = template_text.format(datetime = report_dt_str)
            f = StringIO(text)
            num_rows = 0
            for cells in csd.parse_csd_file(f):
                num_rows += 1
            f.close()

            cursor += timedelta(0, 60)


    def test_timedeltas(self):
        td = AB_TZ.localize(datetime(2010, 11, 7, 0, 0), is_dst = False) - AB_TZ.localize(datetime(2010, 11, 6, 23, 59), is_dst = None)
        self.assertEqual(td, timedelta(0, 60))

        td = AB_TZ.localize(datetime(2010, 11, 7, 0, 59), is_dst = False) - AB_TZ.localize(datetime(2010, 11, 7, 0, 58), is_dst = None)
        self.assertEqual(td, timedelta(0, 60))

        td = AB_TZ.localize(datetime(2010, 11, 6, 1, 0), is_dst = None) - AB_TZ.localize(datetime(2010, 11, 6, 0, 59), is_dst = None)
        self.assertEqual(td, timedelta(0, 60))

        td = AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = True) - AB_TZ.localize(datetime(2010, 11, 7, 0, 59), is_dst = None)
        self.assertEqual(td, timedelta(0, 60))

        td = AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = False) - AB_TZ.localize(datetime(2010, 11, 7, 1, 59), is_dst = True)
        self.assertEqual(td, timedelta(0, 60))

        # Arithmetic falls over here.  Timdelta should be 60 seconds but it isn't!
        ab_a = AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = False)
        ab_b = AB_TZ.localize(datetime(2010, 11, 7, 1, 59), is_dst = True)
        utc_a = UTC.normalize(ab_a.astimezone(UTC))
        utc_b = UTC.normalize(ab_b.astimezone(UTC))
        self.assertEqual(ab_a - ab_b, utc_a - utc_b)
        self.assertEqual(utc_a - ab_b, utc_a - utc_b)
        self.assertEqual(ab_a - utc_b, utc_a - utc_b)



    def _open_rendered_template(self, report_dt):
        template_fn = join(dirname(__file__), 'res', 'csdreport_dst.csv.bz2')

        f = bz2.BZ2File(template_fn)
        template_text = f.read()
        f.close()

        report_dt_str = report_dt.strftime(type(self).CSD_DT_FORMAT)
        text = template_text % (report_dt_str,)
        f = StringIO(text)
        return f


    def assertCsdParseDtEquals(self, report_dt, ref_dt, expected_dt):
        f = self._open_rendered_template(report_dt)
        num_rows = 0
        for cells in csd.parse_csd_file(f, ref_dt):
            self.assertEqual(cells[0], expected_dt)
            num_rows += 1
        f.close()


    def assertCsdParseRaises(self, exception_class, report_dt, ref_dt):
        f = self._open_rendered_template(report_dt)
        it = csd.parse_csd_file(f, ref_dt)
        self.assertRaises(exception_class, it.next)
        f.close()


    def test_dst_end(self):
        # Dst ends 2010-11-07

        rpt_dt = AB_TZ.localize(datetime(2010, 11, 7, 0, 59), is_dst = None)
        self.assertCsdParseDtEquals(rpt_dt, None, UTC.normalize(rpt_dt.astimezone(UTC)))

        rpt_dt = datetime(2010, 11, 7, 1, 0)
        ref_dt = AB_TZ.localize(datetime(2010, 11, 7, 0, 59))
        expected_dt = UTC.normalize(AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = True).astimezone(UTC))
        self.assertCsdParseDtEquals(rpt_dt, ref_dt, expected_dt)

        rpt_dt = datetime(2010, 11, 7, 1, 30)
        ref_dt = AB_TZ.localize(datetime(2010, 11, 7, 0, 59))
        expected_dt = UTC.normalize(AB_TZ.localize(rpt_dt, is_dst = True).astimezone(UTC))
        self.assertCsdParseDtEquals(rpt_dt, ref_dt, expected_dt)

        rpt_dt = datetime(2010, 11, 7, 1, 30)
        ref_dt = AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = False)
        expected_dt = UTC.normalize(AB_TZ.localize(rpt_dt, is_dst = False).astimezone(UTC))
        self.assertCsdParseDtEquals(rpt_dt, ref_dt, expected_dt)

        # Without a reference dt, there is not way to guess at whether
        # DST is active.  Should raise AmbiguousTimeError
        self.assertCsdParseRaises(pytz.AmbiguousTimeError, datetime(2010, 11, 7, 1, 30), None)


    def test_dt(self):
        cell = 'Last Update : Mar 14, 2010 02:00'

        struct_time = strptime(cell, "Last Update : %b %d, %Y %H:%M")
        dt = datetime(*struct_time[0:6])
        self.assertEquals(dt.hour, 2)
        self.assertRaises(pytz.NonExistentTimeError, AB_TZ.localize, dt, is_dst = None)


class TestCsdWebservice(unittest.TestCase):
    def test_csd_webservice(self):
        f = csd.urlopen()
        rows = list(csd.parse_csd_file(f))
        f.close()
        self.assertTrue(len(rows) > 50)


loader = unittest.TestLoader()
remote_suites = [
    loader.loadTestsFromTestCase(TestCsdWebservice),
    doctest.DocTestSuite(csd),
]

local_suites = [
    loader.loadTestsFromTestCase(TestCsd),
]


if __name__ == '__main__':
    sys.exit(libtest.main(sys.argv[1:], local_suites, remote_suites))
