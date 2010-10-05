import unittest
from xmltopy.xmlserializer import parse_date, parse_datetime
from lxml import etree
from datetime import datetime, date, timedelta

try: import pytz
except ImportError: print 'WARNING! pytz not installed. datetime related tests will fail.'

class TestDateHandling(unittest.TestCase):
    def test_parse_datetime(self):
        self.assertEqual(parse_datetime('2001-01-01T12:00:00'),
                         datetime(2001, 01, 01, 12, 00, 00, tzinfo=pytz.utc))
        
        self.assertEqual(parse_datetime('1999-12-31T23:59:59'),
                         datetime(1999, 12, 31, 23, 59, 59, tzinfo=pytz.utc))        
        
        self.assertEqual(parse_datetime('1999-12-31T23:59:59Z'),
                         datetime(1999, 12, 31, 23, 59, 59, tzinfo=pytz.utc))     
    
        self.assertEqual(parse_datetime('1999-12-31T23:59:59UTC'),
                         datetime(1999, 12, 31, 23, 59, 59, tzinfo=pytz.utc))     
        
        self.assertEqual(parse_datetime('1999-12-31T23:59:59GMT'),
                         datetime(1999, 12, 31, 23, 59, 59, tzinfo=pytz.utc))
        
        assert parse_datetime('1999-12-31T23:59:59-05:00').utcoffset() == timedelta(hours = -5)
        assert parse_datetime('1999-12-31T23:59:59+05:30').utcoffset() == timedelta(hours=5, minutes=30)
        
    def test_parse_date(self):
        assert parse_date('1999-12-31') == date(1999, 12, 31)
        assert parse_date('1999-12-31-05:00') == date(1999, 12, 31)
        assert parse_date('1999-12-31+05:30') == date(1999, 12, 31)