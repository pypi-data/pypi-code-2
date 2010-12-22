########################################################################
## Standard library imports
from datetime import date
import unittest
import doctest
import sys

########################################################################
## Custom Imports
import libtest
import aeso._util
from aeso._util import DayBlockIt

class TestDayBlockIt(unittest.TestCase):
    def test_iteration(self):
        start_date = date(1995, 1, 1)
        end_date = date(1995, 1, 10)

        it = DayBlockIt(start_date, end_date, 10)
        self.assertEquals(it.next(), (start_date, end_date))
        self.assertRaises(StopIteration, it.next)

        it = DayBlockIt(start_date, end_date, 5)
        self.assertEquals(it.next(), (date(1995, 1, 1), date(1995, 1, 5)))
        self.assertEquals(it.next(), (date(1995, 1, 6), date(1995, 1, 10)))
        self.assertRaises(StopIteration, it.next)


    def test_negative(self):
        start_date = date(1995, 1, 10)
        end_date = date(1995, 1, 1)

        it = DayBlockIt(start_date, end_date, -10)
        self.assertEquals(it.next(), (start_date, end_date))

        it = DayBlockIt(start_date, end_date, -5)
        self.assertEquals(it.next(), (date(1995, 1, 10), date(1995, 1, 6)))
        self.assertEquals(it.next(), (date(1995, 1, 5), date(1995, 1, 1)))
        self.assertRaises(StopIteration, it.next)


loader = unittest.TestLoader()
remote_suites = []

local_suites = [
    loader.loadTestsFromTestCase(TestDayBlockIt),
    doctest.DocTestSuite(aeso._util),
]


if __name__ == '__main__':
    sys.exit(libtest.main(sys.argv[1:], local_suites, remote_suites))
